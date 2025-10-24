import ipaddress
import re
import sys
import argparse
import requests

ipv4_regex = re.compile(r'((?:[0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{1,2})')
ipfile = r"C:\Users\v-micgilmore\Downloads\ServiceTags_Public_20250714.json"

with open(ipfile) as f:
    filestr = f.read()


parser = argparse.ArgumentParser(description="Get list of IPs from stdin and check to see if they are MS")
parser.add_argument(
        "--mode",
        choices=["match", "notmatch"],
        default="match",
        help="return matching ips or non matching ips (default: match)"
    )
parser.add_argument(
        "--print-errors",
        action="store_true",
        help="print errors"
    )
parser.add_argument(
        "--print-service-tags",
        action="store_true",
        help="print errors"
    )
parser.add_argument(
        "--wireshark",
        action="store_true",
        help="print wireshark display filter"
    )
parser.add_argument(
        "--offline-mode",
        action="store_true",
        help=f"Read from offline file {ipfile}"
    )

args = parser.parse_args()


def is_ip_in_ranges(ip, ranges):
    ip_obj = ipaddress.ip_address(ip)
    for range_str in ranges:
        network = ipaddress.ip_network(range_str, strict=False)
        if ip_obj in network:
            return True
    return False

lines = sys.stdin.read().strip().splitlines()
#lines = ["52.123.173.240"]
ip_ranges = ips = set(re.findall(ipv4_regex, filestr))
results = []
#args.print_servicetags = True

if not args.offline_mode:
    unique_ips = ','.join(set(lines))
    print(f'{len(lines)} received {len(set(lines))} unique ips, querying API now...')
    url = "https://azservicetags.azurewebsites.net//api/iplookup?ipAddresses="+unique_ips
    response = requests.get(url)
    assert response.status_code == 200

    for r in response.json():
        for ip in lines:
            if r['ipAddress'] == ip and len(r['matchedServiceTags']) > 0:
                results.append(ip)
                st = ""
                if args.print_service_tags:
                    for i in r['matchedServiceTags']:
                        st+= '\t'+i['serviceTagId']
                print(ip + st)
else:
    for ip in check:
        try:
            result = is_ip_in_ranges(ip, ip_ranges)
            if result == True and args.mode == 'match':
                print(f"{ip}")
                results.append(ip)
            elif result == False and args.mode == 'notmatch':
                print(f"{ip}")
                results.append(ip)
        except ValueError as e:
            if args.print_errors:
                print(e)
if args.wireshark:
    print(' || '.join(['ip.dst == '+i for i in results]))
