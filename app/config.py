import os

# Uygulama yapılandırması
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
SELENIUM_HOST = os.environ.get('SELENIUM_HOST', 'selenium')
SELENIUM_PORT = os.environ.get('SELENIUM_PORT', 4444)

# Platform yapılandırması
PLATFORM = os.environ.get('PLATFORM', 'instagram')
USERNAME = os.environ.get('USERNAME', 'sucukluyumurta1252')
PASSWORD = os.environ.get('PASSWORD', '20062003Am.')

# Veri toplama yapılandırması
MAX_ACCOUNTS = int(os.environ.get('MAX_ACCOUNTS', 100))
POST_HOURS = int(os.environ.get('POST_HOURS', 24))
DATA_DIR = os.environ.get('DATA_DIR', '/data')
