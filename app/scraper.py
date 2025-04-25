import time
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
            
            self.driver = webdriver.Remote(
                command_executor=f'http://{self.selenium_host}:4444/wd/hub',
                options=options
            )
            self.driver.set_window_size(1920, 1080)
            return True
        except Exception as e:
            logger.error(f"WebDriver başlatılırken hata oluştu: {str(e)}")
            return False
    
    def login(self, username, password):
        """Sosyal medya platformuna giriş yapar."""
        try:
            if self.platform == 'instagram':
                self.driver.get('https://www.instagram.com/accounts/login/')
                time.sleep(2)  # Sayfanın yüklenmesi için bekle
                
                # Çerezleri kabul et (gerekirse)
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Kabul Et')]"))
                    )
                    cookie_button.click()
                except:
                    logger.info("Çerez butonu bulunamadı, devam ediliyor.")
                
                # Kullanıcı adı ve şifre giriş alanları
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='sucukluyumurta1252']"))
                )
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='20062003Am.']")
                
                # Giriş bilgilerini doldur
                username_input.send_keys(username)
                password_input.send_keys(password)
                
                # Giriş butonuna tıkla
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                
                # Giriş başarılı mı diye kontrol et
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]"))
                    )
                    logger.info("Instagram'a başarıyla giriş yapıldı.")
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
    
    def get_user_posts(self, username, hours=24):
        """Belirtilen kullanıcının son 24 saatteki gönderilerini alır."""
        posts = []
        try:
            if self.platform == 'instagram':
                # Kullanıcı profiline git
                self.driver.get(f'https://www.instagram.com/{username}/')
                time.sleep(3)  # Sayfanın yüklenmesi için bekle
                
                # Son 24 saat için datetime hesapla
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                # İlk 12 gönderiyi incele (varsayılan olarak bir sayfada görünen)
                post_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//article//a[contains(@href, '/p/')]"))
                )
                
                # Her gönderinin bağlantısını al
                post_links = [post.get_attribute('href') for post in post_elements[:12]]
                
                for link in post_links:
                    self.driver.get(link)
                    time.sleep(2)  # Gönderi sayfasının yüklenmesi için bekle
                    
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
                            # Gönderi içeriğini al
                            try:
                                caption = self.driver.find_element(By.XPATH, "//div[contains(@class, '_a9zs')]").text
                            except NoSuchElementException:
                                caption = ""
                            
                            # Gönderi tipini kontrol et (fotoğraf veya video)
                            post_type = "photo"
                            try:
                                if self.driver.find_element(By.XPATH, "//video"):
                                    post_type = "video"
                            except NoSuchElementException:
                                pass
                            
                            # Beğeni sayısını al
                            try:
                                likes = self.driver.find_element(By.XPATH, "//section//span/div").text
                            except NoSuchElementException:
                                likes = "0"
                            
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
                            logger.info(f"Gönderi 24 saatten eski, atlanıyor: {username} - {post_date}")
                    
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