source ./venv/bin/activate
cp proxies.json proxies.json.backup_$(date +%Y-%m-%dT%H:%M:%S)
python3 -u test_and_remove_proxies.py
#if [ $? -ne 0 ]; then
#    echo "Ошибка при выполнении скрипта"
#    exit 1
#fi

## Update resume data
# Скачиваем файл
curl -o default_cv_data.yml https://raw.githubusercontent.com/s-rb/site/master/_data/cv_data.yml

# Проверяем, был ли файл успешно скачан
if [ $? -eq 0 ]; then
    echo "Файл cv_data.yml успешно скачан и заменен."
else
    echo "Не удалось скачать файл cv_data.yml. Используем default_cv_data.yml."
    cp default_cv_data.yml default_cv_data.yml
fi

python -u app.py