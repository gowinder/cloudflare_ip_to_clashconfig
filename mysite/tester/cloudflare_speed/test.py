from requests_toolbelt.adapters import host_header_ssl
import requests

s = requests.Session()
s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
url = 'https://%s%s' % ('104.16.60.238', '/__down?bytes=1000000000')
headers = {'HOST': 'speed.cloudflare.com'}

try:
    response = s.get(url, headers=headers, stream = True, timeout=10 + 1)
except Exception as ex:
    print(ex)

curl --resolve speed.cloudflare.com:443:104.16.60.238 https://speed.cloudflare.com/__down?bytes=1000000000