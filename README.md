# LeaveMaster

LeaveMaster是一個使用Selenium和Tesseract OCR自動化請假流程的腳本。該腳本自動登錄請假系統，輸入驗證碼並提交請假申請。

## 特點
- 自動輸入學號和密碼
- 自動識別並輸入驗證碼
- 自動提交請假申請

## 先決條件
- Python 3.x
- Selenium
- OpenCV
- Tesseract OCR

## 安裝

1. 安裝Python 3.x
2. 安裝所需的Python庫:
    ```bash
    pip install selenium opencv-python pytesseract
    ```
3. 下載並安裝對應瀏覽器的WebDriver（例如[ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/))

## 使用方法

1. 克隆此倉庫到你的本地機器
    ```bash
    git clone https://github.com/yourusername/leavemaster.git
    cd leavemaster
    ```
2. 修改腳本中的學號、密碼和請假理由
    ```python
    driver.find_element(By.NAME, 'student_id').send_keys('your_student_id')
    driver.find_element(By.NAME, 'password').send_keys('your_password')
    # 如果需要輸入請假理由，請在此處添加相應代碼
    ```
3. 執行腳本
    ```bash
    python script.py
    ```

## 注意事項

- 確保你擁有合法權限來自動化處理這些請假申請，因為這可能違反某些網站的使用條款。
- 如果驗證碼識別不準確，可能需要進一步調整圖像處理的參數。

## 貢獻

歡迎貢獻！請先fork此倉庫，創建一個新的分支進行修改，並提交pull request。

## 授權

此項目基於MIT許可證，詳見[LICENSE](LICENSE)文件。