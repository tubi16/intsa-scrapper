FROM python:3.9-slim

WORKDIR /app

# Temel bağımlılıklar
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Gerekli Python paketlerini yükle
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Python modül arama yolunu çalışma dizinine ayarla
ENV PYTHONPATH=/app

# Veri dizini oluştur
RUN mkdir -p /data
VOLUME /data

# Herhangi bir ek yapılandırma
ENV TZ=Europe/Istanbul

# Varsayılan komut - container başladığında hiçbir şey yapma
# Docker Compose'da her servis için özel komut belirtilecek
CMD ["python", "main.py"]