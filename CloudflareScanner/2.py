import csv

input_file = 'CloudflareScanner/result.csv'
output_file = 'CloudflareScanner/proxyip.txt'

with open(input_file, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    valid_ips = []
    for row in reader:
        try:
            speed = float(row['Download Speed (MB/s)'])
            if speed > 10:
                valid_ips.append(row['IP Address'])
        except Exception:
            continue

with open(output_file, 'w', encoding='utf-8') as outfile:
    for ip in valid_ips:
        outfile.write(ip + '\n')
