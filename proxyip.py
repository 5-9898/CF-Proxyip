import csv
import requests
import time

input_file = 'CloudflareScanner/result.csv'
proxyip_file = 'proxyip.txt'
with_country_file = 'proxyip_with_country.txt'
countries_file = 'countries.txt'
RETRY = 10

# 加载国家代码-中文名字典
country_dict = {}
with open(countries_file, 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            code = parts[0].strip()
            name = parts[1].strip()
            country_dict[code] = name

# 步骤1：筛选Download Speed (MB/s) > 10的IP，保存到proxyip.txt，并记住速度
valid_infos = []
with open(input_file, 'r', encoding='utf-8') as csvfile:
    first_line = csvfile.readline()
    csvfile.seek(0)
    delimiter = '\t' if '\t' in first_line else ','
    reader = csv.DictReader(csvfile, delimiter=delimiter)
    for row in reader:
        try:
            speed = float(row.get('Download Speed (MB/s)', '0').strip())
            if speed > 10:
                ip = row.get('IP Address', '').strip()
                if ip:
                    valid_infos.append({'ip': ip, 'speed': speed})
        except Exception as e:
            print(f"Error parsing row: {row}, error: {e}")

with open(proxyip_file, 'w', encoding='utf-8') as outfile:
    for info in valid_infos:
        outfile.write(info['ip'] + '\n')
print(f"筛选完成，共输出 {len(valid_infos)} 个IP到 {proxyip_file}")

# 步骤2：查询国家信息并根据字典格式化输出
def get_country(ip):
    for attempt in range(RETRY):
        try:
            url = f'https://ipinfo.io/{ip}/json'
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if 'country' in data:
                return data['country']
            else:
                print(f"{ip} 未返回国家，响应内容：{data}")
        except Exception as e:
            print(f"第 {attempt+1} 次获取 {ip} 国家信息失败，错误：{e}")
        time.sleep(1)  # 每次重试间隔
    return 'Unknown'

with open(with_country_file, 'w', encoding='utf-8') as outfile:
    for info in valid_infos:
        ip = info['ip']
        speed = info['speed']
        country_code = get_country(ip)
        country_name = country_dict.get(country_code, country_code)
        # 输出格式：IP#速度(MB/s)国家代码国家中文名
        line = f"{ip}#{speed:.2f}(MB/s){country_code}{country_name}\n"
        outfile.write(line)
        print(line.strip())

print(f"查询国家并格式化输出完成，共输出 {len(valid_infos)} 个IP到 {with_country_file}")
