from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import cv2
import pytesseract
import random

# 配置ChromeDriver的路徑
chrome_driver_path = '/Users/chenyaoxuan/Desktop/chromedriver'

# 最大重試次數
MAX_RETRIES = 3

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

def login(driver, wait, user_id, password):
    """執行登入流程"""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # 選擇身分別
            identity_select = wait.until(EC.presence_of_element_located((By.ID, 'Type')))
            identity_select.send_keys('學生')  # 根據需要選擇身分別

            # 隨機等待1到3秒
            time.sleep(random.uniform(1, 3))

            # 輸入使用者ID
            user_id_input = wait.until(EC.presence_of_element_located((By.ID, 'UserID')))
            user_id_input.send_keys(user_id)

            # 隨機等待1到3秒
            time.sleep(random.uniform(1, 3))

            # 輸入密碼
            password_input = wait.until(EC.presence_of_element_located((By.ID, 'PWD')))
            password_input.send_keys(password)

            # 隨機等待1到3秒
            time.sleep(random.uniform(1, 3))

            # 找到驗證碼圖片
            captcha_image_element = wait.until(EC.presence_of_element_located((By.XPATH, '//img[@src="/HttpRequest/MakeCheckCodePIC.ashx"]')))
            captcha_image_path = '/Users/chenyaoxuan/Downloads/captcha.png'
            captcha_image_element.screenshot(captcha_image_path)

            # 隨機等待1到3秒
            time.sleep(random.uniform(1, 3))

            # 識別驗證碼
            captcha_text = recognize_captcha(captcha_image_path)
            print("識別出的驗證碼是:", captcha_text)

            # 隨機等待1到3秒
            time.sleep(random.uniform(1, 3))

            # 輸入驗證碼
            captcha_input = wait.until(EC.presence_of_element_located((By.ID, 'CheckCode')))
            captcha_input.send_keys(captcha_text)

            # 隨機等待1到3秒
            time.sleep(random.uniform(1, 3))

            # 點擊登入按鈕
            login_button = wait.until(EC.element_to_be_clickable((By.ID, 'Client_Login')))
            login_button.click()

            # 等待頁面跳轉（根據具體情況調整）
            time.sleep(5)

            # 檢查是否顯示系統維護信息
            try:
                maintenance_message = driver.find_element(By.XPATH, '//*[contains(text(), "系統維護")]')
                if maintenance_message:
                    print("系統維護中，請稍後再試。")
                    return False
            except:
                pass

            # 驗證是否登入成功（根據具體情況調整）
            success_element = driver.find_element(By.XPATH, 'YOUR_SUCCESS_ELEMENT_XPATH')
            if success_element:
                print("登入成功！")
                return True
            else:
                print("登入失敗，重試中...")
                retries += 1
        except Exception as e:
            print(f"登入過程中出現錯誤: {e}")
            retries += 1

    print("達到最大重試次數，登入失敗。")
    return False

def main():
    driver = init_webdriver(chrome_driver_path)
    driver.get('https://ntcbadm1.ntub.edu.tw/login.aspx')  # 替換為你的登入頁面URL
    wait = WebDriverWait(driver, 10)

    try:
        if login(driver, wait, user_id='n1116441', password='ee25393887'):
            # 登入成功後的操作
            pass
        else:
            # 登入失敗後的操作
            pass
    finally:
        # 關閉瀏覽器
        driver.quit()

if __name__ == "__main__":
    main()