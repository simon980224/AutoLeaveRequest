import logging
import os
import time
from datetime import datetime

import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 配置日誌
log_path = '/Users/chenyaoxuan/Downloads/automation.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_path, filemode='a')

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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    captcha_text = pytesseract.image_to_string(binary, config='--psm 7').strip()
    return captcha_text

def login(driver, wait, user_id, password, captcha_path, max_retries):
    """執行登入流程"""
    retries = 0
    while retries < max_retries:
        try:
            identity_select = wait.until(EC.presence_of_element_located((By.ID, 'Type')))
            identity_select.send_keys('學生')  # 根據需要選擇身分別

            user_id_input = wait.until(EC.presence_of_element_located((By.ID, 'UserID')))
            user_id_input.clear()
            user_id_input.send_keys(user_id)

            password_input = wait.until(EC.presence_of_element_located((By.ID, 'PWD')))
            password_input.clear()
            password_input.send_keys(password)

            captcha_image_element = wait.until(EC.presence_of_element_located((By.XPATH, '//img[@src="/HttpRequest/MakeCheckCodePIC.ashx"]')))
            captcha_image_path = os.path.join(captcha_path, f'captcha_{int(time.time())}.png')
            captcha_image_element.screenshot(captcha_image_path)

            captcha_text = recognize_captcha(captcha_image_path)
            os.remove(captcha_image_path)

            captcha_input = wait.until(EC.presence_of_element_located((By.ID, 'CheckCode')))
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)

            login_button = wait.until(EC.element_to_be_clickable((By.ID, 'Client_Login')))
            login_button.click()

            wait.until(EC.url_contains('https://ntcbadm1.ntub.edu.tw/Portal/indexSTD.aspx'))

            try:
                maintenance_message = driver.find_element(By.XPATH, '//*[contains(text(), "系統維護")]')
                if maintenance_message:
                    return False
            except:
                pass

            if driver.current_url == 'https://ntcbadm1.ntub.edu.tw/Portal/indexSTD.aspx':
                return True
            else:
                retries += 1
        except Exception as e:
            logging.error(f"登入過程中出現錯誤: {e}")
            retries += 1

    return False

def get_absence_record(driver, wait):
    """檢查曠課紀錄"""
    try:
        driver.get('https://ntcbadm1.ntub.edu.tw/StdAff/STDWeb/ABS_SearchSACP.aspx')
        table = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_GRD')))
        
        if len(rows := table.find_elements(By.TAG_NAME, 'tr')) > 1:
            cells = rows[1].find_elements(By.TAG_NAME, 'td')
            record = [cell.text for cell in cells]
            if record[0] == '曠課':
                return record
        else:
            return None
    except Exception as e:
        logging.error(f"檢查曠課紀錄過程中出現錯誤: {e}")
        return None

def absence_record_page(driver):
    """轉跳請假頁面"""
    try:
        driver.get('https://ntcbadm1.ntub.edu.tw/StdAff/STDWeb/ABS0101.aspx')
    except Exception as e:
        logging.error(f"轉跳請假頁面過程中出現錯誤: {e}")

def fill_leave_form(driver, wait, record):
    """新增請假表單"""
    try:
        add_button = wait.until(EC.element_to_be_clickable((By.ID, 'REC_Insert')))
        add_button.click()
        
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'TB_iframeContent')))

        start_date_input = wait.until(EC.presence_of_element_located((By.ID, 'SEA_SDate')))
        start_date_input.clear()
        start_date_input.send_keys(record[1])

        department_select = driver.find_element(By.ID, 'SEA_DN')
        department_select.send_keys('進修推廣部')
        holiday_select = driver.find_element(By.ID, 'SEA_Holiday')
        holiday_select.send_keys('事假')

        sections = record[3].split(',')
        for section in sections:
            section_checkbox = driver.find_element(By.ID, f'SEA_Section_{section.strip()}')
            if not section_checkbox.is_selected():
                section_checkbox.click()

        reason_input = driver.find_element(By.ID, 'SEA_Note')
        reason_input.clear()
        reason_input.send_keys('公司加班')
    except Exception as e:
        logging.error(f"填寫請假表單過程中出現錯誤: {e}")

def main():
    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', '/Users/chenyaoxuan/Desktop/chromedriver')
    MAX_RETRIES = 3
    captcha_path = os.getenv('CAPTCHA_PATH', '/Users/chenyaoxuan/Downloads')
    
    user_id = os.getenv('USER_ID', 'n1116441')
    password = os.getenv('PASSWORD', 'ee25393887')
    
    driver = init_webdriver(chrome_driver_path)
    driver.get('https://ntcbadm1.ntub.edu.tw/login.aspx')
    wait = WebDriverWait(driver, 10)

    start_time = datetime.now()
    logging.info(f"執行時間: {start_time}")

    try:
        if login(driver, wait, user_id=user_id, password=password, captcha_path=captcha_path, max_retries=MAX_RETRIES):
            first_absence_record = get_absence_record(driver, wait)
            if first_absence_record:
                absence_record_page(driver)
                fill_leave_form(driver, wait, first_absence_record)
                success = True
                send_content = first_absence_record
            else:
                logging.info("沒有曠課紀錄")
                success = False
                send_content = "沒有曠課紀錄"
        else:
            logging.error("登入失敗。")
            success = False
            send_content = "登入失敗"
    finally:
        driver.quit()
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logging.info(f"送出時間: {end_time}")
        logging.info(f"運行時間: {elapsed_time} 秒")
        logging.info(f"送出內容: {send_content}")
        logging.info(f"成功與否: {'成功' if success else '失敗'}")
        logging.info('-' * 50)

if __name__ == "__main__":
    main()