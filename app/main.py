import os
import time
import logging
from datetime import datetime
from tasks import scrape_user_posts
from celery import group
from utils import get_following_accounts, save_to_json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Giriş bilgilerini çevre değişkenlerinden al
    platform = os.environ.get('PLATFORM', 'instagram')
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')
    
    if not username or not password:
        logger.error("Kullanıcı adı veya şifre eksik! Çevre değişkenlerini kontrol edin.")
        return
    
    logger.info(f"{platform} platformu için oturum açılıyor... Kullanıcı: {username}")
    
    try:
        # Takip edilen hesapları al
        accounts = get_following_accounts(platform, username, password)
        logger.info(f"Toplam {len(accounts)} takip edilen hesap bulundu.")
        
        if not accounts:
            logger.warning("Takip edilen hesap bulunamadı.")
            return
        
        # Her hesap için asenkron görev oluştur
        tasks = []
        for account in accounts:
            tasks.append(scrape_user_posts.s(platform, account, username, password))
        
        # Görevleri grup olarak çalıştır
        job = group(tasks)
        result = job.apply_async()
        
        # Tüm görevlerin tamamlanmasını bekle
        while not result.ready():
            logger.info(f"Görevler çalışıyor... Tamamlanan: {result.completed_count()}/{len(tasks)}")
            time.sleep(5)
        
        # Görev sonuçlarını topla
        all_posts = []
        for task_result in result.get():
            if task_result:
                all_posts.extend(task_result)
        
        # Sonuçları JSON'a kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/data/posts_{timestamp}.json"
        save_to_json(all_posts, filename)
        logger.info(f"Toplam {len(all_posts)} gönderi {filename} dosyasına kaydedildi.")
        
    except Exception as e:
        logger.error(f"İşlem sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    # Ana uygulamanın başlangıç noktası
    logger.info("Sosyal medya takip sistemi başlatılıyor...")
    main()