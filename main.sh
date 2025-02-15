source /app/venv/bin/activate
cp proxies.json proxies.json.backup_$(date +%Y-%m-%dT%H:%M:%S)
python3 -u test_and_remove_proxies.py
if [ $? -ne 0 ]; then
    echo "Ошибка при выполнении скрипта"
    exit 1
fi
python3 -u main_app.py