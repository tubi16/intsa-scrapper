import json
import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

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
        
        # Bot algılama mekanizmalarını atlatmak için
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')
        
        driver = webdriver.Remote(
            command_executor=f'http://{selenium_host}:4444/wd/hub',
            options=options
        )
        driver.set_window_size(1920, 1080)
        
        # Bot algılamasını atlatmak için ek önlemler
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        if platform == 'instagram':
            # Instagram'a giriş yap
            driver.get('https://www.instagram.com/')
            time.sleep(random.uniform(5, 8))  # Daha uzun bir bekleme
            driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(random.uniform(3, 5))
            
            # Çerezleri kabul et (gerekirse)
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Kabul Et')]"))
                )
                cookie_button.click()
                time.sleep(random.uniform(1, 2))
            except:
                logger.info("Çerez butonu bulunamadı, devam ediliyor.")
            
            # Kullanıcı adı ve şifre giriş alanları
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
            )
            password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            
            # İnsan gibi yazma simulasyonu
            for char in username:
                username_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
                
            time.sleep(random.uniform(0.5, 1.5))
            
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            
            # Giriş butonuna tıkla
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Giriş başarılı mı diye kontrol et
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]"))
                )
                logger.info("Instagram'a başarıyla giriş yapıldı.")
                
                # Olası "Şimdi Değil" veya bildirim popup'larını kapat
                try:
                    not_now_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Şimdi Değil')]"))
                    )
                    not_now_button.click()
                    time.sleep(random.uniform(1, 2))
                except:
                    pass
                
            except TimeoutException:
                raise Exception("Instagram girişi başarısız oldu. Kullanıcı adı veya şifre hatalı olabilir.")
                
            # Profil sayfasına git
            driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(random.uniform(3, 5))
            
            # Following sayfasına git - birden fazla seçici dene
            following_clicked = False
            
            # Yeni UI için takip edilen hesapları göster
            try:
                following_count = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following')]"))
                )
                following_count.click()
                following_clicked = True
                time.sleep(random.uniform(2, 3))
            except:
                # Alternatif seçici dene
                try:
                    following_count = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, '_aacl')]//a[contains(@href, 'following')]"))
                    )
                    following_count.click()
                    following_clicked = True
                    time.sleep(random.uniform(2, 3))
                except:
                    # Profilden takip ettiklerini bulmayı dene
                    try:
                        following_section = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//ul//li[3]//a"))
                        )
                        following_section.click()
                        following_clicked = True
                        time.sleep(random.uniform(2, 3))
                    except:
                        logger.error("Following sayfasına erişilemedi.")
                        raise Exception("Following sayfasına erişilemedi.")
            
            if following_clicked:
                # Following listesini scrape et
                try:
                    # Following penceresi - birden fazla seçici dene
                    following_dialog = None
                    for selector in [
                        "//div[@role='dialog']",
                        "//div[contains(@class, '_aano')]",
                        "//div[contains(@class, 'isgrP')]"
                    ]:
                        try:
                            following_dialog = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                            if following_dialog:
                                break
                        except:
                            continue
                    
                    if not following_dialog:
                        raise Exception("Following listesi penceresi bulunamadı.")
                    
                    # Scroll yaparak tüm hesapları yükle
                    scrolls = 0
                    max_scrolls = 20  # Maksimum scroll sayısı (hesap sayısına bağlı olarak ayarlayın)
                    
                    # Daha önce görülen hesapları izlemek için set
                    seen_usernames = set()
                    
                    while len(accounts) < max_accounts and scrolls < max_scrolls:
                        # Kullanıcı adlarını al - birden fazla seçici dene
                        user_elements = []
                        for selector in [
                            ".//div[contains(@class, '_aano')]//div[contains(@class, '_ab8y')]//div[contains(@class, '_ab8w')]//div[contains(@class, '_aacl')]",
                            ".//div[contains(@class, 'PZuss')]//a//span",
                            ".//div[contains(@class, '_aano')]//span//a//span",
                            ".//div[contains(@class, '_aano')]//div[contains(@role, 'button')]//span//span"
                        ]:
                            try:
                                elements = following_dialog.find_elements(By.XPATH, selector)
                                if elements:
                                    user_elements = elements
                                    break
                            except:
                                continue
                        
                        # Kullanıcı adlarını topla
                        new_accounts_found = False
                        for user_element in user_elements:
                            try:
                                username_text = user_element.text
                                if username_text and username_text not in seen_usernames:
                                    seen_usernames.add(username_text)
                                    accounts.append(username_text)
                                    new_accounts_found = True
                                    if len(accounts) >= max_accounts:
                                        break
                            except (StaleElementReferenceException, NoSuchElementException):
                                continue
                        
                        # Eğer yeni hesap bulunamadıysa ve maks. scroll sayısına ulaşılmadıysa scroll yap
                        if not new_accounts_found and len(accounts) < max_accounts:
                            # Scroll yap
                            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', 
                                                 following_dialog)
                            time.sleep(random.uniform(1.5, 3))  # Rate limit'i aşmamak için bekle
                        
                        scrolls += 1
                        
                        # Instagram rate limit'lerine dikkat etmek için periyodik olarak bekle
                        if scrolls % 5 == 0:
                            time.sleep(random.uniform(2, 4))
                
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
    
    # Sonuçları karıştır (Random sampling)
    if accounts:
        random.shuffle(accounts)
        accounts = accounts[:max_accounts]
    
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