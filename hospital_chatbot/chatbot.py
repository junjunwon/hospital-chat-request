# -*- coding: utf-8 -*-
"""
차치업무 도우미 챗봇 - 로직 모듈
키워드 매칭 기반의 간단한 챗봇 구현
"""

import random
from datetime import datetime
from excel_data import (
    HIERARCHICAL_WORK_DATA, WORK_CATEGORIES, GREETING_RESPONSES, 
    DEFAULT_RESPONSES, FAQ_DATA, TIME_GREETINGS, EMERGENCY_KEYWORDS, 
    DEPARTMENT_CONTACTS
)

class SimpleHospitalChatbot:
    """차치업무 도우미 챗봇 클래스"""
    
    def __init__(self):
        """챗봇 초기화"""
        self.conversation_history = []
        self.user_name = None
        self.current_navigation = {
            "level": 0,  # 0: 메인 카테고리 선택, 1: 세부항목 선택, 2: 세부항목2 선택
            "main_category": None,      # 선택된 메인 카테고리 (예: "수리")
            "subcategory_key": None,    # 선택된 세부항목 키 (예: "의료기기")
            "sub_item_key": None        # 선택된 세부항목2 키
        }
        print("🏥 차치업무 도우미 챗봇이 시작되었습니다!")
    
    def process_message(self, user_input):
        """
        사용자 입력을 처리하고 응답 생성
        Args:
            user_input (str): 사용자가 입력한 메시지
        Returns:
            dict: 응답 정보가 담긴 딕셔너리
        """
        if not user_input or not user_input.strip():
            return self._format_response("메시지를 입력해주세요.", "오류")
        
        user_input = user_input.lower().strip()
        
        # 대화 기록에 추가
        self.conversation_history.append({
            "user": user_input,
            "timestamp": self._get_current_time()
        })
        
        # 응급상황 우선 처리
        emergency_response = self._check_emergency(user_input)
        if emergency_response:
            return emergency_response
        
        # 1. 인사말 처리
        if self._is_greeting(user_input):
            response = self._get_greeting_response()
            return self._format_response(response, "인사")
        
        # 2. 사용자 이름 설정
        name_response = self._check_name_setting(user_input)
        if name_response:
            return name_response
        
        # 3. FAQ 검색
        faq_response = self._search_faq(user_input)
        if faq_response:
            return self._format_response(faq_response, "FAQ")
        
        # 4. 부서 연락처 검색
        contact_response = self._search_contacts(user_input)
        if contact_response:
            return self._format_response(contact_response, "연락처")
        
        # 5. 카테고리별 키워드 매칭
        category_response = self._match_category(user_input)
        if category_response:
            return category_response
        
        # 6. 계층적 네비게이션 처리
        navigation_response = self._handle_navigation(user_input)
        if navigation_response:
            return navigation_response
        
        # 7. 자유입력 텍스트 검색 (2글자 이상)
        free_text_response = self._search_free_text(user_input)
        if free_text_response:
            return free_text_response
        
        # 8. 기본 응답
        response = random.choice(DEFAULT_RESPONSES)
        return self._format_response(response, "기본")
    
    def _check_emergency(self, text):
        """응급상황 키워드 확인"""
        for keyword, response in EMERGENCY_KEYWORDS.items():
            if keyword in text:
                return self._format_response(
                    f"🚨 {response}", 
                    "응급상황", 
                    priority="HIGH"
                )
        return None
    
    def _is_greeting(self, text):
        """인사말 감지"""
        greetings = ["안녕", "hello", "hi", "반가워", "처음", "시작", "헬로"]
        return any(greeting in text for greeting in greetings)
    
    def _get_greeting_response(self):
        """시간대별 인사말 생성"""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 12:
            time_greeting = TIME_GREETINGS["morning"]
        elif 12 <= current_hour < 18:
            time_greeting = TIME_GREETINGS["afternoon"]
        elif 18 <= current_hour < 22:
            time_greeting = TIME_GREETINGS["evening"]
        else:
            time_greeting = TIME_GREETINGS["night"]
        
        base_greeting = random.choice(GREETING_RESPONSES)
        
        if self.user_name:
            return f"{self.user_name}님, {time_greeting} {base_greeting}"
        else:
            return f"{time_greeting} {base_greeting}"
    
    def _check_name_setting(self, text):
        """사용자 이름 설정 확인"""
        # 다양한 이름 설정 패턴 처리
        if "이름" in text:
            # 패턴 1: "제 이름은 김철수입니다"
            if "이름은" in text or "이름는" in text:
                parts = text.split()
                for i, part in enumerate(parts):
                    if "이름은" in part or "이름는" in part:
                        if i + 1 < len(parts):
                            name = parts[i + 1].replace("입니다", "").replace(".", "").replace("예요", "")
                            if name and len(name) <= 10:  # 유효한 이름 길이 체크
                                self.user_name = name
                                return self._format_response(
                                    f"반갑습니다, {name}님! 앞으로 {name}님이라고 부르겠습니다.",
                                    "이름설정"
                                )
            
            # 패턴 2: "김철수라고 불러주세요"
            elif "불러" in text or "부르" in text:
                # 이름 추출 시도
                parts = text.split()
                for part in parts:
                    clean_part = part.replace("라고", "").replace("으로", "").replace("님", "")
                    if clean_part and len(clean_part) <= 10 and clean_part != "이름":
                        self.user_name = clean_part
                        return self._format_response(
                            f"알겠습니다, {clean_part}님! 앞으로 {clean_part}님이라고 부르겠습니다.",
                            "이름설정"
                        )
        
        return None
    
    def _search_faq(self, text):
        """FAQ 검색"""
        for keyword, answer in FAQ_DATA.items():
            if keyword in text:
                return f"📋 {answer}"
        return None
    
    def _search_contacts(self, text):
        """부서 연락처 검색"""
        if "연락처" in text or "번호" in text or "내선" in text:
            for department, contact in DEPARTMENT_CONTACTS.items():
                if department in text:
                    return f"📞 {department}: {contact}"
            
            # 전체 연락처 목록 요청
            if "전체" in text or "모든" in text:
                contact_list = "\n".join([f"{dept}: {num}" for dept, num in DEPARTMENT_CONTACTS.items()])
                return f"📞 부서별 연락처:\n{contact_list}"
        
        return None
    
    def _match_category(self, text):
        """카테고리 키워드 매칭"""
        for category, data in WORK_CATEGORIES.items():
            for keyword in data["keywords"]:
                if keyword in text:
                    response = random.choice(data["responses"])
                    return self._format_response(response, category)
        return None
    
    def _format_response(self, message, category, priority="NORMAL"):
        """응답 포맷팅"""
        return {
            "message": message,
            "category": category,
            "timestamp": self._get_current_time(),
            "priority": priority,
            "conversation_count": len(self.conversation_history)
        }
    
    def _get_current_time(self):
        """현재 시간 반환"""
        return datetime.now().strftime("%H:%M")
    
    def get_conversation_summary(self):
        """대화 요약 정보"""
        if not self.conversation_history:
            return "아직 대화 기록이 없습니다."
        
        total_messages = len(self.conversation_history)
        first_message_time = self.conversation_history[0]["timestamp"]
        last_message_time = self.conversation_history[-1]["timestamp"]
        
        return {
            "총 메시지 수": total_messages,
            "첫 메시지 시간": first_message_time,
            "마지막 메시지 시간": last_message_time,
            "사용자 이름": self.user_name or "미설정"
        }
    
    def _handle_navigation(self, text):
        """계층적 네비게이션 처리"""
        # 메인 메뉴로 돌아가기
        if any(keyword in text for keyword in ["메인", "처음", "홈", "돌아가기", "초기화"]):
            self.current_navigation = {
                "level": 0,
                "category": None,
                "subcategory": None,
                "sub_item": None
            }
            return self._show_main_categories()
        
        # 뒤로 가기
        if any(keyword in text for keyword in ["뒤로", "이전", "상위"]):
            return self._navigate_back()
        
        # 카테고리 선택 (Level 1)
        if self.current_navigation["level"] == 0:
            for category_key, category_data in HIERARCHICAL_WORK_DATA.items():
                if any(keyword in text for keyword in category_data["keywords"]) or category_data["name"] in text:
                    self.current_navigation = {
                        "level": 1,
                        "category": category_key,
                        "subcategory": None,
                        "sub_item": None
                    }
                    return self._show_subcategories(category_key)
        
        # 세부항목 선택 (Level 2)
        elif self.current_navigation["level"] == 1:
            category_key = self.current_navigation["category"]
            category_data = HIERARCHICAL_WORK_DATA[category_key]
            
            for subcat_key, subcat_data in category_data["subcategories"].items():
                if any(keyword in text for keyword in subcat_data["keywords"]) or subcat_data["name"] in text:
                    self.current_navigation["subcategory"] = subcat_key
                    self.current_navigation["level"] = 2
                    return self._show_sub_items(category_key, subcat_key)
        
        # 세부항목2 선택 (Level 3)
        elif self.current_navigation["level"] == 2:
            category_key = self.current_navigation["category"]
            subcat_key = self.current_navigation["subcategory"]
            subcat_data = HIERARCHICAL_WORK_DATA[category_key]["subcategories"][subcat_key]
            
            for item_key, item_data in subcat_data["sub_items"].items():
                if item_data["name"] in text or any(keyword in text for keyword in item_data["name"].split()):
                    self.current_navigation["sub_item"] = item_key
                    self.current_navigation["level"] = 3
                    return self._show_item_details(category_key, subcat_key, item_key)
        
        return None
    
    def _show_main_categories(self):
        """메인 카테고리 목록 표시"""
        categories = []
        for key, data in HIERARCHICAL_WORK_DATA.items():
            categories.append(f"• {data['name']}: {data['description']}")
        
        response = f"""🏥 차치업무 카테고리 선택

{chr(10).join(categories)}

원하는 카테고리를 선택해주세요.
예: "수리", "물품", "멸균품거즈", "격리실" 등"""
        
        return self._format_response(response, "메인메뉴")
    
    def _show_subcategories(self, category_key):
        """세부항목 목록 표시"""
        category_data = HIERARCHICAL_WORK_DATA[category_key]
        subcategories = []
        
        for key, data in category_data["subcategories"].items():
            subcategories.append(f"• {data['name']}: {data['description']}")
        
        response = f"""📂 {category_data['name']} - 세부항목

{chr(10).join(subcategories)}

원하는 세부항목을 선택해주세요.
💡 "뒤로" 또는 "메인"으로 이전 단계로 이동 가능합니다."""
        
        return self._format_response(response, f"{category_data['name']}_세부항목")
    
    def _show_sub_items(self, category_key, subcat_key):
        """세부항목2 목록 표시"""
        category_data = HIERARCHICAL_WORK_DATA[category_key]
        subcat_data = category_data["subcategories"][subcat_key]
        items = []
        
        for key, data in subcat_data["sub_items"].items():
            items.append(f"• {data['name']}")
        
        response = f"""📋 {category_data['name']} > {subcat_data['name']}

{chr(10).join(items)}

원하는 항목을 선택해주세요.
💡 "뒤로" 또는 "메인"으로 이전 단계로 이동 가능합니다."""
        
        return self._format_response(response, f"{subcat_data['name']}_항목목록")
    
    def _show_item_details(self, category_key, subcat_key, item_key):
        """세부항목2 상세 정보 표시"""
        item_data = HIERARCHICAL_WORK_DATA[category_key]["subcategories"][subcat_key]["sub_items"][item_key]
        
        response = f"""📝 {item_data['name']} 상세 정보

🔧 요청방법:
{item_data['request_method']}

{item_data['contact']}

💡 추가정보: {item_data['free_text']}

💬 다른 항목을 보려면 "뒤로", 처음부터 시작하려면 "메인"을 입력하세요."""
        
        return self._format_response(response, f"{item_data['name']}_상세")
    
    def _navigate_back(self):
        """이전 단계로 이동"""
        if self.current_navigation["level"] == 3:
            # 세부항목2에서 세부항목으로
            self.current_navigation["level"] = 2
            self.current_navigation["sub_item"] = None
            return self._show_sub_items(
                self.current_navigation["category"], 
                self.current_navigation["subcategory"]
            )
        elif self.current_navigation["level"] == 2:
            # 세부항목에서 항목으로
            self.current_navigation["level"] = 1
            self.current_navigation["subcategory"] = None
            return self._show_subcategories(self.current_navigation["category"])
        elif self.current_navigation["level"] == 1:
            # 항목에서 메인으로
            self.current_navigation = {
                "level": 0,
                "category": None,
                "subcategory": None,
                "sub_item": None
            }
            return self._show_main_categories()
        else:
            # 이미 메인 메뉴
            return self._show_main_categories()
    
    def _search_free_text(self, text):
        """자유입력 텍스트 검색 (2글자 이상)"""
        if len(text.strip()) < 2:
            return None
        
        search_results = []
        
        # 모든 계층 데이터에서 free_text 필드 검색
        for category_key, category_data in HIERARCHICAL_WORK_DATA.items():
            for subcat_key, subcat_data in category_data["subcategories"].items():
                for item_key, item_data in subcat_data["sub_items"].items():
                    # free_text에서 2글자 이상 매칭되는 부분 찾기
                    if self._text_similarity(text, item_data["free_text"]) >= 2:
                        search_results.append({
                            "category": category_data["name"],
                            "subcategory": subcat_data["name"],
                            "item_name": item_data["name"],
                            "request_method": item_data["request_method"],
                            "contact": item_data["contact"],
                            "free_text": item_data["free_text"],
                            "match_score": self._text_similarity(text, item_data["free_text"])
                        })
        
        if search_results:
            # 매칭 점수순으로 정렬
            search_results.sort(key=lambda x: x["match_score"], reverse=True)
            
            # 상위 3개 결과만 표시
            top_results = search_results[:3]
            
            response_parts = ["🔍 검색 결과:\n"]
            
            for i, result in enumerate(top_results, 1):
                response_parts.append(f"""
{i}. **{result['item_name']}**
   📂 {result['category']} > {result['subcategory']}
   
   🔧 요청방법:
   {result['request_method']}
   
   {result['contact']}
   
   💡 {result['free_text']}
   {"="*50}""")
            
            response_parts.append("\n💬 더 자세한 내용을 원하시면 해당 카테고리로 이동해주세요.")
            
            return self._format_response("\n".join(response_parts), "검색결과")
        
        return None
    
    def _text_similarity(self, search_text, target_text):
        """텍스트 유사도 계산 (2글자 이상 연속 매칭)"""
        search_text = search_text.lower().strip()
        target_text = target_text.lower()
        
        max_match_length = 0
        
        # 2글자 이상의 연속 매칭 찾기
        for i in range(len(search_text) - 1):
            for length in range(2, len(search_text) - i + 1):
                substring = search_text[i:i + length]
                if substring in target_text:
                    max_match_length = max(max_match_length, length)
        
        return max_match_length

    def get_help_message(self):
        """도움말 메시지"""
        help_text = f"""
🏥 차치업무 도우미 챗봇 사용법

📋 계층적 네비게이션:
• 메인 카테고리 → 세부항목 → 세부항목2 순서로 탐색
• "뒤로" - 이전 단계로 이동
• "메인" - 처음으로 돌아가기

🔍 검색 기능:
• 2글자 이상 입력시 관련 항목 검색
• 자유로운 텍스트로 원하는 정보 찾기

📂 현재 위치: {self._get_current_location()}

💬 사용 예시:
• "수리" → 수리 관련 세부항목 표시
• "EKG 수리" → EKG 관련 정보 검색
• "거즈 공급" → 거즈 관련 정보 표시

🆘 응급상황:
• "응급", "화재", "코드블루" 등의 키워드 사용
        """
        
        return self._format_response(help_text.strip(), "도움말")
    
    def _get_current_location(self):
        """현재 네비게이션 위치 표시"""
        if self.current_navigation["level"] == 0:
            return "메인 메뉴"
        elif self.current_navigation["level"] == 1:
            category_name = HIERARCHICAL_WORK_DATA[self.current_navigation["category"]]["name"]
            return f"{category_name}"
        elif self.current_navigation["level"] == 2:
            category_name = HIERARCHICAL_WORK_DATA[self.current_navigation["category"]]["name"]
            subcat_name = HIERARCHICAL_WORK_DATA[self.current_navigation["category"]]["subcategories"][self.current_navigation["subcategory"]]["name"]
            return f"{category_name} > {subcat_name}"
        elif self.current_navigation["level"] == 3:
            category_name = HIERARCHICAL_WORK_DATA[self.current_navigation["category"]]["name"]
            subcat_name = HIERARCHICAL_WORK_DATA[self.current_navigation["category"]]["subcategories"][self.current_navigation["subcategory"]]["name"]
            item_name = HIERARCHICAL_WORK_DATA[self.current_navigation["category"]]["subcategories"][self.current_navigation["subcategory"]]["sub_items"][self.current_navigation["sub_item"]]["name"]
            return f"{category_name} > {subcat_name} > {item_name}"
        
        return "알 수 없음"

# 챗봇 인스턴스를 전역으로 사용할 수 있도록 생성
chatbot_instance = SimpleHospitalChatbot()

def get_chatbot_response(user_input):
    """
    외부에서 챗봇 응답을 받기 위한 함수
    Args:
        user_input (str): 사용자 입력
    Returns:
        dict: 챗봇 응답
    """
    return chatbot_instance.process_message(user_input)

if __name__ == "__main__":
    # 테스트용 대화형 실행
    print("=" * 50)
    print("🏥 차치업무 도우미 챗봇 테스트")
    print("=" * 50)
    print("종료하려면 'quit' 또는 'exit'를 입력하세요")
    print("도움말을 보려면 'help'를 입력하세요")
    print("-" * 50)
    
    chatbot = SimpleHospitalChatbot()
    
    while True:
        try:
            user_input = input("👤 당신: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료', '나가기']:
                print("👋 챗봇을 종료합니다. 수고하셨습니다!")
                break
            
            if user_input.lower() in ['help', '도움말']:
                response = chatbot.get_help_message()
            elif user_input.lower() in ['summary', '요약']:
                summary = chatbot.get_conversation_summary()
                response = {"message": str(summary), "category": "요약"}
            else:
                response = chatbot.process_message(user_input)
            
            print(f"🤖 챗봇: {response['message']}")
            print(f"   [카테고리: {response['category']} | 시간: {response['timestamp']}]")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 챗봇을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")
