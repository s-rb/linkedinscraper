import json
import requests
from fake_useragent import UserAgent
from six import print_

urlIp = "http://api.ipify.org?format=json"
url = urlIp
# url = f"http://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=java&location=usa&f_TPR=&f_WT=&geoId=&f_TPR=r400000&start=0"
ua = UserAgent(browsers=['Safari', 'Chrome', 'Firefox'], os=["Windows", "Ubuntu", "Mac OS X", "Android", "iOS"])

def load_config(file_name):
    # Load the config file
    with open(file_name) as f:
        return json.load(f)

config =load_config('config.json')

def load_proxies(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_proxies(file_path, proxies):
    with open(file_path, 'w') as file:
        json.dump(proxies, file, indent=4)


def checkProxyEquals(ip1, headers_ua, http_proxy):
    try:
        r = requests.get(urlIp, headers=headers_ua, proxies=http_proxy, timeout=10)
        r.raise_for_status()
        ip2 = r.json()['ip']
    except requests.exceptions.RequestException as e:
        assert False, f"WARNING! NO CONNECTION! Proxy connection test failed: Failed to make the first API call without proxy. Reason: {str(e)}"

    # Verify that the two IP addresses are different
    assert ip1 != ip2, "Proxy connection test failed: IP addresses are the same"

    # Print the IP addresses for verification
    print(f"Personal IP: {ip1}")
    print(f"Proxy IP: {ip2}")
    print("Proxy connection was successfully used for request.")
    return True


def check_proxy(proxy, ip1):
    http_proxy = {"http": f"http://{proxy['ip_address']}:{proxy['port']}",
                  "https": f"https://{proxy['ip_address']}:{proxy['port']}"}
    headers_ua = {**config['headers'], "User-Agent": ua.random}

    try:
        r = requests.get(url, headers=headers_ua, proxies=http_proxy, timeout=10)
        r.raise_for_status()  # Raise an error for bad responses
        if (r.status_code == 200): return checkProxyEquals(ip1, headers_ua, http_proxy)
        else: raise requests.RequestException
    except Exception as ex:
        print(f"HTTP request failed with proxy {http_proxy}: {ex}")

    return False


def test_and_remove_proxies(file_path):
    # Make the first API call without using the proxy
    try:
        response1 = requests.get(url, headers={**config['headers'], "User-Agent": ua.random}, timeout=5)
        response1.raise_for_status()

        response1 = requests.get(urlIp, headers={**config['headers'], "User-Agent": ua.random}, timeout=5)
        response1.raise_for_status()
        ip1 = response1.json()['ip']
    except requests.exceptions.RequestException as e:
        assert False, f"WARNING! NO CONNECTION! Proxy connection test failed: Failed to make the first API call without proxy. Reason: {str(e)}"


    proxies = load_proxies(file_path)
    valid_proxies = []

    counter = 1
    for proxy in proxies:
        print(f"Checking proxy: {counter}/{len(proxies)}")
        counter += 1
        success = False
        for _ in range(2):  # 1 attempts
            if check_proxy(proxy, ip1):
                success = True
                break
        if success:
            print(f"Valid proxy found! proxy: {proxy}")
            valid_proxies.append(proxy)
        else:
            print(f"Proxy {proxy} is not accessible and will be removed.")
        print("\n---------------------\n")

    save_proxies(file_path, valid_proxies)

if __name__ == "__main__":
    test_and_remove_proxies('proxies.json')