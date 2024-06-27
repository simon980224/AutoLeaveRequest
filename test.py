import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import cv2
import pytesseract

def init_webdriver(chrome_driver_path):
    """初始化WebDriver"""
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def recognize_captcha(image_path):
    """使用OpenCV和Tesseract進行驗證碼識別"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 轉為灰階
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)  # 二值化
    captcha_text = pytesseract.image_to_string(binary, config='--psm 7').strip()
    return captcha_text

def login(driver, wait, user_id, password, captcha_path, max_retries):
    """執行登入流程"""
    retries = 0
    while retries < max_retries:
        try:
            wait = WebDriverWait(driver, 10)
            # 選擇身分別
            identity_select = wait.until(EC.presence_of_element_located((By.ID, 'Type')))
            identity_select.send_keys('學生')  # 根據需要選擇身分別

            # 輸入使用者ID
            user_id_input = wait.until(EC.presence_of_element_located((By.ID, 'UserID')))
            user_id_input.clear()
            user_id_input.send_keys(user_id)

            # 輸入密碼
            password_input = wait.until(EC.presence_of_element_located((By.ID, 'PWD')))
            password_input.clear()
            password_input.send_keys(password)

            # 找到驗證碼圖片
            captcha_image_element = wait.until(EC.presence_of_element_located((By.XPATH, '//img[@src="/HttpRequest/MakeCheckCodePIC.ashx"]')))
            captcha_image_path = os.path.join(captcha_path, f'captcha_{int(time.time())}.png')
            captcha_image_element.screenshot(captcha_image_path)

            # 識別驗證碼
            captcha_text = recognize_captcha(captcha_image_path)

            # 刪除舊的驗證碼圖片
            os.remove(captcha_image_path)

            # 輸入驗證碼
            captcha_input = wait.until(EC.presence_of_element_located((By.ID, 'CheckCode')))
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)

            # 點擊登入按鈕
            login_button = wait.until(EC.element_to_be_clickable((By.ID, 'Client_Login')))
            login_button.click()

            # 等待頁面跳轉（根據具體情況調整）
            wait.until(EC.url_contains('https://ntcbadm1.ntub.edu.tw/Portal/indexSTD.aspx'))

            # 檢查是否顯示系統維護信息
            try:
                maintenance_message = driver.find_element(By.XPATH, '//*[contains(text(), "系統維護")]')
                if maintenance_message:
                    return False
            except:
                pass

            # 驗證是否登入成功（檢查當前URL）
            if driver.current_url == 'https://ntcbadm1.ntub.edu.tw/Portal/indexSTD.aspx':
                return True
            else:
                retries += 1
        except Exception as e:
            retries += 1

    return False

def get_absence_record(driver):
    """檢查曠課紀錄"""
    try:
        driver.get('https://ntcbadm1.ntub.edu.tw/StdAff/STDWeb/ABS_SearchSACP.aspx')
        
        # 等待表格加載
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_GRD')))
        
        # 獲取第一筆資料
        if len(rows := table.find_elements(By.TAG_NAME, 'tr')) > 1:
            cells = rows[1].find_elements(By.TAG_NAME, 'td')
            record = [cell.text for cell in cells]
            if record[0] == '曠課':
                return record
        else:
            return None
    except Exception as e:
        return None

def absence_record_page(driver):
    """轉跳請假頁面"""
    try:
        driver.get('https://ntcbadm1.ntub.edu.tw/StdAff/STDWeb/ABS0101.aspx')
    except Exception as e:
        pass

def fill_leave_form(driver, record):
    """新增請假表單"""
    try:
        wait = WebDriverWait(driver, 10)
        # 等待新增按鈕出現並點擊
        add_button = wait.until(EC.element_to_be_clickable((By.ID, 'REC_Insert')))
        add_button.click()
        
        # 切換到iframe
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'TB_iframeContent')))

        # 填寫表單
        # 請假日期
        start_date_input = wait.until(EC.presence_of_element_located((By.ID, 'SEA_SDate')))
        end_date_input = driver.find_element(By.ID, 'SEA_EDate')
        start_date_input.clear()
        start_date_input.send_keys(record[1])
        # 學校js有自動填寫
        # end_date_input.clear()
        # end_date_input.send_keys(record[1])

        # 請假類別
        department_select = driver.find_element(By.ID, 'SEA_DN')
        department_select.send_keys('進修推廣部')
        holiday_select = driver.find_element(By.ID, 'SEA_Holiday')
        holiday_select.send_keys('事假')

        # 請假節次
        sections = record[3].split(',')
        for section in sections:
            section_checkbox = driver.find_element(By.ID, f'SEA_Section_{section.strip()}')
            if not section_checkbox.is_selected():
                section_checkbox.click()

        # 請假事由
        reason_input = driver.find_element(By.ID, 'SEA_Note')
        reason_input.clear()
        reason_input.send_keys('公司加班')
        
    except Exception as e:
        pass

def main():
    # 配置ChromeDriver的路徑
    chrome_driver_path = '/Users/chenyaoxuan/Desktop/chromedriver'
    # 最大重試次數
    MAX_RETRIES = 3
    
    captcha_path = '/Users/chenyaoxuan/Downloads'
    driver = init_webdriver(chrome_driver_path)
    driver.get('https://ntcbadm1.ntub.edu.tw/login.aspx')  # 替換為你的登入頁面URL
    wait = WebDriverWait(driver, 10)

    try:
        if login(driver, wait, user_id='n1116441', password='ee25393887', captcha_path=captcha_path, max_retries=MAX_RETRIES):
            # 登入成功後檢查曠課紀錄
            first_absence_record = get_absence_record(driver)
            if first_absence_record:
                # 轉跳到請假網站
                absence_record_page(driver)
                # 填寫請假表單
                fill_leave_form(driver, first_absence_record)
                # 等待3秒，以便觀察結果
                time.sleep(3)  
                print("假單填寫完畢")
            else:
                print("沒有曠課紀錄")
        else:
            # 登入失敗後的操作
            print("登入失敗，無法檢查曠課紀錄。")
    finally:
        # 關閉瀏覽器
        driver.quit()

if __name__ == "__main__":
    main()