import time
import random
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SocialMediaScraper:
    def __init__(self, platform, selenium_host='selenium'):
        self.platform = platform
        self.selenium_host = selenium_host
        self.driver = None
    
    def setup_driver(self):
        """Selenium WebDriver'ı yapılandırır ve başlatır."""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Bot algılama mekanizmalarını atlatmak için
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Remote(
                command_executor=f'http://{self.selenium_host}:4444/wd/hub',
                options=options
            )
            self.driver.set_window_size(1920, 1080)
            
            # Bot algılamasını atlatmak için ek önlemler
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
        except Exception as e:
            logger.error(f"WebDriver başlatılırken hata oluştu: {str(e)}")
            return False
    
    def login(self, username, password):
        """Sosyal medya platformuna giriş yapar."""
        try:
            if self.platform == 'instagram':
                self.driver.get('https://www.instagram.com/accounts/login/')
                # Rastgele bekleme süresi
                time.sleep(random.uniform(3, 5))
                
                # Çerezleri kabul et (gerekirse)
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Kabul Et')]"))
                    )
                    cookie_button.click()
                    time.sleep(random.uniform(1, 2))
                except:
                    logger.info("Çerez butonu bulunamadı, devam ediliyor.")
                
                # Kullanıcı adı ve şifre giriş alanları
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
                )
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
                
                # Giriş bilgilerini doğal şekilde gir
                self._type_like_human(username_input, username)
                time.sleep(random.uniform(0.5, 1.5))
                self._type_like_human(password_input, password)
                
                # Giriş butonuna tıkla
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                
                # Giriş başarılı mı diye kontrol et
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]"))
                    )
                    logger.info("Instagram'a başarıyla giriş yapıldı.")
                    
                    # Olası "Şimdi Değil" veya bildirim popup'larını kapat
                    try:
                        not_now_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Şimdi Değil')]"))
                        )
                        not_now_button.click()
                        time.sleep(random.uniform(1, 2))
                    except:
                        pass
                    
                    return True
                except TimeoutException:
                    logger.error("Instagram girişi başarısız oldu. Kullanıcı adı ve şifreyi kontrol edin.")
                    return False
                
            elif self.platform == 'twitter':
                # Twitter için login kodları
                pass
            else:
                logger.error(f"Platform desteklenmiyor: {self.platform}")
                return False
                
        except Exception as e:
            logger.error(f"Giriş sırasında hata oluştu: {str(e)}")
            return False
    
    def _type_like_human(self, element, text):
        """İnsan gibi yazma simulasyonu - botların tespitini zorlaştırır"""
        for character in text:
            element.send_keys(character)
            time.sleep(random.uniform(0.05, 0.2))  # Her karakter arasında rastgele gecikme
    
    def get_user_posts(self, username, hours=24):
        """Belirtilen kullanıcının son 24 saatteki gönderilerini alır."""
        posts = []
        try:
            if self.platform == 'instagram':
                # Kullanıcı profiline git
                self.driver.get(f'https://www.instagram.com/{username}/')
                time.sleep(random.uniform(3, 5))  # Sayfanın yüklenmesi için bekle
                
                # Profil bulunmadı veya gizli mi kontrol et
                if "This Account is Private" in self.driver.page_source or "Sayfa Bulunamadı" in self.driver.page_source:
                    logger.warning(f"{username} profili gizli veya mevcut değil, atlanıyor.")
                    return posts
                
                # Son 24 saat için datetime hesapla
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                # Gönderileri bul - muhtemelen a[href] ile başlayan ve '/p/' içeren linkler
                try:
                    # Modern Instagram UI için
                    post_elements = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//article//a[contains(@href, '/p/')]"))
                    )
                except:
                    try:
                        # Alternatif seçici dene
                        post_elements = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, '_aabd')]//a"))
                        )
                    except:
                        logger.warning(f"{username} için gönderi elementleri bulunamadı.")
                        return posts
                
                # En fazla 12 gönderiyi incele (ayarlanabilir)
                max_posts = min(12, len(post_elements))
                post_links = [post.get_attribute('href') for post in post_elements[:max_posts]]
                
                for link in post_links:
                    # Her gönderi arasında kısa bir bekleme
                    time.sleep(random.uniform(2, 4))
                    
                    self.driver.get(link)
                    time.sleep(random.uniform(3, 5))  # Gönderi sayfasının yüklenmesi için bekle
                    
                    try:
                        # Gönderi tarihini bul
                        time_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//time"))
                        )
                        post_date_str = time_element.get_attribute('datetime')
                        post_date = datetime.fromisoformat(post_date_str.replace('Z', '+00:00'))
                        
                        # Yerel saat dilimine çevir
                        post_date = post_date.replace(tzinfo=None)
                        
                        # Son 24 saat içinde mi kontrol et
                        if post_date >= cutoff_time:
                            # Gönderi içeriğini al - birden fazla seçici dene
                            caption = ""
                            for selector in [
                                "//div[contains(@class, '_a9zs')]",
                                "//div[contains(@class, 'C4VMK')]//span",
                                "//div[contains(@class, '_ac2a')]//span"
                            ]:
                                try:
                                    caption_element = self.driver.find_element(By.XPATH, selector)
                                    caption = caption_element.text
                                    break
                                except NoSuchElementException:
                                    continue
                            
                            # Gönderi tipini kontrol et (fotoğraf veya video)
                            post_type = "photo"
                            try:
                                if self.driver.find_element(By.XPATH, "//video"):
                                    post_type = "video"
                            except NoSuchElementException:
                                pass
                            
                            # Beğeni sayısını al - birden fazla seçici dene
                            likes = "0"
                            for selector in [
                                "//section//span/div",
                                "//div[contains(@class, '_aacl')]//span",
                                "//a[contains(@href, 'liked_by')]/span"
                            ]:
                                try:
                                    likes_element = self.driver.find_element(By.XPATH, selector)
                                    likes = likes_element.text
                                    break
                                except NoSuchElementException:
                                    continue
                            
                            # Post verilerini kaydet
                            post_data = {
                                "platform": self.platform,
                                "username": username,
                                "post_url": link,
                                "caption": caption,
                                "type": post_type,
                                "likes": likes,
                                "date": post_date.isoformat(),
                                "scraped_at": datetime.now().isoformat()
                            }
                            
                            posts.append(post_data)
                            logger.info(f"Gönderi eklendi: {username} - {post_date}")
                        else:
                            logger.info(f"Gönderi belirtilen süreden ({hours} saat) eski, atlanıyor: {username} - {post_date}")
                    
                    except Exception as e:
                        logger.error(f"Gönderi işlenirken hata oluştu: {str(e)}")
                
            elif self.platform == 'twitter':
                # Twitter için post scraping kodları
                pass
            
            return posts
            
        except Exception as e:
            logger.error(f"Gönderiler alınırken hata oluştu: {str(e)}")
            return posts
    
    def close(self):
        """WebDriver'ı kapatır."""
        if self.driver:
            self.driver.quit()