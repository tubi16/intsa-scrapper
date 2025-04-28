#!/bin/bash
# check_env.sh
# Bu betik Docker konteynerinde çevre değişkenlerinin doğru şekilde ayarlanıp ayarlanmadığını kontrol eder

echo "Çevre değişkenlerini kontrol etme betiği"
echo "----------------------------------------"

# Docker konteynerinde çalıştır
docker-compose exec scraper env | grep -E "USERNAME|PASSWORD|PLATFORM|REDIS|SELENIUM"

echo "----------------------------------------"
echo "Çevre değişkenleri doğru şekilde ayarlanmışsa, yukarıda USERNAME ve PASSWORD değerlerini görmelisiniz."
echo "Eğer değerleri görmüyorsanız, docker-compose.yml dosyanızda veya .env dosyanızda sorun var demektir."