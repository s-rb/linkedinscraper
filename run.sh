uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
cp src/backend/proxies.json src/backend/proxies.json.backup_$(date +%Y-%m-%dT%H:%M:%S)
python3 src/backend/test_and_remove_proxies.py
if [ $? -ne 0 ]; then
    echo "Ошибка при выполнении скрипта"
    exit 1
fi
#if [ ! -f src/backend/proxies.json ] || [ ! -s src/backend/proxies.json ] || [ "$(jq '. | length' src/backend/proxies.json)" -eq 0 ]; then
#    echo "Отсутствуют прокси!"
#    exit 1
#fi
python3 src/backend/main.py