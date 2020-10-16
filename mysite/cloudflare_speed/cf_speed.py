import os
import pathlib
import time
import yaml
import ping3
import math
import requests
import colorama
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import threading
import socket
from datetime import datetime, timedelta 
from requests_toolbelt.adapters import host_header_ssl

PING_MAX = 5000
SPEED_MIN = 99999999999

dns_cache = {}
prv_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args):
    # Uncomment to see what calls to `getaddrinfo` look like.
    # print(args)
    try:
        return dns_cache[args[:2]] # hostname and port
    except KeyError:
        return prv_getaddrinfo(*args)

socket.getaddrinfo = new_getaddrinfo

class speed_test(object):
    def __init__(self, ip: str):
        self.ip = ip
        self.ping_max = 0
        self.ping_min = PING_MAX
        self.ping_avg = PING_MAX
        self.lost_rate = 1.0
        self.speed_max = 0
        self.speed_min = SPEED_MIN
        self.speed_avg = SPEED_MIN

    def print_ping(self):
        print(' ip:', self.ip, ', lost:', self.lost_rate * 100, ', avg:', self.ping_avg, ', max:', self.ping_max, ', min:', self.ping_min)

    def ping_failed(self):
        self.ping_max = 0
        self.ping_min = PING_MAX
        self.ping_avg = PING_MAX
        self.lost_rate = 1.0

    def ping(self, count: int, log):
        lost = 0
        all_time = 0
        for i in range(count):
            try:
                p = 0.0
                if log:
                    p = ping3.verbose_ping(self.ip)
                else:
                    p = ping3.ping(self.ip)
                p *= 1000  # get as ms
                #if self.ping_max == PING_MAX:
                self.ping_max = max(p, self.ping_max)
                #if self.ping_min == PING_MAX:
                self.ping_min = min(p, self.ping_min)
                all_time += p
            except:
                lost += 1
        if lost == count:
            self.ping_failed()
        if count == lost:
            self.ping_avg = PING_MAX
        else:
            self.ping_avg = all_time / (count - lost)
        self.lost_rate = lost / count

    def download_test(self, host, path, chunk_size, max_size, max_time, log):
        s = requests.Session()
        s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        url = 'https://%s%s' % (host, path)
        headers = {'HOST': host}

        # from https://stackoverflow.com/a/44378047
        key = (host, 443)
        value = (socket.AddressFamily.AF_INET, 0, 0, '', (self.ip, 443))
        dns_cache[key] = [value]
        try:
            response = s.get(url, headers=headers, stream = True, timeout=max_time + 1)
            content_size = int(response.headers['content-length'])
            start_tick = datetime.now()
            downloaded = 0
            for data in response.iter_content(chunk_size=chunk_size):
                if (datetime.now() - start_tick).seconds >= max_time:
                    break
                if downloaded >= max_size:
                    break
                downloaded += len(data)
            
            t = datetime.now() - start_tick
        except Exception as ex:
            print(ex)
            downloaded = 0
            t = timedelta(seconds = max_time)
        speed = downloaded / t.seconds
        if log:
            print('speed ', self.ip, ': speed:', speed)
        return speed, downloaded, t

    def speed_test(self, host, path, chunk_size, max_size, max_time, log, count: int):
        total = 0
        all_t = timedelta(seconds=0)
        for i in range(count):
            speed, downloaded, t = self.download_test(host, path, chunk_size, max_size, max_time, log)
            self.speed_max = max(speed, self.speed_max)
            self.speed_min = min(speed, self.speed_min)
            total += downloaded
            all_t += t
        self.speed_avg = total / all_t.seconds
    
    def print_speed(self):
        print(self.ip, ' avg:', self.speed_avg, ', max:', self.speed_max, ', min:', self.speed_min)

class cf_speed(object):
    def __init__(self):
        colorama.init()
        self.ip_list = []
        self.speed_list = []
        self.pinged_count = 0
        self.pinged_mutex = threading.Lock()

    def load_config(self, data):
        self.cfg = yaml.load(data, Loader=yaml.Loader)


    def load_ip_list(self):
        url = self.cfg['cloudflare']['ip_list']['url']
        print('get ip list from ', colorama.Fore.YELLOW,
              url, colorama.Style.RESET_ALL)
        result = requests.get(url)
        r = result.content.decode('utf-8')
        self.ip_list = r.splitlines()
        if self.cfg['cloudflare']['log']['ip_list']:
            print(self.ip_list)
        
        self.speed_list = []
        for ip in self.ip_list:
            st = speed_test(ip)
            self.speed_list.append(st)

        max_ip = self.cfg['cloudflare']['test']['max_ip']
        if max_ip != -1:
            self.speed_list = self.speed_list[:max_ip]

    def increase_pinged(self):
        self.pinged_mutex.acquire()
        self.pinged_count += 1
        self.pinged_mutex.release()

    def ping_ip_range(self, start, end):
        for st in self.speed_list[start:end]:
            st.ping(self.cfg['cloudflare']['test']['ping_count'], self.cfg['cloudflare']['log']['ping'])
            self.increase_pinged()

    def ping(self):
        self.pinged_count = 0
        ping_thread = self.cfg['cloudflare']['test']['ping_thread']
        if ping_thread == 1:
            for st in self.speed_list:
                st.ping(self.cfg['cloudflare']['test']['ping_count'], self.cfg['cloudflare']['log']['ping'])
        else:
            speed_count = len(self.speed_list)
            if ping_thread > speed_count:
                print(' thread count is more than speed count, fix it')
                ping_thread = speed_count
            
            step = math.ceil(speed_count / ping_thread)
            executor = ThreadPoolExecutor(ping_thread)
            for i in range(ping_thread):
                end = min(speed_count, (i + 1) * step)     
                executor.submit(self.ping_ip_range, i*step, end)
            last = 0
            with tqdm(total=speed_count) as pbar:
                while(True):
                    time.sleep(1.0)
                    pbar.update(self.pinged_count - last)
                    last = self.pinged_count
                    if self.pinged_count >= speed_count:
                        break

        self.speed_list.sort(key=lambda st: (st.lost_rate, st.ping_avg))

        self.speed_list = self.speed_list[:self.cfg['cloudflare']['result']['select_count']]

        if self.cfg['cloudflare']['log']['sorted_ping_list']:
            for st in self.speed_list:
                st.print_ping()

    def speed_test(self):
        for st in self.speed_list:
            t = self.cfg['cloudflare']['test']
            st.speed_test(t['host'], t['path'], 
                t['download_chunk'], t['download_size'], 
                t['download_time'], self.cfg['cloudflare']['log']['speed'],
                t['speed_test_count'])

        self.speed_list.sort(key=lambda st: (-st.speed_avg))
        if self.cfg['cloudflare']['log']['sorted_speed_list']:
            for st in self.speed_list:
                st.print_speed()

    def generate_openclash_config(self):
        pass


def test():
    sp = cf_speed()
    config_file = os.path.join(pathlib.Path(__file__).parent.absolute(), '../../config.yaml')
    with open(config_file, 'r', encoding='utf-8') as f:
        d = f.read()
        sp.load_config(d)
    
    sp.load_ip_list()
    sp.ping()
    sp.speed_test()
    sp.generate_openclash_config()
        
        

if __name__ == '__main__':
    test()