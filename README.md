# 🏥 삼성서울병원 중앙간호사 도우미

## 🌐 온라인 데모
**GitHub Pages에서 바로 사용해보세요!**
```
https://[사용자명].github.io/hospital-chat-request/
```

Python 기반 웹 챗봇과 GitHub Pages 정적 웹사이트 두 가지 버전을 제공하는 병동 간호업무 도우미 시스템입니다.

## 📋 프로젝트 개요

- **목적**: 삼성서울병원 중앙간호사를 위한 업무 지원 시스템
- **기술 스택**: Python (서버), HTML/CSS/JavaScript (클라이언트), GitHub Pages (배포)
- **특징**: 계층적 네비게이션, 자유텍스트 검색, 반응형 UI

## 🎯 주요 기능

### 💬 챗봇 기능
- **계층적 네비게이션**: 간호업무 > 세부업무 > 상세절차 구조로 체계적 탐색
- **자유텍스트 검색**: 2글자 이상 입력시 관련 간호업무 자동 검색
- **동적 버튼 시스템**: 상황별 맞춤 네비게이션 버튼
- **간호업무별 카테고리 분류**: 수리, 물품, 멸균품/거즈, 격리실 등
- **실시간 연락처 안내**: 부서별 담당자 정보 제공
- **응급상황 우선 처리**: 응급, 화재, 코드블루 등

### 🌐 웹 인터페이스
- **반응형 디자인**: 데스크톱, 태블릿, 모바일 최적화
- **현대적 UI**: 메신저 스타일 챗봇 인터페이스
- **실시간 타이핑 인디케이터**: 자연스러운 대화 경험
- **다크/라이트 테마**: 사용자 환경 고려
- **키보드 단축키**: 접근성 향상

## 🚀 사용 방법

### 🌐 GitHub Pages (권장)
1. 위의 온라인 데모 링크 접속
2. 바로 사용 시작!

### 💻 로컬 서버 실행
```bash
# 저장소 클론
git clone https://github.com/[사용자명]/hospital-chat-request.git
cd hospital-chat-request/hospital_chatbot

# 서버 실행
python3 server.py

# 브라우저에서 접속
# http://localhost:8000
```

## 📁 프로젝트 구조

```
hospital-chat-request/
├── docs/                           # GitHub Pages 정적 웹사이트
│   ├── index.html                 # 메인 웹페이지
│   ├── data.js                    # 간호업무 데이터
│   ├── chatbot.js                 # 챗봇 로직
│   ├── .nojekyll                  # Jekyll 비활성화
│   └── README.md                  # 배포 가이드
├── hospital_chatbot/              # Python 서버 버전
│   ├── hierarchical_chatbot.py    # 챗봇 로직
│   ├── enhanced_excel_data.py     # 엑셀 데이터
│   ├── server.py                  # 웹 서버
│   ├── static/                    # 정적 파일
│   └── templates/                 # HTML 템플릿
├── .github/workflows/             # GitHub Actions
│   └── pages.yml                  # 자동 배포 설정
└── README.md                      # 이 파일
```

## 💻 사용 예시

### 🔄 계층적 네비게이션
1. **수리** → **의료기기** → **EKG 수리 요청** → 상세 절차 확인
2. **물품** → **구매의뢰** → **CPOE 등록 방법** → 연락처 안내
3. **격리실** → **VRE** → **새로 발생 시 절차** → 단계별 가이드

### 🔍 자유텍스트 검색 (2글자 이상)
- **"수리"** → 수리 관련 모든 정보 검색
- **"거즈"** → 거즈 공급 관련 상세 안내
- **"격리"** → 격리실 운영 절차 검색
- **"연락처"** → 부서별 연락처 정보

### 🎯 기본 대화
- **"안녕하세요"** → 시간대별 인사말
- **"제 이름은 김철수입니다"** → 개인화된 응답
- **"도움말"** → 상세 사용법 안내

### 🆘 응급상황
- **"응급"**, **"화재"**, **"코드블루"** → 즉시 대응 절차 안내

## 🌐 GitHub Pages 배포

### 자동 배포 (권장)
1. GitHub 저장소 Fork 또는 Clone
2. Settings → Pages → Source: "GitHub Actions" 선택
3. `main` 브랜치로 푸시하면 자동 배포

### 수동 배포
1. Settings → Pages → Source: "Deploy from a branch"
2. Branch: `main`, Folder: `/docs` 선택
3. 5-10분 후 `https://[사용자명].github.io/hospital-chat-request/` 접속

## 🔧 커스터마이징

### 데이터 수정
- **GitHub Pages**: `docs/data.js` 파일 수정
- **Python 버전**: `hospital_chatbot/enhanced_excel_data.py` 파일 수정

### UI 수정
- **GitHub Pages**: `docs/index.html` 내 CSS 섹션 수정
- **Python 버전**: `hospital_chatbot/templates/hierarchical_index.html` 수정

## 📊 기술 세부사항

### 🌐 정적 웹사이트 버전
- **언어**: HTML5, CSS3, JavaScript (ES6+)
- **데이터**: JSON 형태의 정적 데이터
- **검색**: 클라이언트 사이드 키워드 매칭
- **성능**: 메시지 제한(50개), 지연 로딩

### 💻 Python 서버 버전
- **백엔드**: Python HTTP Server
- **프론트엔드**: HTML, CSS, JavaScript
- **데이터**: Python Dictionary 구조
- **세션**: 서버 사이드 세션 관리

## 📱 호환성

- **브라우저**: Chrome, Firefox, Safari, Edge (최신 버전)
- **디바이스**: 데스크톱, 태블릿, 모바일
- **네트워크**: 오프라인 지원 (정적 버전)
- **접근성**: 키보드 네비게이션, 스크린 리더 지원

## 🔄 최신 업데이트

### 2024.09.26 - v2.0 (GitHub Pages 지원)
- ✅ GitHub Pages 정적 웹사이트 버전 추가
- ✅ JavaScript 챗봇 로직 완전 구현
- ✅ 반응형 모바일 UI 최적화
- ✅ 자동 배포 GitHub Actions 설정
- ✅ 오프라인 지원 가능한 구조

### 2024.09.26 - v1.0 (Python 서버)
- ✅ 계층적 데이터 구조 구현
- ✅ 엑셀 데이터 완전 파싱 (63개 세부항목)
- ✅ 자유텍스트 검색 기능
- ✅ 동적 UI 및 네비게이션 버튼
- ✅ 타이핑 인디케이터 및 애니메이션

## 🤝 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

- **개발팀**: 삼성서울병원 IT지원팀
- **이슈 신고**: GitHub Issues
- **기능 제안**: GitHub Discussions

---

💻 **개발**: 삼성서울병원 중앙간호사 도우미 개발팀  
🌐 **온라인 데모**: [GitHub Pages](https://[사용자명].github.io/hospital-chat-request/)  
📅 **최종 업데이트**: 2024년 9월 26일
