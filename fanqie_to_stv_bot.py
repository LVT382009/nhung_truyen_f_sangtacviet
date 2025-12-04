import time
import os 
import re 
import msvcrt 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib3.exceptions import ReadTimeoutError # Thêm thư viện xử lý lỗi mạng

# Cấu hình Mặc định
FANQIE_DEFAULT_TEMPLATE = "https://fanqienovel.com/library/audience1-cat2-19-stat1-count0/page_{}?sort=newest"
SANGTACVIET_URL = "https://sangtacviet.app/"
SCROLL_TIMES = 3  

# --- CẤU HÌNH ĐƯỜNG DẪN FILE LỊCH SỬ ---
HISTORY_DIR = r"D:\nhúng truyện fanqie, qidian,qimao"
HISTORY_FILE = os.path.join(HISTORY_DIR, "da_lam_xong.txt")

# --- CẤU HÌNH TÀI KHOẢN (NGƯỜI DÙNG TỰ ĐIỀN) ---
STV_USERNAME = "YOUR_USERNAME_HERE" 
STV_PASSWORD = "YOUR_PASSWORD_HERE"

def setup_driver():
    """Khởi tạo trình duyệt Chrome"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    # Thêm timeout load trang để tránh đợi quá lâu (60s là timeout)
    options.set_capability("pageLoadStrategy", "normal")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    # Cài đặt timeout cho trình duyệt
    driver.set_page_load_timeout(60) 
    return driver

def get_book_id(url):
    if not url: return None
    match = re.search(r'/page/(\d+)', url)
    if match:
        return match.group(1)
    return None

def ensure_history_dir():
    if not os.path.exists(HISTORY_DIR):
        try:
            os.makedirs(HISTORY_DIR)
            print(f"[*] Đã tạo thư mục mới: {HISTORY_DIR}")
        except Exception as e:
            print(f"[!] Không thể tạo thư mục lưu trữ: {e}")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    
    ids = set()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ids.add(line)
    except Exception as e:
        print(f"[!] Lỗi khi đọc file lịch sử: {e}")
    return ids

def save_history(book_id):
    if not book_id: return
    ensure_history_dir()
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(book_id + "\n")
    except Exception as e:
        print(f"[!] Lỗi khi lưu lịch sử: {e}")

def login_to_stv(driver, wait):
    print("--- Đang truy cập Sangtacviet ---")
    try:
        driver.get(SANGTACVIET_URL)
        try:
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Đăng nhập')] | //button[contains(text(), 'Đăng nhập')]")))
            login_btn.click()
            print("-> Đã mở form đăng nhập")

            username_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[placeholder*='Tài khoản'], input[type='text']")))
            username_field.clear()
            username_field.send_keys(STV_USERNAME)

            password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password'], input[placeholder*='Mật khẩu'], input[type='password']")
            password_field.clear()
            password_field.send_keys(STV_PASSWORD)

            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], div.modal-footer button")
            if not submit_btn:
                 submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Đăng nhập')]")
            
            submit_btn.click()
            print(f"-> Đã điền thông tin cho user: {STV_USERNAME}")
            time.sleep(3)
        except:
            print("-> Có vẻ bạn ĐÃ đăng nhập rồi hoặc không tìm thấy nút đăng nhập.")
            
    except Exception as e:
        print(f"!! Lỗi khi thao tác login: {e}")

def run_automation(driver, wait, custom_url=None):
    processed_ids = load_history()
    print(f"\n[*] File lịch sử: {HISTORY_FILE}")
    print(f"[*] Đã tải lịch sử: {len(processed_ids)} ID truyện đã làm.")

    url_template = None
    current_page = 1
    single_page_mode = False 

    if custom_url:
        match = re.search(r'page_(\d+)', custom_url)
        if match:
            current_page = int(match.group(1)) 
            url_template = custom_url.replace(f"page_{current_page}", "page_{}")
            print(f"[*] Đã nhận diện link nhiều trang. Bắt đầu từ trang {current_page}...")
        else:
            single_page_mode = True
            print("[*] Link này không có số trang (page_X). Tool sẽ chỉ quét 1 lần trang này.")
    else:
        url_template = FANQIE_DEFAULT_TEMPLATE
        current_page = 1

    while True:
        if single_page_mode:
            target_url = custom_url
        else:
            target_url = url_template.format(current_page)

        print(f"\n==================================================")
        print(f"[*] ĐANG QUÉT TRANG SỐ: {current_page if not single_page_mode else 'Custom'}")
        print(f"==================================================")
        
        # 1. Quét link Fanqie
        try:
            driver.get(target_url)
            time.sleep(3)
            print(f"[*] Đang lăn chuột...")
            for i in range(SCROLL_TIMES):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)

            print("[*] Đang lấy danh sách truyện...")
            story_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/page/']")
            new_books = []
            
            for elem in story_elements:
                raw_href = elem.get_attribute('href')
                if raw_href and "fanqienovel.com/page/" in raw_href:
                    book_id = get_book_id(raw_href)
                    if book_id and book_id not in processed_ids:
                        is_duplicate_in_batch = any(item[0] == book_id for item in new_books)
                        if not is_duplicate_in_batch:
                            new_books.append((book_id, raw_href))
        except Exception as e:
            print(f"[!] Lỗi khi quét Fanqie: {e}. Thử lại trang này...")
            time.sleep(5)
            continue

        if not new_books:
            print(f"[!] Không có truyện mới nào ở trang {current_page} (Tất cả ID đã có trong file).")
            if single_page_mode:
                print("-> Dừng.")
                break
            else:
                print("-> Chuyển sang trang tiếp theo ngay lập tức...")
                current_page += 1
                continue

        print(f"[+] Tìm thấy {len(new_books)} truyện MỚI (ID chưa trùng).")

        # 2. Mở Tab STV xử lý (CÓ CƠ CHẾ CHỐNG TREO)
        print("=> Đang xử lý (Nhấn 'q' để DỪNG)...")
        original_window = driver.current_window_handle
        
        # --- FIX LỖI TIMEOUT ---
        opened_tab_success = False
        retry_count = 0
        while not opened_tab_success and retry_count < 3:
            try:
                driver.switch_to.new_window('tab') 
                driver.get(SANGTACVIET_URL)
                opened_tab_success = True
            except Exception as e:
                print(f"\n[!] Lỗi mở tab STV (Lần {retry_count+1}): {e}")
                print("-> Đang thử đóng tab lỗi và mở lại...")
                try:
                    driver.close() # Cố gắng đóng tab lỗi
                    driver.switch_to.window(original_window) # Quay về tab gốc
                except:
                    pass
                retry_count += 1
                time.sleep(3)
        
        if not opened_tab_success:
            print("[!!!] KHÔNG THỂ MỞ STV SAU 3 LẦN THỬ. DỪNG AUTO ĐỂ TRÁNH TREO MÁY.")
            break
        # -----------------------
        
        stop_requested = False

        for index, (book_id, link) in enumerate(new_books):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key.lower() == b'q':
                    print("\n[!!!] Đã nhận lệnh dừng. Quay về Menu.")
                    stop_requested = True
                    break
            
            if book_id in processed_ids:
                continue

            print(f"Processing {index + 1}/{len(new_books)} | ID: {book_id}", end='\r')
            
            try:
                search_box = wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
                search_box.clear()
                search_box.send_keys(Keys.CONTROL + "a")
                search_box.send_keys(Keys.DELETE)
                
                search_box.send_keys(link)
                time.sleep(0.5)
                search_box.send_keys(Keys.ENTER)
                
                time.sleep(2.5) 
                
                save_history(book_id)
                processed_ids.add(book_id)
                print(f"-> OK: ID {book_id} đã lưu.               ") 

            except Exception as e:
                print(f"\n[!] Lỗi xử lý: {e}")
                print("-> Đang tải lại trang chủ STV để cứu vãn...")
                try:
                    driver.get(SANGTACVIET_URL)
                    time.sleep(3)
                except:
                    print("-> Tải lại thất bại. Bỏ qua lượt này.")
        
        # Đóng tab sau khi xong trang
        try:
            driver.close()
            driver.switch_to.window(original_window)
        except:
            print("[!] Lỗi khi đóng tab, tiếp tục...")
            # Cố gắng switch về tab đầu tiên nếu mất dấu
            driver.switch_to.window(driver.window_handles[0])
        
        if stop_requested:
            break
            
        print(f"\n[DONE] Hoàn thành trang {current_page if not single_page_mode else 'Custom'}.")
        
        if single_page_mode:
            break 
        else:
            current_page += 1
            time.sleep(2)

def main():
    driver = None
    wait = None
    ensure_history_dir()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n================ MENU TOOL (ANTI-CRASH) ================")
        print("1. Mở trang Sangtacviet (Đăng nhập/Check)")
        print("2. Chạy Auto (Link Mặc Định)")
        print("3. Chạy Auto (Nhập Link Fanqie)")
        print("4. Thoát tool")
        print("========================================================")
        
        choice = input("Nhập lựa chọn (1-4): ").strip()
        
        if choice in ['1', '2', '3']:
            if driver is None:
                print("\n[*] Đang khởi động trình duyệt...")
                try:
                    driver = setup_driver()
                    wait = WebDriverWait(driver, 15)
                except Exception as e:
                    print(f"Lỗi khởi động Chrome: {e}")
                    input("Nhấn Enter để thử lại...")
                    continue

            if choice == '1':
                login_to_stv(driver, wait)
                input("\n-> Nhấn Enter để quay lại Menu...")
            
            elif choice == '2':
                run_automation(driver, wait, custom_url=None)
                input("\n-> Đợt chạy kết thúc. Nhấn Enter để quay lại Menu...")
            
            elif choice == '3':
                print("\n--- NHẬP LINK FANQIE ---")
                user_link = input("Dán link vào đây: ").strip()
                if user_link:
                    run_automation(driver, wait, custom_url=user_link)
                else:
                    print("Link trống!")
                input("\n-> Đợt chạy kết thúc. Nhấn Enter để quay lại Menu...")
        
        elif choice == '4':
            print("Tạm biệt!")
            if driver:
                try: driver.quit()
                except: pass
            break
        else:
            print("Lựa chọn không hợp lệ.")
            time.sleep(1)

if __name__ == "__main__":
    main()