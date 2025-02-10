import os
import subprocess
import requests
import re

def get_uuid():
    if not os.path.exists('uuid.txt'):
        uuid = input("请输入您的UUID: ")
        with open('uuid.txt', 'w') as f:
            f.write(uuid)
    else:
        with open('uuid.txt', 'r') as f:
            uuid = f.read().strip()
    return uuid

def get_region():
    print("请选择地区代码:")
    print("日本 -- JP")
    print("香港 -- HK")
    print("新加坡 -- SG")
    print("台湾 -- TW")
    print("美国 -- US")
    region = input("请输入地区代码: ")
    return region

def get_service():
    print("请选择媒体服务代码:")
    print("NF+PV+HAMI+BAHAMUT+GPT+Crunchyroll -- ALL")
    print("Netflix -- NF")
    print("PrimeVideo -- PV")
    print("HAMI -- HAMI")
    print("ChatGPT -- GPT")
    print("Crunchyroll -- CR")
    print("动画疯 -- BAHAMUT")
    service = input("请输入媒体代码: ")
    return service

def send_request(uuid, region):
    url = f"http://109.176.255.156:8080?uuid={uuid}&region={region}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('value')
    else:
        print("请求失败:", response.json())
        return None


def nf_test():
    result = os.popen("./nf")
    result = result.read()
    return result


def find_in_nf_test(nf_region):
    for _ in range(4):
        result = os.popen("./nf")
        result = result.read()
        print(result)
        if "您的出口IP完整解锁Netflix，支持非自制剧的观看" in result and f"所识别的IP地域信息：{nf_region}" in result:
            print("done")
            return 0


def together(region, service):
    return f"{region}_{service}"


service_domain_map = {
    'ALL': ['address'],
    'NF': ['netflix.com', 'netflix.net', 'nflximg.com', 'nflximg.net', 'nflxvideo.net', 'nflxso.net', 'nflxext.com'],
    'HAMI': ['hinet.net'],
    'BAHAMUT': ['gamer.com.tw', 'bahamut.com'],
    'GPT': ['openai.com'],
    'PV': ['amazonprimevideo.cn', 'amazonprimevideo.com.cn', 'mazonprimevideos.com', 'amazonvideo.cc', 'media-amazon.com', 'prime-video.com', 'primevideo.cc', 'primevideo.com', 'primevideo.info', 'primevideo.org', 'primevideo.tv', 'pv-cdn.net'],
    'CR': ['crunchyroll.com']
}

nf_region_map = {
    "JP": "日本",
    "HK": "香港",
    "SG": "新加坡",
    "TW": "台湾",
    "US": "美国",
}


def change_conf(proxy_ip):
    conf_path = "/etc/dnsmasq.conf"

    with open(conf_path, 'r') as file:
        lines = file.readlines()

    with open(conf_path, 'w') as file:
        for line in lines:
            if line.startswith("address="):
                parts = line.split('/')
                file.write(f"address=/{parts[1]}/{proxy_ip}\n")
            else:
                file.write(line)


def main():
    print('使用本脚本请注意如下事项：')
    print('1.你需要先获得uuid')
    print('2.本脚本使用过程中仅能输入大写字母 不支持特殊字符和小写 请严格按照提示输入否则报错')
    uuid = get_uuid()
    region = get_region()
    service = get_service()
    print(service)
    os.system("rm -rf /etc/resolv.conf && echo 'nameserver 1.1.1.1'>/etc/resolv.conf")
    if service == "NF":
        while True:
            service = 'NF'
            service_id = together(region, service)
            print(service_id)
            print("NF")
            proxy_ip = send_request(uuid, service_id)
            print("requested")
            print(proxy_ip)
            if proxy_ip is None:
                print("Failed to get proxy IP. Exiting.")
                break
            os.system("systemctl stop dnsmasq")
            change_conf(proxy_ip)
            os.system("systemctl restart dnsmasq")
            os.system("rm -rf /etc/resolv.conf && echo 'nameserver 127.0.0.1'>/etc/resolv.conf")
            nf_region = nf_region_map.get(region, 'luna')
            result = find_in_nf_test(nf_region)
            if result == 0:
                break

    print('work_done')
    print(proxy_ip)

if __name__ == "__main__":
    main()
