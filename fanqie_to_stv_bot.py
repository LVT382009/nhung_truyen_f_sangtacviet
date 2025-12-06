import time
import os 
import re 
import msvcrt 
import urllib.parse 
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib3.exceptions import ReadTimeoutError
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException

# Cấu hình Mặc định
FANQIE_DEFAULT_TEMPLATE = "https://fanqienovel.com/library/audience1-cat2-19-stat1-count0/page_{}?sort=newest"
SANGTACVIET_URL = "https://sangtacviet.app/"
SCROLL_TIMES = 3  

# --- CẤU HÌNH ĐƯỜNG DẪN FILE LỊCH SỬ ---
HISTORY_DIR = r"D:\nhúng truyện fanqie, qidian,qimao"
HISTORY_FILE = os.path.join(HISTORY_DIR, "da_lam_xong.txt")

# --- CẤU HÌNH TÀI KHOẢN ---
STV_USERNAME = "YOUR_USERNAME_HERE" 
STV_PASSWORD = "YOUR_PASSWORD_HERE"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    options.set_capability("pageLoadStrategy", "eager")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.set_page_load_timeout(10) 
    driver.set_script_timeout(10)
    return driver

def get_book_id(url):
    if not url: return None
    match = re.search(r'/page/(\d+)', url)
    if match: return match.group(1)
    return None

def ensure_history_dir():
    if not os.path.exists(HISTORY_DIR):
        try: os.makedirs(HISTORY_DIR)
        except: pass

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    ids = set()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip(): ids.add(line.strip())
    except: pass
    return ids

def save_history(book_id):
    if not book_id: return
    ensure_history_dir()
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(book_id + "\n")
    except: pass

def check_is_recent(text_content):
    """
    Kiểm tra xem truyện có mới cập nhật trong vòng 2 ngày không.
    Trả về: True (Mới), False (Cũ)
    """
    if not text_content: return True # Không check được thì cứ lấy cho chắc
    
    # Các từ khóa tiếng Trung thường gặp trên Fanqie
    # 刚刚(vừa xong), 分钟(phút), 小时(giờ) -> Chắc chắn mới
    if any(k in text_content for k in ["刚刚", "分钟", "小时", "Just now", "minutes", "hours"]):
        return True
    
    # Hôm qua (昨天), Hôm kia (前天) -> Chắc chắn mới (<= 2 ngày)
    if any(k in text_content for k in ["昨天", "前天", "Yesterday", "day before"]):
        return True
    
    # X ngày trước (X天前)
    # Tìm số ngày
    day_match = re.search(r'(\d+)\s*(天前|days ago)', text_content)
    if day_match:
        days = int(day_match.group(1))
        if days <= 2:
            return True
        else:
            print(f"-> Truyện cũ: {days} ngày trước (> 2 ngày)")
            return False

    # Kiểm tra ngày tháng cụ thể (YYYY-MM-DD)
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text_content)
    if date_match:
        try:
            date_str = date_match.group(0)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            delta = datetime.now() - date_obj
            if delta.days <= 2:
                return True
            else:
                print(f"-> Truyện cũ: {date_str} ({delta.days} ngày trước)")
                return False
        except: pass

    # Mặc định trả về True nếu không tìm thấy thông tin ngày (để tránh bỏ sót)
    return True

def login_to_stv(driver, wait):
    print("--- Đang truy cập Sangtacviet ---")
    try:
        driver.set_page_load_timeout(30)
        driver.get(SANGTACVIET_URL)
        try:
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Đăng nhập')] | //button[contains(text(), 'Đăng nhập')]")))
            login_btn.click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='username']"))).send_keys(STV_USERNAME)
            driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(STV_PASSWORD)
            
            submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], div.modal-footer button")
            if not submit: submit = driver.find_element(By.XPATH, "//button[contains(text(), 'Đăng nhập')]")
            submit.click()
            print(f"-> Đã gửi đăng nhập: {STV_USERNAME}")
            time.sleep(2)
        except:
            print("-> Đã đăng nhập hoặc không thấy nút.")
    except Exception as e:
        print(f"!! Lỗi login: {e}")

def reset_stv_tab(driver, original_window):
    try:
        if len(driver.window_handles) > 1: driver.close()
    except: pass
    driver.switch_to.window(original_window)
    driver.switch_to.new_window('tab')
    driver.set_page_load_timeout(5)
    try:
        driver.get(SANGTACVIET_URL)
        return True
    except:
        return False

def run_automation(driver, wait, custom_url=None):
    processed_ids = load_history()
    print(f"\n[*] Lịch sử: {len(processed_ids)} ID.")

    url_template = None
    current_page = 1
    single_page_mode = False 

    if custom_url:
        match = re.search(r'page_(\d+)', custom_url)
        if match:
            current_page = int(match.group(1)) 
            url_template = custom_url.replace(f"page_{current_page}", "page_{}")
        else:
            single_page_mode = True
    else:
        url_template = FANQIE_DEFAULT_TEMPLATE
        current_page = 1

    stop_scan_completely = False # Cờ để dừng toàn bộ tool khi gặp truyện cũ

    while True:
        if stop_scan_completely:
            print("\n[STOP] Đã gặp truyện cũ quá 2 ngày. Dừng quét.")
            break

        if single_page_mode: target_url = custom_url
        else: target_url = url_template.format(current_page)

        print(f"\n==================================================")
        print(f"[*] QUÉT TRANG: {current_page if not single_page_mode else 'Custom/Search'}")
        
        # 1. QUÉT FANQIE
        try:
            driver.set_page_load_timeout(20) 
            driver.get(target_url)
            time.sleep(1.5) 
            for i in range(SCROLL_TIMES):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)

            # Lấy tất cả các thẻ link truyện
            story_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/page/']")
            new_books = []
            
            for elem in story_elements:
                raw_href = elem.get_attribute('href')
                if raw_href and "fanqienovel.com/page/" in raw_href:
                    book_id = get_book_id(raw_href)
                    if book_id and book_id not in processed_ids:
                        if not any(item[0] == book_id for item in new_books):
                            
                            # --- KIỂM TRA NGÀY CẬP NHẬT ---
                            # Lấy nội dung text của thẻ chứa (thường là cha của thẻ a hoặc thẻ a)
                            # Fanqie thường để thông tin update ngay bên cạnh hoặc trong thẻ cha
                            try:
                                # Lấy text của thẻ cha bao quanh link để tìm thông tin ngày
                                book_text = elem.find_element(By.XPATH, "./../..").text
                            except:
                                book_text = elem.text # Fallback
                            
                            if check_is_recent(book_text):
                                new_books.append((book_id, raw_href))
                            else:
                                # Nếu gặp truyện cũ (> 2 ngày) và đang sort=newest
                                # Thì tất cả truyện sau đó cũng cũ -> DỪNG LUÔN
                                if "sort=newest" in target_url or not custom_url:
                                    print(f"-> Phát hiện truyện cũ ID {book_id}. Dừng quét vì danh sách đã hết truyện mới.")
                                    stop_scan_completely = True
                                    break
                                # Nếu không phải sort=newest thì chỉ bỏ qua truyện này thôi
        
        except Exception as e:
            print(f"[!] Lỗi quét Fanqie: {e}. Thử lại...")
            continue

        if not new_books:
            if stop_scan_completely: break
            print(f"[!] Không có truyện mới (hoặc đã làm hết) ở trang này.")
            if single_page_mode: break
            else:
                current_page += 1
                if current_page > 1000:
                    print("\n[LOOP] Quay về trang 1...")
                    current_page = 1
                continue

        print(f"[+] Tìm thấy {len(new_books)} truyện MỚI (<= 2 ngày).")

        # 2. XỬ LÝ SANGTACVIET
        print("=> Bắt đầu nhúng (Nhấn 'q' để DỪNG)...")
        original_window = driver.current_window_handle
        
        driver.switch_to.new_window('tab')
        try:
            driver.set_page_load_timeout(5)
            driver.get(SANGTACVIET_URL)
        except: pass

        stop_requested = False

        for index, (book_id, link) in enumerate(new_books):
            if msvcrt.kbhit() and msvcrt.getch().lower() == b'q':
                print("\n[!!!] Đã nhận lệnh DỪNG.")
                stop_requested = True
                break
            
            if book_id in processed_ids: continue

            print(f"ID: {book_id} | ", end='')
            
            try:
                driver.set_page_load_timeout(5)
                driver.set_script_timeout(5)
                
                wait_short = WebDriverWait(driver, 3)
                search_box = wait_short.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
                search_box.clear()
                try: 
                    search_box.send_keys(Keys.CONTROL + "a")
                    search_box.send_keys(Keys.DELETE)
                except: pass
                
                search_box.send_keys(link)
                search_box.send_keys(Keys.ENTER)
                
                save_history(book_id)
                processed_ids.add(book_id)
                print("OK.")

            except (TimeoutException, ReadTimeoutError, WebDriverException, Exception) as e:
                print(f"Lỗi/Lag -> Reset Tab & SKIP.")
                reset_stv_tab(driver, original_window)

        try:
            if len(driver.window_handles) > 1: driver.close()
            driver.switch_to.window(original_window)
        except:
            driver.switch_to.window(driver.window_handles[0])
        
        if stop_requested: break
        if stop_scan_completely: break
            
        print(f"\n[DONE] Xong trang.")
        
        if single_page_mode: break 
        else: 
            current_page += 1
            if current_page > 1000: current_page = 1

def main():
    driver = None
    wait = None
    ensure_history_dir()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n================ MENU TOOL NHÚNG TRUYỆN ================")
        print("1. Mở Sangtacviet")
        print("2. Chạy Auto (Mặc định: Fanqie)")
        print("3. Chạy Auto (Nhập link)")
        print("4. Chạy Auto (Tìm theo từ khóa)")
        print("5. Xem tổng số ID đã làm")
        print("6. Thoát")
        
        choice = input("Chọn chức năng (1-6): ").strip()
        
        if choice in ['1', '2', '3', '4']:
            if driver is None:
                print("\n[*] Khởi động Chrome...")
                try:
                    driver = setup_driver()
                    wait = WebDriverWait(driver, 10)
                except Exception as e:
                    print(f"Lỗi: {e}")
                    input("Enter để thử lại...")
                    continue

            if choice == '1':
                login_to_stv(driver, wait)
                input("\n-> Enter về Menu...")
            elif choice == '2':
                run_automation(driver, wait, custom_url=None)
                input("\n-> Enter về Menu...")
            elif choice == '3':
                lnk = input("\nLink Fanqie: ").strip()
                if lnk: run_automation(driver, wait, custom_url=lnk)
                input("\n-> Enter về Menu...")
            elif choice == '4':
                keyword = input("\nNhập từ khóa (Ví dụ: hệ thống, system...): ").strip()
                if keyword:
                    search_url = f"https://fanqienovel.com/search?q={urllib.parse.quote(keyword)}"
                    print(f"-> Đang tìm kiếm: {search_url}")
                    run_automation(driver, wait, custom_url=search_url)
                input("\n-> Enter về Menu...")

        elif choice == '5':
            current_ids = load_history()
            print(f"\n[INFO] Tổng số ID đã lưu: {len(current_ids)}")
            input("\n-> Nhấn Enter để quay lại Menu...")
        
        elif choice == '6':
            if driver: 
                try: driver.quit()
                except: pass
            break
        else: time.sleep(1)

if __name__ == "__main__":
    main()