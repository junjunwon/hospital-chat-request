/**
 * 병원 간호사 도우미 챗봇 - JavaScript
 * 클라이언트 사이드 로직 및 UI 상호작용
 */

// 전역 변수
let messageCount = 0;
let isTyping = false;
let sessionId = null;
let currentNavigationLevel = 0;

// DOM 요소 참조
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const charCount = document.getElementById('charCount');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorModal = document.getElementById('errorModal');
const helpModal = document.getElementById('helpModal');

// 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
});

/**
 * 챗봇 초기화
 */
function initializeChatbot() {
    // Enter 키로 메시지 전송
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 문자 수 카운터
    messageInput.addEventListener('input', updateCharCount);
    
    // 버튼 상태 업데이트
    messageInput.addEventListener('input', updateSendButton);
    
    // 초기 상태 설정
    updateCharCount();
    updateSendButton();
    
    console.log('🤖 챗봇 클라이언트가 초기화되었습니다.');
}

/**
 * 메시지 전송
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isTyping) {
        return;
    }
    
    // 사용자 메시지 표시
    addMessage(message, 'user');
    
    // 입력 필드 초기화
    messageInput.value = '';
    updateCharCount();
    updateSendButton();
    
    // 타이핑 인디케이터 표시
    showTypingIndicator();
    
    try {
        // 서버에 요청 전송 (세션 ID 포함)
        const requestBody = { 
            message: message,
            session_id: sessionId 
        };
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // 세션 ID 저장
        if (data.session_id) {
            sessionId = data.session_id;
        }
        
        // 타이핑 인디케이터 제거
        hideTypingIndicator();
        
        // 봇 응답 표시
        addMessage(data.message, 'bot', data.category, data.priority);
        
        // 네비게이션 버튼 상태 업데이트
        updateNavigationButtons(data.category);
        
    } catch (error) {
        console.error('메시지 전송 오류:', error);
        hideTypingIndicator();
        
        let errorMessage = '죄송합니다. 일시적인 오류가 발생했습니다.';
        let errorTitle = '오류';
        
        // 에러 타입별 세분화된 메시지
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            errorMessage = '서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.';
            errorTitle = '연결 오류';
        } else if (error.message.includes('HTTP 500')) {
            errorMessage = '서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
            errorTitle = '서버 오류';
        } else if (error.message.includes('HTTP 400')) {
            errorMessage = '요청이 올바르지 않습니다. 메시지를 다시 입력해주세요.';
            errorTitle = '요청 오류';
        }
        
        // 에러 메시지 표시
        addMessage(errorMessage, 'bot', '오류');
        
        showErrorModal(errorTitle, error.message);
    }
}

/**
 * 빠른 메시지 전송
 */
function sendQuickMessage(message) {
    messageInput.value = message;
    sendMessage();
}

/**
 * 메시지 추가
 */
function addMessage(text, sender, category = '', priority = 'NORMAL') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // 메시지 ID 생성
    const messageId = `msg-${++messageCount}`;
    messageDiv.id = messageId;
    
    // 응급 메시지 스타일 적용
    const isEmergency = priority === 'HIGH' || category === '응급상황';
    
    const currentTime = getCurrentTime();
    const avatar = sender === 'user' ? '👩‍⚕️' : '🤖';
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text ${isEmergency ? 'emergency-message' : ''}">
                    ${formatMessage(text)}
                </div>
                <div class="message-time">
                    ${currentTime}
                    ${category && sender === 'bot' ? ` • ${category}` : ''}
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text ${isEmergency ? 'emergency-message' : ''}">
                    ${formatMessage(text)}
                </div>
                <div class="message-time">
                    ${currentTime}
                    ${category && sender === 'bot' ? ` • ${category}` : ''}
                </div>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // 응급 메시지 시 특별 효과
    if (isEmergency) {
        playEmergencyAlert();
    }
    
    return messageDiv;
}

/**
 * 메시지 포맷팅
 */
function formatMessage(text) {
    // 줄바꿈 처리
    text = text.replace(/\n/g, '<br>');
    
    // URL 링크 처리
    text = text.replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank" rel="noopener">$1</a>'
    );
    
    // 전화번호 강조
    text = text.replace(
        /(\d{3,4}-\d{4}|\d{4})/g,
        '<strong>$1</strong>'
    );
    
    return text;
}

/**
 * 타이핑 인디케이터 표시
 */
function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    sendButton.disabled = true;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-message';
    typingDiv.id = 'typing-indicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

/**
 * 타이핑 인디케이터 숨기기
 */
function hideTypingIndicator() {
    isTyping = false;
    sendButton.disabled = false;
    
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

/**
 * 문자 수 카운터 업데이트
 */
function updateCharCount() {
    const currentLength = messageInput.value.length;
    charCount.textContent = currentLength;
    
    // 문자 수에 따른 색상 변경
    if (currentLength > 180) {
        charCount.style.color = '#ff4757';
    } else if (currentLength > 150) {
        charCount.style.color = '#ffa502';
    } else {
        charCount.style.color = '#666';
    }
}

/**
 * 전송 버튼 상태 업데이트
 */
function updateSendButton() {
    const hasText = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasText || isTyping;
    
    if (hasText && !isTyping) {
        sendButton.classList.add('active');
    } else {
        sendButton.classList.remove('active');
    }
}

/**
 * 채팅 영역을 맨 아래로 스크롤
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * 현재 시간 반환
 */
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 도움말 요청
 */
async function getHelp() {
    try {
        const response = await fetch('/help', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('도움말을 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        showHelpModal(data.message);
        
    } catch (error) {
        console.error('도움말 요청 오류:', error);
        showHelpModal(); // 기본 도움말 표시
    }
}

/**
 * 에러 모달 표시
 */
function showErrorModal(title, message) {
    const errorModal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');
    
    if (title) {
        errorModal.querySelector('.modal-header h3').textContent = `⚠️ ${title}`;
    }
    
    errorMessage.textContent = message || '알 수 없는 오류가 발생했습니다.';
    errorModal.style.display = 'flex';
    
    // 5초 후 자동 닫기
    setTimeout(() => {
        closeModal();
    }, 5000);
}

/**
 * 도움말 모달 표시
 */
function showHelpModal(content) {
    const helpModal = document.getElementById('helpModal');
    
    if (content) {
        // 서버에서 받은 도움말 내용으로 업데이트
        const helpContent = helpModal.querySelector('.help-content');
        helpContent.innerHTML = content.replace(/\n/g, '<br>');
    }
    
    helpModal.style.display = 'flex';
}

/**
 * 모달 닫기
 */
function closeModal() {
    errorModal.style.display = 'none';
}

/**
 * 도움말 모달 닫기
 */
function closeHelpModal() {
    helpModal.style.display = 'none';
}

/**
 * 응급상황 알림 효과
 */
function playEmergencyAlert() {
    // 시각적 효과
    document.body.style.animation = 'shake 0.5s ease-in-out';
    
    setTimeout(() => {
        document.body.style.animation = '';
    }, 500);
    
    // 브라우저 알림 (사용자 권한 필요)
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('🚨 응급상황 알림', {
            body: '응급상황이 감지되었습니다.',
            icon: '/favicon.ico'
        });
    }
}

/**
 * 브라우저 알림 권한 요청
 */
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            console.log('알림 권한:', permission);
        });
    }
}

/**
 * 키보드 단축키 처리
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter: 메시지 전송
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        sendMessage();
    }
    
    // ESC: 모달 닫기
    if (e.key === 'Escape') {
        closeModal();
        closeHelpModal();
    }
    
    // F1: 도움말
    if (e.key === 'F1') {
        e.preventDefault();
        getHelp();
    }
});

/**
 * 모바일 화면 크기 조정
 */
function adjustForMobile() {
    const isMobile = window.innerWidth <= 480;
    
    if (isMobile) {
        // 모바일에서는 viewport 높이 조정
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
}

// 화면 크기 변경 시 조정
window.addEventListener('resize', adjustForMobile);
window.addEventListener('orientationchange', adjustForMobile);

/**
 * 페이지 가시성 변경 처리
 */
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // 페이지가 다시 보일 때 입력 필드에 포커스
        if (!isTyping) {
            messageInput.focus();
        }
    }
});

/**
 * 접근성 향상을 위한 ARIA 속성 설정
 */
function setupAccessibility() {
    messageInput.setAttribute('aria-label', '메시지 입력');
    sendButton.setAttribute('aria-label', '메시지 전송');
    chatMessages.setAttribute('aria-label', '채팅 메시지 목록');
    chatMessages.setAttribute('aria-live', 'polite');
}

/**
 * 초기 설정
 */
document.addEventListener('DOMContentLoaded', function() {
    setupAccessibility();
    adjustForMobile();
    requestNotificationPermission();
    setupSearchInput();
    
    // 입력 필드에 포커스
    setTimeout(() => {
        messageInput.focus();
    }, 100);
});

// CSS 애니메이션 정의 (동적 추가)
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .active {
        transform: scale(1.05);
    }
`;
document.head.appendChild(style);

/**
 * 에러 로깅 및 모니터링
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript 오류:', e.error);
    
    // 사용자에게 친화적인 오류 메시지 표시
    showErrorModal(
        '예상치 못한 오류',
        '일시적인 문제가 발생했습니다. 페이지를 새로고침해주세요.'
    );
});

/**
 * 성능 모니터링
 */
if ('performance' in window) {
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`페이지 로드 시간: ${loadTime}ms`);
    });
}

/**
 * 네비게이션 버튼 상태 업데이트
 */
function updateNavigationButtons(category) {
    const mainButtons = document.getElementById('mainButtons');
    const navigationButtons = document.getElementById('navigationButtons');
    
    // 메인 메뉴 관련 카테고리인지 확인
    const navigationCategories = [
        '메인메뉴', '세부항목', '항목목록', '상세', '검색결과',
        '수리_세부항목', '물품_세부항목', '멸균품거즈_세부항목', '격리실_세부항목'
    ];
    
    if (navigationCategories.some(navCat => category && category.includes(navCat))) {
        // 네비게이션이 필요한 상태
        mainButtons.style.display = 'none';
        navigationButtons.style.display = 'flex';
        currentNavigationLevel = 1;
    } else if (category === '인사' || category === '기본') {
        // 메인 버튼 표시
        mainButtons.style.display = 'flex';
        navigationButtons.style.display = 'none';
        currentNavigationLevel = 0;
    }
}

/**
 * 검색 입력 영역 표시
 */
function showSearchInput() {
    const searchContainer = document.getElementById('searchContainer');
    const navigationButtons = document.getElementById('navigationButtons');
    const searchInput = document.getElementById('searchInput');
    
    searchContainer.style.display = 'flex';
    navigationButtons.style.display = 'none';
    searchInput.focus();
}

/**
 * 검색 입력 영역 숨기기
 */
function hideSearchInput() {
    const searchContainer = document.getElementById('searchContainer');
    const navigationButtons = document.getElementById('navigationButtons');
    const searchInput = document.getElementById('searchInput');
    
    searchContainer.style.display = 'none';
    navigationButtons.style.display = 'flex';
    searchInput.value = '';
}

/**
 * 검색 수행
 */
function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchText = searchInput.value.trim();
    
    if (searchText.length < 2) {
        alert('2글자 이상 입력해주세요.');
        return;
    }
    
    // 검색어로 메시지 전송
    sendQuickMessage(searchText);
    hideSearchInput();
}

/**
 * 메인 메뉴로 돌아가기
 */
function goToMainMenu() {
    sendQuickMessage('메인');
}

/**
 * 뒤로 가기
 */
function goBack() {
    sendQuickMessage('뒤로');
}

/**
 * 검색 입력 Enter 키 처리
 */
function setupSearchInput() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
            if (e.key === 'Escape') {
                hideSearchInput();
            }
        });
    }
}

/**
 * 동적 버튼 생성 (서버 응답에 따라)
 */
function createDynamicButtons(responseText) {
    // 응답에서 선택 가능한 옵션들을 추출하여 버튼 생성
    const quickButtons = document.getElementById('quickButtons');
    
    // 기존 동적 버튼 제거
    const existingDynamic = quickButtons.querySelector('.dynamic-buttons');
    if (existingDynamic) {
        existingDynamic.remove();
    }
    
    // 응답에서 "•" 로 시작하는 옵션들 찾기
    const options = responseText.match(/• ([^:]+)/g);
    
    if (options && options.length > 0) {
        const dynamicButtonGroup = document.createElement('div');
        dynamicButtonGroup.className = 'button-group dynamic-buttons';
        
        options.slice(0, 4).forEach(option => {
            const cleanOption = option.replace('• ', '').trim();
            const button = document.createElement('button');
            button.className = 'quick-btn dynamic-btn';
            button.textContent = cleanOption;
            button.onclick = () => sendQuickMessage(cleanOption);
            dynamicButtonGroup.appendChild(button);
        });
        
        quickButtons.appendChild(dynamicButtonGroup);
    }
}

/**
 * 메시지 추가 (오버라이드)
 */
function addMessage(text, sender, category = '', priority = 'NORMAL') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // 메시지 ID 생성
    const messageId = `msg-${++messageCount}`;
    messageDiv.id = messageId;
    
    // 응급 메시지 스타일 적용
    const isEmergency = priority === 'HIGH' || category === '응급상황';
    
    const currentTime = getCurrentTime();
    const avatar = sender === 'user' ? '👩‍⚕️' : '🤖';
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text ${isEmergency ? 'emergency-message' : ''}">
                    ${formatMessage(text)}
                </div>
                <div class="message-time">
                    ${currentTime}
                    ${category && sender === 'bot' ? ` • ${category}` : ''}
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text ${isEmergency ? 'emergency-message' : ''}">
                    ${formatMessage(text)}
                </div>
                <div class="message-time">
                    ${currentTime}
                    ${category && sender === 'bot' ? ` • ${category}` : ''}
                </div>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // 응급 메시지 시 특별 효과
    if (isEmergency) {
        playEmergencyAlert();
    }
    
    // 봇 메시지인 경우 동적 버튼 생성 시도
    if (sender === 'bot') {
        createDynamicButtons(text);
    }
    
    return messageDiv;
}

// 전역 함수로 export (HTML에서 사용)
window.sendMessage = sendMessage;
window.sendQuickMessage = sendQuickMessage;
window.getHelp = getHelp;
window.closeModal = closeModal;
window.closeHelpModal = closeHelpModal;
window.getCurrentTime = getCurrentTime;
window.updateCharCount = updateCharCount;
window.showSearchInput = showSearchInput;
window.hideSearchInput = hideSearchInput;
window.performSearch = performSearch;
window.goToMainMenu = goToMainMenu;
window.goBack = goBack;
