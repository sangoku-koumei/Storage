
import time
import random
import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# KEYWORDS: [Stealth_Engine, Selenium, Undetected_Chrome, Human_Mimicry, Note_Poster]
# DESCRIPTION: Note.comへのステルス投稿を担う中核エンジン。ブラウザ自動操作の検知を回避し、人間らしい挙動で記事と画像を自動投稿する。

class NoteStealthPoster:
    def __init__(self, headless=False):
        self.options = uc.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.driver = None

    def start_driver(self):
        """Start the undetected-chromedriver"""
        self.driver = uc.Chrome(options=self.options)
        self.driver.maximize_window()

    def human_delay(self, min_sec=3, max_sec=15):
        """Inject random jitter to appear human"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def is_safe_time(self):
        """Check if current time is within 07:00 - 02:00 (Safe working hours)"""
        now = datetime.datetime.now().time()
        start = datetime.time(7, 0)
        end = datetime.time(2, 0)
        
        # If end is smaller than start, it means it crosses midnight
        if start <= end:
            return start <= now <= end
        else:
            return now >= start or now <= end

    def login(self, email, password):
        """Simulate human login process"""
        if not self.driver: self.start_driver()
        
        self.driver.get("https://note.com/login")
        self.human_delay(5, 10)
        
        # Note login fields (Selectors might need maintenance)
        try:
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "mail_address"))
            )
            email_field.send_keys(email)
            self.human_delay(1, 3)
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            self.human_delay(2, 4)
            
            # Submit
            # login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
            # Using CSS selector for more stability if text changes
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button.m-form__submit")
            login_button.click()
            self.human_delay(5, 8)
            return True
        except Exception as e:
            print(f"Login Failed: {e}")
            return False

    def post_note_rich(self, title, body, image_dir=None):
        """Post a note with rich blocks (paragraphs and images)"""
        if not self.driver: return False
        if not self.is_safe_time():
            print("Night shutdown active.")
            return False

        try:
            self.driver.get("https://note.com/publish")
            self.human_delay(5, 10)
            
            # Title
            title_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.m-noteEditHeadline__title"))
            )
            title_area.send_keys(title)
            self.human_delay(3, 5)

            # Split body into blocks (paragraphs and image placeholders)
            # Placeholder format: [IMAGE:filename.jpg]
            import re
            blocks = re.split(r'(\[IMAGE:[^\]]+\])', body)
            
            # Focus the editor
            editor = self.driver.find_element(By.ID, "note-editor")
            editor.click()
            self.human_delay(1, 2)

            for block in blocks:
                block = block.strip()
                if not block: continue
                
                img_match = re.match(r'\[IMAGE:([^\]]+)\]', block)
                if img_match and image_dir:
                    # Image insertion logic
                    img_name = img_match.group(1)
                    img_path = os.path.join(image_dir, img_name)
                    
                    if os.path.exists(img_path):
                        print(f"Uploading image: {img_path}")
                        # 1. Click "+" menu (Add block)
                        plus_btn = self.driver.find_element(By.CSS_SELECTOR, "button.m-noteEdit__add")
                        plus_btn.click()
                        self.human_delay(1, 2)
                        
                        # 2. Click Image icon (Usually the first one in the popover)
                        img_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept='image/*']")
                        img_input.send_keys(img_path)
                        self.human_delay(10, 20) # Wait for upload
                else:
                    # Paragraph / Heading / List insertion logic
                    # Basic Markdown-like support: Detect headings and bullet points
                    if block.startswith("## "):
                        # Convert to H2 (Note usually does this if you type "## " but send_keys is fast)
                        # We'll just send it and hope Note's editor handles it, or just send the text
                        editor.send_keys(block)
                    elif block.startswith("### "):
                        editor.send_keys(block)
                    elif block.startswith("- ") or block.startswith("* "):
                        editor.send_keys(block)
                    else:
                        editor.send_keys(block)
                    
                    editor.send_keys("\n\n")
                    self.human_delay(2, 5)

            # Click Publish
            publish_btn = self.driver.find_element(By.CSS_SELECTOR, "button.m-noteEdit__publish")
            publish_btn.click()
            self.human_delay(5, 8)
            return True
            
        except Exception as e:
            print(f"Rich Posting Failed: {e}")
            return False

    def quit(self):
        if self.driver:
            self.driver.quit()
