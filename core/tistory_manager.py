import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


class TistoryManager:
    """티스토리 관리 클래스"""

    def __init__(self, use_profile=False):  # 배포용 기본값 False
        self.driver = None
        self.is_logged_in = False
        self.use_profile = use_profile

    def setup_driver(self, use_profile=False):  # 배포시 기본값을 False로 변경
        """Chrome 드라이버 설정 - 배포용 최적화"""
        try:
            chrome_options = Options()
            
            # 배포용 안정성 옵션
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            
            # 메모리 최적화
            chrome_options.add_argument("--memory-pressure-off")
            chrome_options.add_argument("--max_old_space_size=4096")
            
            # 1순위: webdriver-manager로 자동 다운로드 (배포용 최적)
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Chrome 드라이버 자동 설정 완료")
                return True
            except Exception as e:
                print(f"⚠️ 자동 설정 실패: {e}")
    
            # 2순위: 시스템 Chrome 사용
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✅ 시스템 Chrome 사용 성공")
                return True
            except Exception as e:
                print(f"⚠️ 시스템 Chrome 실패: {e}")
    
            # 실패 시 안내
            print("❌ Chrome 브라우저를 찾을 수 없습니다.")
            print("💡 Chrome 브라우저를 설치해주세요: https://www.google.com/chrome/")
            return False
    
        except Exception as e:
            print(f"드라이버 설정 오류: {e}")
            return False

    def open_tistory_login(self):
        """티스토리 로그인 페이지 열기"""
        try:
            if not self.driver:
                if not self.setup_driver(self.use_profile):
                    return False

            self.driver.get("https://www.tistory.com/auth/login")
            return True
        except Exception as e:
            print(f"로그인 페이지 열기 오류: {e}")
            return False

    def go_to_write_page(self):
        initial_window_count = len(self.driver.window_handles)

        # 글쓰기 버튼 클릭 해 글 작성 페이지로 이동
        try:
            print("📝 글쓰기 버튼 찾는 중...")
            write_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".wrap_link .link_tab")
            if write_buttons:
                # 첫 번째 버튼이 글쓰기 버튼
                write_button = write_buttons[0]
                print("📝 글쓰기 버튼 발견, 클릭 중...")
                write_button.click()
                
                WebDriverWait(self.driver, 10).until(
                    lambda driver: len(driver.window_handles) > initial_window_count
                )
                
                new_window = self.driver.window_handles[-1]
                self.driver.switch_to.window(new_window)
                
                print("✅ 글쓰기 페이지로 이동 완료")
            else:
                print("⚠️ 글쓰기 버튼을 찾을 수 없습니다.")
                return False
        except Exception as e:
            print("⚠️ 글쓰기 버튼을 찾을 수 없습니다.")
            return False
        
        try:
            # 알림창이 있는지 확인
            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            print("⚠️ 알림창 발견, 닫는 중...")
            # 알림창 닫기
            alert.dismiss()
            print("✅ 알림창 닫기 완료")
        except Exception as e:
            print("ℹ️ 알림창 없음, 계속 진행합니다.")
            pass

        return True

    def write_post(self, title, content, category=""):
        """글 작성 - 자동 입력 시도 후 수동 안내"""
        print(f"📝 글 작성 시작: {title}")
        
        # 제목 입력 시도
        title_input = None
        try:
            title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#post-title-inp"))
            )
            print("✅ 제목 필드 발견: #post-title-inp")
        except Exception as e:
            print(f"⚠️ 제목 필드 찾기 실패: {e}")
            return
        
        if title_input:
            title_input.clear()
            title_input.send_keys(title)
            print("✅ 제목 입력 완료")
        else:
            print("⚠️ 제목 입력 필드를 찾을 수 없습니다.")
            return
        
        # 내용 입력 시도
        try:
            codemirror_container = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "CodeMirror-line"))
            )
            
            # ActionChains를 생성
            actions = ActionChains(self.driver)
            
            # 에디터를 클릭해서 포커스를 맞추고, 바로 텍스트를 입력
            actions.move_to_element(codemirror_container)
            actions.click()                              
            actions.send_keys(content)                   
            actions.perform()
            
            print("✅ CodeMirror 에디터 내용 입력 성공")
            
        except Exception as editor_error:
            print(f"⚠️ 마크다운 에디터 처리 중 오류: {str(editor_error)}")
            return False

        return True


    def publish_post(self, date: str = None, hour: int = None, minute: int = None):
        # 완료 버튼 클릭
        print("🚀 발행 시도 중...")
        try:
            # 완료 버튼
            complete_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish-layer-btn"))
            )
            complete_button.click()
            print("✅ 완료 버튼 클릭 완료!")
            time.sleep(2)
            
        except Exception as e:
            print(f"⚠️ 자동 발행 실패: {e}")
            print("📱 수동으로 발행 버튼을 클릭하세요.")
            return False
        
        # 공개 설정
        try:
            # 팝업 내 공개 설정 영역 찾기
            popup_items = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".info_editor.info_editor_type2 .inp_item"))
            )

            if len(popup_items) >= 1:
                # 첫 번째 항목이 공개 설정
                open_radio = WebDriverWait(popup_items[0], 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#open20"))
                )
                open_radio.click()
                print("✅ 공개 설정 완료!")

            time.sleep(1)

            popup_items = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".info_editor.info_editor_type2 .inp_item"))
            )

            # 발행일 설정
            if len(popup_items) >= 3:
                date_button = popup_items[4].find_element(By.TAG_NAME, "button")
                date_button.click()

        except Exception as e:
            print(f"⚠️ 공개 설정 실패: {e}")
        
        try:
            # 날짜 파싱 (YYYY-MM-DD 형식)
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                raise ValueError("날짜 형식 오류: YYYY-MM-DD 형식으로 입력해주세요")
            
            year, month, day = map(int, date.split('-'))
            
            print(f"예약 날짜: {year}년 {month}월 {day}일 {hour}시 {minute}분")

            # 1. 예약 버튼 클릭
            reserve_btn = self.driver.find_element(By.CSS_SELECTOR, ".btn_reserve")
            reserve_btn.click()
            
            # 2. 캘린더 로딩 대기
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tbl_calendar")))
            
            # 3. 원하는 년월까지 이동
            while True:
                current_text = self.driver.find_element(By.CSS_SELECTOR, ".txt_calendar").text.strip()
                cur_year, cur_month = current_text.replace("년", "").replace("월", "").split()
                cur_year, cur_month = int(cur_year), int(cur_month)
                print(f"현재 캘린더: {cur_year}년 {cur_month}월")
                
                if cur_year == year and cur_month == month:
                    break
                
                time.sleep(1)
                self.driver.find_element(By.CSS_SELECTOR, ".btn_next").click()
            
            # 4. 원하는 일자 클릭
            day_btn = self.driver.find_element(By.XPATH, f"//button[@class='btn_day' and text()='{day}']")
            day_btn.click()
            
            # 5. 시간 설정
            hour_input = self.driver.find_element(By.ID, "dateHour")
            hour_input.clear()
            hour_input.send_keys(str(max(0, min(23, hour))))
            
            minute_input = self.driver.find_element(By.ID, "dateMinute")
            minute_input.clear()
            minute_input.send_keys(str(max(0, min(59, minute))))
            
            print(f"✅ 발행일 설정 완료: {date} {hour}:{minute}")
            time.sleep(1)

        except Exception as e:
            print(f"⚠️ 발행일 설정 실패: {e}")

        # 공개 발행 버튼 클릭
        try:
            publish_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish-btn"))
            )
            publish_button.click()
            print("✅ 발행 버튼 클릭 완료!")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"⚠️ 최종 발행 버튼 클릭 실패: {e}")

    def close_driver(self):
        """드라이버 종료"""
        if self.driver and self.driver != "default_browser":
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False