uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
cp proxies.json proxies.json.backup_$(date +%Y-%m-%dT%H:%M:%S)
python3 test_and_remove_proxies.py
if [ $? -ne 0 ]; then
    echo "Ошибка при выполнении скрипта"
    exit 1
fi
if [ ! -f proxies.json ] || [ ! -s proxies.json ] || [ "$(jq '. | length' proxies.json)" -eq 0 ]; then
    echo "Отсутствуют прокси!"
    exit 1
fi
python3 main.py