import os

# Uygulama yapılandırması
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
SELENIUM_HOST = os.environ.get('SELENIUM_HOST', 'selenium')
SELENIUM_PORT = int(os.environ.get('SELENIUM_PORT', 4444))

# Platform yapılandırması - önemli bilgileri çevre değişkenlerinden alın
PLATFORM = os.environ.get('PLATFORM', 'instagram')
USERNAME = os.environ.get('INSTAGRAM_USERNAME', '')
PASSWORD = os.environ.get('INSTAGRAM_PASSWORD', '')

# Veri toplama yapılandırması
MAX_ACCOUNTS = int(os.environ.get('MAX_ACCOUNTS', 100))
POST_HOURS = int(os.environ.get('POST_HOURS', 24))
DATA_DIR = os.environ.get('DATA_DIR', '/data')

# Rate limiting ve güvenlik ayarları
# Instagram'ın rate-limit'lerini aşmamak için
REQUEST_DELAY_MIN = float(os.environ.get('REQUEST_DELAY_MIN', 2.0))  # En az bekleme süresi (saniye)
REQUEST_DELAY_MAX = float(os.environ.get('REQUEST_DELAY_MAX', 5.0))  # En fazla bekleme süresi (saniye)
MAX_POSTS_PER_USER = int(os.environ.get('MAX_POSTS_PER_USER', 12))   # Kullanıcı başına incelenecek max gönderi
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))                  # Hata durumunda max yeniden deneme sayısı
RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 60))                 # Yeniden deneme arasındaki bekleme süresi (saniye)