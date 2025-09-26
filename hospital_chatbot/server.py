# -*- coding: utf-8 -*-
"""
삼성서울병원 중앙간호사 도우미 - 웹 서버
Python 기본 HTTP 서버를 사용한 웹 애플리케이션
"""

import os
import json
import urllib.parse
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from hierarchical_chatbot import HierarchicalHospitalChatbot

class ChatbotRequestHandler(BaseHTTPRequestHandler):
    """챗봇 웹 서버 요청 처리 클래스"""
    
    # 클래스 변수로 사용자 세션 관리
    user_sessions = {}
    
    def __init__(self, *args, **kwargs):
        # 현재 파일의 디렉토리 경로
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """GET 요청 처리 (HTML 페이지 및 정적 파일 서빙)"""
        try:
            if self.path == '/' or self.path == '/index.html':
                self._serve_file('templates/hierarchical_index.html', 'text/html')
            elif self.path == '/static/style.css':
                self._serve_file('static/style.css', 'text/css')
            elif self.path == '/static/script.js':
                self._serve_file('static/script.js', 'application/javascript')
            elif self.path == '/help':
                self._handle_help_request()
            elif self.path == '/favicon.ico':
                # favicon 요청 무시
                self.send_response(204)
                self.end_headers()
            else:
                self._send_error(404, "페이지를 찾을 수 없습니다.")
        except Exception as e:
            print(f"GET 요청 처리 오류: {e}")
            self._send_error(500, "서버 내부 오류가 발생했습니다.")
    
    def do_POST(self):
        """POST 요청 처리 (챗봇 메시지 처리)"""
        try:
            if self.path == '/chat':
                self._handle_chat_request()
            elif self.path == '/help':
                self._handle_help_request()
            else:
                self._send_error(404, "API 엔드포인트를 찾을 수 없습니다.")
        except Exception as e:
            print(f"POST 요청 처리 오류: {e}")
            self._send_error(500, "서버 내부 오류가 발생했습니다.")
    
    def _get_user_session(self, request_data):
        """사용자 세션 가져오기 또는 생성"""
        session_id = request_data.get('session_id')
        
        # 세션 ID가 없거나 유효하지 않으면 새로 생성
        if not session_id or session_id not in self.user_sessions:
            session_id = str(uuid.uuid4())
            self.user_sessions[session_id] = HierarchicalHospitalChatbot()
            print(f"새 사용자 세션 생성: {session_id[:8]}...")
        
        return session_id, self.user_sessions[session_id]
    
    def _handle_chat_request(self):
        """챗봇 메시지 처리"""
        try:
            # 요청 데이터 읽기
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "요청 데이터가 없습니다.")
                return
            
            post_data = self.rfile.read(content_length)
            
            # JSON 데이터 파싱
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_error(400, "잘못된 JSON 형식입니다.")
                return
            
            user_message = data.get('message', '').strip()
            if not user_message:
                self._send_error(400, "메시지가 비어있습니다.")
                return
            
            # 사용자 세션 가져오기
            session_id, user_chatbot = self._get_user_session(data)
            
            # 챗봇 응답 생성
            bot_response = user_chatbot.process_message(user_message)
            
            # 세션 ID를 응답에 포함
            bot_response['session_id'] = session_id
            
            # 성공 응답 전송
            self._send_json_response(bot_response)
            
            # 서버 로그 출력
            print(f"[{bot_response['timestamp']}] 세션 {session_id[:8]}: {user_message}")
            print(f"[{bot_response['timestamp']}] 챗봇: {bot_response['message'][:50]}...")
            
        except Exception as e:
            print(f"챗봇 요청 처리 오류: {e}")
            self._send_error(500, "챗봇 처리 중 오류가 발생했습니다.")
    
    def _handle_help_request(self):
        """도움말 요청 처리"""
        try:
            # 임시 챗봇 인스턴스로 도움말 생성
            temp_chatbot = HierarchicalHospitalChatbot()
            help_response = temp_chatbot.get_help_message()
            self._send_json_response(help_response)
        except Exception as e:
            print(f"도움말 요청 처리 오류: {e}")
            self._send_error(500, "도움말 로드 중 오류가 발생했습니다.")
    
    def _serve_file(self, file_path, content_type):
        """파일 서빙"""
        # 보안: 경로 탐색 공격 방지
        if '..' in file_path or file_path.startswith('/'):
            self._send_error(403, "잘못된 파일 경로입니다.")
            return
            
        full_path = os.path.join(self.base_path, file_path)
        
        # 보안: 기본 경로 밖의 파일 접근 차단
        if not full_path.startswith(self.base_path):
            self._send_error(403, "접근이 거부되었습니다.")
            return
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type + '; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('X-Content-Type-Options', 'nosniff')  # 보안 헤더
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self._send_error(404, f"파일을 찾을 수 없습니다: {file_path}")
        except UnicodeDecodeError:
            self._send_error(500, f"파일 인코딩 오류: {file_path}")
        except PermissionError:
            self._send_error(403, f"파일 접근 권한이 없습니다: {file_path}")
        except Exception as e:
            print(f"파일 서빙 오류: {e}")
            self._send_error(500, "파일 로드 중 오류가 발생했습니다.")
    
    def _send_json_response(self, data):
        """JSON 응답 전송"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """에러 응답 전송"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {
            "error": True,
            "status_code": status_code,
            "message": message,
            "timestamp": self._get_current_time()
        }
        
        response_data = json.dumps(error_data, ensure_ascii=False, indent=2)
        self.wfile.write(response_data.encode('utf-8'))
    
    def do_OPTIONS(self):
        """CORS preflight 요청 처리"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _get_current_time(self):
        """현재 시간 반환"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def log_message(self, format, *args):
        """서버 로그 메시지 포맷팅"""
        print(f"[서버] {self._get_current_time()} - {format % args}")

class HospitalChatbotServer:
    """병원 챗봇 서버 클래스"""
    
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.server = None
    
    def start(self):
        """서버 시작"""
        try:
            server_address = (self.host, self.port)
            self.server = HTTPServer(server_address, ChatbotRequestHandler)
            
            print("=" * 60)
            print("🏥 삼성서울병원 중앙간호사 도우미 서버")
            print("=" * 60)
            print(f"📍 서버 주소: http://{self.host}:{self.port}")
            print(f"🚀 서버가 시작되었습니다...")
            print("=" * 60)
            print("📋 이용 방법:")
            print("   1. 웹 브라우저에서 위 주소로 접속")
            print("   2. 챗봇과 대화 시작")
            print("   3. 서버 종료: Ctrl+C")
            print("=" * 60)
            
            # 서버 실행
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 서버를 종료합니다...")
            self.stop()
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"❌ 포트 {self.port}가 이미 사용 중입니다.")
                print(f"   다른 포트를 사용하거나 기존 프로세스를 종료해주세요.")
            else:
                print(f"❌ 서버 시작 오류: {e}")
        except Exception as e:
            print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
    
    def stop(self):
        """서버 중지"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("✅ 서버가 정상적으로 종료되었습니다.")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='삼성서울병원 중앙간호사 도우미 서버')
    parser.add_argument('--host', default='localhost', help='서버 호스트 (기본값: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='서버 포트 (기본값: 8000)')
    
    args = parser.parse_args()
    
    # 서버 시작
    server = HospitalChatbotServer(args.host, args.port)
    server.start()

if __name__ == "__main__":
    main()
