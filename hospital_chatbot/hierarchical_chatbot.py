# -*- coding: utf-8 -*-
"""
계층적 차치업무 도우미 챗봇
실제 엑셀 데이터를 기반으로 한 항목 > 세부항목 > 세부항목2 구조
"""

import random
from datetime import datetime
from excel_data import (
    HIERARCHICAL_WORK_DATA, GREETING_RESPONSES, DEFAULT_RESPONSES, 
    FAQ_DATA, TIME_GREETINGS, EMERGENCY_KEYWORDS, DEPARTMENT_CONTACTS
)

class HierarchicalHospitalChatbot:
    """계층적 차치업무 도우미 챗봇"""
    
    def __init__(self):
        """챗봇 초기화"""
        self.conversation_history = []
        self.user_name = None
        self.current_navigation = {
            "level": 0,               # 0: 메인, 1: 세부항목, 2: 세부항목2
            "main_category": None,    # 선택된 메인 카테고리
            "subcategory_key": None,  # 선택된 세부항목 키
            "sub_item_key": None      # 선택된 세부항목2 키
        }
        print("🏥 삼성서울병원 중앙간호사 도우미 챗봇이 시작되었습니다!")
    
    def process_message(self, user_input):
        """
        사용자 입력을 처리하고 응답 생성
        """
        if not user_input or not user_input.strip():
            return self._create_response("메시지를 입력해주세요.", "안내")
        
        user_input = user_input.strip()
        self.conversation_history.append(f"사용자: {user_input}")
        
        # 1. 응급상황 최우선 처리
        emergency_response = self._check_emergency(user_input)
        if emergency_response:
            return emergency_response
        
        # 2. 네비게이션 명령어 처리
        nav_command = self._handle_navigation_commands(user_input)
        if nav_command:
            return nav_command
        
        # 3. 사용자 이름 설정
        name_response = self._handle_name_setting(user_input)
        if name_response:
            return name_response
        
        # 4. 인사말 처리
        greeting_response = self._handle_greeting(user_input)
        if greeting_response:
            return greeting_response
        
        # 5. FAQ 처리
        faq_response = self._handle_faq(user_input)
        if faq_response:
            return faq_response
        
        # 6. 계층적 네비게이션 처리
        hierarchy_response = self._handle_hierarchical_navigation(user_input)
        if hierarchy_response:
            return hierarchy_response
        
        # 7. 자유텍스트 검색 (2글자 이상)
        free_text_response = self._search_free_text(user_input)
        if free_text_response:
            return free_text_response
        
        # 8. 기본 응답 (메인 카테고리 표시)
        return self._show_main_categories()
    
    def _handle_navigation_commands(self, text):
        """네비게이션 명령어 처리"""
        text_lower = text.lower()
        
        # 메인으로 돌아가기
        if any(keyword in text_lower for keyword in ["메인", "처음", "홈", "초기화"]):
            self._reset_navigation()
            return self._show_main_categories()
        
        # 뒤로 가기
        if any(keyword in text_lower for keyword in ["뒤로", "이전", "back"]):
            return self._go_back()
        
        return None
    
    def _handle_hierarchical_navigation(self, text):
        """현재 레벨에 따른 계층적 네비게이션 처리"""
        level = self.current_navigation["level"]
        
        if level == 0:
            # 메인 카테고리 선택
            return self._handle_main_category_selection(text)
        elif level == 1:
            # 세부항목 선택
            return self._handle_subcategory_selection(text)
        elif level == 2:
            # 세부항목2 선택
            return self._handle_sub_item_selection(text)
        
        return None
    
    def _handle_main_category_selection(self, text):
        """메인 카테고리 선택 처리"""
        text_lower = text.lower()
        
        # 정확한 카테고리명 매칭
        for category_name in HIERARCHICAL_WORK_DATA.keys():
            if category_name.lower() in text_lower or text_lower in category_name.lower():
                self.current_navigation["main_category"] = category_name
                self.current_navigation["level"] = 1
                return self._show_subcategories(category_name)
        
        # 키워드 매칭
        for category_name, category_data in HIERARCHICAL_WORK_DATA.items():
            for keyword in category_data.get("keywords", []):
                if keyword in text_lower:
                    self.current_navigation["main_category"] = category_name
                    self.current_navigation["level"] = 1
                    return self._show_subcategories(category_name)
        
        return None
    
    def _handle_subcategory_selection(self, text):
        """세부항목 선택 처리"""
        if not self.current_navigation["main_category"]:
            return self._show_main_categories()
        
        category_data = HIERARCHICAL_WORK_DATA[self.current_navigation["main_category"]]
        text_lower = text.lower()
        
        # 세부항목 매칭
        for subcat_key, subcat_data in category_data["subcategories"].items():
            subcat_name = subcat_data["name"]
            if subcat_name.lower() in text_lower or text_lower in subcat_name.lower():
                self.current_navigation["subcategory_key"] = subcat_key
                self.current_navigation["level"] = 2
                return self._show_sub_items(subcat_key)
        
        return None
    
    def _handle_sub_item_selection(self, text):
        """세부항목2 선택 처리"""
        if not self.current_navigation["main_category"] or not self.current_navigation["subcategory_key"]:
            return self._show_main_categories()
        
        category_data = HIERARCHICAL_WORK_DATA[self.current_navigation["main_category"]]
        subcat_data = category_data["subcategories"][self.current_navigation["subcategory_key"]]
        text_lower = text.lower()
        
        # 세부항목2 매칭
        for item_key, item_data in subcat_data["sub_items"].items():
            item_name = item_data["name"]
            if item_name.lower() in text_lower or text_lower in item_name.lower():
                return self._show_final_result(item_key)
        
        return None
    
    def _show_main_categories(self):
        """메인 카테고리 목록 표시"""
        self._reset_navigation()
        
        message = "🏥 **병동 간호업무 카테고리 선택**\n\n"
        message += "원하는 간호업무 카테고리를 선택해주세요:\n\n"
        
        buttons = []
        for i, (category_name, category_data) in enumerate(HIERARCHICAL_WORK_DATA.items(), 1):
            message += f"{i}. **{category_name}** - {category_data['description']}\n"
            buttons.append({
                "text": category_name,
                "action": "category",
                "value": category_name
            })
        
        message += "\n💡 **사용 팁:** 카테고리명을 입력하거나 버튼을 클릭하세요!"
        
        return self._create_response(message, "메인메뉴", buttons)
    
    def _show_subcategories(self, category_name):
        """세부항목 목록 표시"""
        if category_name not in HIERARCHICAL_WORK_DATA:
            return self._show_main_categories()
        
        category_data = HIERARCHICAL_WORK_DATA[category_name]
        
        message = f"📁 **{category_name}** 세부간호업무\n\n"
        message += f"{category_data['description']}\n\n"
        message += "세부간호업무를 선택해주세요:\n\n"
        
        buttons = []
        for i, (subcat_key, subcat_data) in enumerate(category_data["subcategories"].items(), 1):
            subcat_name = subcat_data["name"]
            message += f"{i}. **{subcat_name}**\n"
            buttons.append({
                "text": subcat_name,
                "action": "subcategory", 
                "value": subcat_key
            })
        
        # 네비게이션 버튼 추가
        buttons.extend([
            {"text": "🔙 뒤로", "action": "nav", "value": "back"},
            {"text": "🏠 메인", "action": "nav", "value": "main"}
        ])
        
        return self._create_response(message, f"{category_name}_세부항목", buttons)
    
    def _show_sub_items(self, subcategory_key):
        """세부항목2 목록 표시"""
        category_name = self.current_navigation["main_category"]
        category_data = HIERARCHICAL_WORK_DATA[category_name]
        subcat_data = category_data["subcategories"][subcategory_key]
        
        message = f"📄 **{subcat_data['name']}** 상세절차\n\n"
        message += f"{subcat_data['description']}\n\n"
        message += "상세절차를 선택해주세요:\n\n"
        
        buttons = []
        for i, (item_key, item_data) in enumerate(subcat_data["sub_items"].items(), 1):
            item_name = item_data["name"]
            message += f"{i}. **{item_name}**\n"
            buttons.append({
                "text": item_name,
                "action": "sub_item",
                "value": item_key
            })
        
        # 네비게이션 버튼 추가
        buttons.extend([
            {"text": "🔙 뒤로", "action": "nav", "value": "back"},
            {"text": "🏠 메인", "action": "nav", "value": "main"}
        ])
        
        return self._create_response(message, f"{subcat_data['name']}_상세항목", buttons)
    
    def _show_final_result(self, sub_item_key):
        """최종 결과 표시"""
        category_name = self.current_navigation["main_category"]
        subcat_key = self.current_navigation["subcategory_key"]
        
        category_data = HIERARCHICAL_WORK_DATA[category_name]
        subcat_data = category_data["subcategories"][subcat_key]
        item_data = subcat_data["sub_items"][sub_item_key]
        
        message = f"✅ **{item_data['name']}**\n\n"
        
        # 요청방법
        if item_data["request_method"]:
            message += f"📋 **요청방법:**\n{item_data['request_method']}\n\n"
        
        # 연락처
        if item_data["contact"]:
            message += f"📞 **연락처:**\n{item_data['contact']}\n\n"
        
        # 관련 정보
        if item_data["free_text"]:
            message += f"🔍 **관련 정보:**\n{item_data['free_text']}\n\n"
        
        # 비고
        if item_data["note"]:
            message += f"💡 **비고:**\n{item_data['note']}\n\n"
        
        # 네비게이션 버튼
        buttons = [
            {"text": "🔙 뒤로", "action": "nav", "value": "back"},
            {"text": "🏠 메인", "action": "nav", "value": "main"},
            {"text": "🔍 다시 검색", "action": "search", "value": "new"}
        ]
        
        return self._create_response(message, "최종결과", buttons)
    
    def _search_free_text(self, text):
        """자유텍스트에서 2글자 이상 검색"""
        if len(text) < 2:
            return None
        
        search_results = []
        text_lower = text.lower()
        
        for category_name, category_data in HIERARCHICAL_WORK_DATA.items():
            for subcat_key, subcat_data in category_data["subcategories"].items():
                for item_key, item_data in subcat_data["sub_items"].items():
                    free_text = item_data.get("free_text", "").lower()
                    
                    # 연속 2글자 이상 매칭 검사
                    match_score = self._calculate_match_score(text_lower, free_text)
                    if match_score > 0:
                        search_results.append({
                            "score": match_score,
                            "category": category_name,
                            "subcategory": subcat_data["name"],
                            "item": item_data,
                            "path": f"{category_name} > {subcat_data['name']} > {item_data['name']}"
                        })
        
        if not search_results:
            return None
        
        # 점수순으로 정렬 후 상위 3개
        search_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = search_results[:3]
        
        message = f"🔍 **'{text}' 검색 결과**\n\n"
        buttons = []
        
        for i, result in enumerate(top_results, 1):
            message += f"{i}. **{result['path']}**\n"
            message += f"   {result['item']['request_method'][:100]}...\n\n"
            
            buttons.append({
                "text": result['item']['name'],
                "action": "direct_result",
                "value": f"{result['category']}|{result['subcategory']}|{result['item']['name']}"
            })
        
        buttons.extend([
            {"text": "🏠 메인", "action": "nav", "value": "main"},
            {"text": "🔍 새 검색", "action": "search", "value": "new"}
        ])
        
        return self._create_response(message, "검색결과", buttons)
    
    def _calculate_match_score(self, search_text, target_text):
        """매칭 점수 계산 (연속 2글자 이상)"""
        if len(search_text) < 2:
            return 0
        
        score = 0
        for i in range(len(search_text) - 1):
            substring = search_text[i:i+2]
            if substring in target_text:
                score += 2
                # 더 긴 매칭에 대해 보너스 점수
                for j in range(3, min(len(search_text) - i + 1, 10)):
                    longer_substring = search_text[i:i+j]
                    if longer_substring in target_text:
                        score += j - 1
                    else:
                        break
        
        return score
    
    def _go_back(self):
        """이전 단계로 이동"""
        level = self.current_navigation["level"]
        
        if level == 0:
            return self._show_main_categories()
        elif level == 1:
            return self._show_main_categories()
        elif level == 2:
            self.current_navigation["level"] = 1
            self.current_navigation["subcategory_key"] = None
            return self._show_subcategories(self.current_navigation["main_category"])
        
        return self._show_main_categories()
    
    def _reset_navigation(self):
        """네비게이션 초기화"""
        self.current_navigation = {
            "level": 0,
            "main_category": None,
            "subcategory_key": None,
            "sub_item_key": None
        }
    
    def _check_emergency(self, text):
        """응급상황 키워드 확인"""
        text_lower = text.lower()
        for keyword, response in EMERGENCY_KEYWORDS.items():
            if keyword in text_lower:
                return self._create_response(f"🚨 **응급상황 감지!**\n\n{response}", "응급", [])
        return None
    
    def _handle_name_setting(self, text):
        """사용자 이름 설정"""
        patterns = ["제 이름은", "내 이름은", "이름:", "name is", "나는"]
        text_lower = text.lower()
        
        for pattern in patterns:
            if pattern in text_lower:
                # 이름 추출
                name_start = text_lower.find(pattern) + len(pattern)
                name_part = text[name_start:].strip()
                if name_part:
                    # 불필요한 문자 제거
                    name = name_part.replace("입니다", "").replace("이에요", "").replace(".", "").strip()
                    self.user_name = name
                    return self._create_response(f"안녕하세요, {name}님! 반갑습니다. 무엇을 도와드릴까요?", "이름설정")
        
        return None
    
    def _handle_greeting(self, text):
        """인사말 처리"""
        greeting_keywords = ["안녕", "hello", "hi", "하이", "반가", "처음", "시작"]
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in greeting_keywords):
            hour = datetime.now().hour
            if 5 <= hour < 12:
                time_greeting = TIME_GREETINGS["morning"]
            elif 12 <= hour < 17:
                time_greeting = TIME_GREETINGS["afternoon"]
            elif 17 <= hour < 21:
                time_greeting = TIME_GREETINGS["evening"]
            else:
                time_greeting = TIME_GREETINGS["night"]
            
            name_part = f" {self.user_name}님" if self.user_name else ""
            message = f"{time_greeting}{name_part}\n\n{random.choice(GREETING_RESPONSES)}"
            
            return self._create_response(message, "인사")
        
        return None
    
    def _handle_faq(self, text):
        """FAQ 처리"""
        text_lower = text.lower()
        for keyword, answer in FAQ_DATA.items():
            if keyword.lower() in text_lower:
                return self._create_response(answer, "FAQ")
        return None
    
    def _create_response(self, message, category, buttons=None):
        """응답 생성"""
        response = {
            "message": message,
            "category": category,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": self.user_name
        }
        
        if buttons:
            response["buttons"] = buttons
        
        # 대화 기록에 추가
        self.conversation_history.append(f"봇: {message[:100]}...")
        
        return response
    
    def get_conversation_history(self):
        """대화 기록 반환"""
        return self.conversation_history
    
    def reset_conversation(self):
        """대화 초기화"""
        self.conversation_history = []
        self._reset_navigation()
        self.user_name = None
        return self._show_main_categories()
    
    def get_help_message(self):
        """도움말 메시지 반환"""
        help_text = """
🏥 삼성서울병원 중앙간호사 도우미 사용법

📋 주요 기능:
• 3단계 계층 네비게이션: 간호업무 → 세부업무 → 상세절차
• 자유텍스트 검색: 2글자 이상 입력으로 관련 간호업무 검색
• 실시간 버튼 네비게이션: 단계별 선택 버튼 제공

🎯 사용 방법:
1. 간호업무 카테고리 선택 (수리, 물품, 제제약/수액 등)
2. 세부간호업무 선택 (의료기기, 일반적인 수리 업무 등)
3. 상세절차 선택하여 최종 정보 확인

💬 네비게이션 명령어:
• "메인", "처음", "홈" - 메인 카테고리로 이동
• "뒤로", "이전" - 이전 단계로 이동

🔍 검색 기능:
• 2글자 이상 입력하면 자동 검색
• 예: "수리", "거즈", "격리실" 등

🆘 응급상황:
• "응급", "화재", "코드블루" 등의 키워드 사용

📞 주요 연락처:
• 의공기술실: T.9233
• 정보지원팀: T.3217
• 통신실: T.3333
        """
        
        return self._create_response(help_text.strip(), "도움말")
