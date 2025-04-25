from celery import Celery
import os
import logging
from scraper import SocialMediaScraper

logger = logging.getLogger(__name__)

# Celery yapılandırması
redis_host = os.environ.get('REDIS_HOST', 'redis')
app = Celery('social_scraper', broker=f'redis://{redis_host}:6379/0')

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Istanbul',
    enable_utc=True,
)

@app.task(bind=True, max_retries=3)
def scrape_user_posts(self, platform, username, login_username, login_password):
    """
    Belirtilen kullanıcının son 24 saatteki gönderilerini toplar.
    
    Args:
        platform: Sosyal medya platformu (instagram, twitter, vb.)
        username: Gönderileri alınacak hesap
        login_username: Giriş yapılacak hesap kullanıcı adı
        login_password: Giriş yapılacak hesap şifresi
        
    Returns:
        list: Gönderilerin listesi
    """
    logger.info(f"{username} kullanıcısının gönderileri toplanıyor...")
    
    selenium_host = os.environ.get('SELENIUM_HOST', 'selenium')
    scraper = SocialMediaScraper(platform, selenium_host)
    
    try:
        if not scraper.setup_driver():
            raise Exception("WebDriver başlatılamadı.")
        
        if not scraper.login(login_username, login_password):
            raise Exception("Platforma giriş yapılamadı.")
        
        posts = scraper.get_user_posts(username)
        logger.info(f"{username} için {len(posts)} gönderi bulundu.")
        
        return posts
        
    except Exception as e:
        logger.error(f"{username} için görev başarısız oldu: {str(e)}")
        # Yeniden deneme
        try:
            self.retry(exc=e, countdown=60 * self.request.retries)
        except:
            return []
    finally:
        # Her durumda driver'ı kapat
        scraper.close()