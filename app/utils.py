import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

def get_following_accounts(platform, username, password, selenium_host='selenium', max_accounts=100):
    """
    Kullanıcının takip ettiği hesapların listesini döndürür.
    
    Args:
        platform: Sosyal medya platformu
        username: Kullanıcı adı
        password: Şifre
        selenium_host: Selenium servisinin host adresi
        max_accounts: Alınacak maksimum hesap sayısı
        
    Returns:
        list: Takip edilen hesapların listesi
    """
    accounts = []
    driver = None
    
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Remote(
            command_executor=f'http://{selenium_host}:4444/wd/hub',
            options=options
        )
        driver.set_window_size(1920, 1080)
        
        if platform == 'instagram':
            # Instagram'a giriş yap
            driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(2)
            
            # Çerezleri kabul et (gerekirse)
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Kabul Et')]"))
                )
                cookie_button.click()
            except:
                pass
            
            # Kullanıcı adı ve şifre giriş alanları
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='sucukluyumurta1252']"))
            )
            password_input = driver.find_element(By.CSS_SELECTOR, "input[name='20062003Am.']")
            
            # Giriş bilgilerini doldur
            username_input.send_keys(username)
            password_input.send_keys(password)
            
            # Giriş butonuna tıkla
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Giriş başarılı mı diye kontrol et
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]"))
                )
                logger.info("Instagram'a başarıyla giriş yapıldı.")
            except TimeoutException:
                raise Exception("Instagram girişi başarısız oldu.")
                
            # Profil sayfasına git
            driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(2)
            
            # Following sayfasına git
            try:
                following_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following')]"))
                )
                following_link.click()
                time.sleep(2)
            except:
                # Alternatif yol dene (yeni UI için)
                try:
                    following_count = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//ul//li[3]//a"))
                    )
                    following_count.click()
                    time.sleep(2)
                except:
                    raise Exception("Following sayfasına erişilemedi.")
            
            # Following listesini scrape et
            try:
                # Following penceresi
                following_dialog = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                )
                
                # Scroll yaparak tüm hesapları yükle
                scrolls = 0
                max_scrolls = 10  # Maksimum scroll sayısı (hesap sayısına bağlı olarak ayarlayın)
                
                while len(accounts) < max_accounts and scrolls < max_scrolls:
                    # Kullanıcı adlarını al
                    user_elements = following_dialog.find_elements(By.XPATH, ".//div[contains(@class, '_aano')]//div[contains(@class, '_ab8y')]//div[contains(@class, '_ab8w')]//div[contains(@class, '_aacl')]")
                    
                    for user_element in user_elements:
                        username = user_element.text
                        if username and username not in accounts:
                            accounts.append(username)
                            if len(accounts) >= max_accounts:
                                break
                    
                    # Scroll yap
                    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', following_dialog)
                    time.sleep(1)
                    scrolls += 1
                
            except Exception as e:
                logger.error(f"Following listesi alınırken hata oluştu: {str(e)}")
                
        elif platform == 'twitter':
            # Twitter için following listesi alma kodları
            pass
        
    except Exception as e:
        logger.error(f"Takip edilen hesaplar alınırken hata oluştu: {str(e)}")
    finally:
        if driver:
            driver.quit()
    
    return accounts

def save_to_json(data, filename):
    """
    Verileri JSON dosyasına kaydeder.
    
    Args:
        data: Kaydedilecek veriler
        filename: Dosya adı
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"JSON dosyası kaydedilirken hata oluştu: {str(e)}")
        return False