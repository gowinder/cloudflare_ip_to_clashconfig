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

PING_MAX = 5000
SPEED_MIN = 0


class speed_test(object):
    def __init__(self, ip: str):
        self.ip = ip
        self.ping_max = 0
        self.ping_min = PING_MAX
        self.ping_avg = PING_MAX
        self.lost_rate = 1.0
        self.speed_max = 0
        self.speed_min = 0
        self.speed_avg = 0

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

    def speed_test(self, count: int, time):
        pass


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

        for st in self.speed_list:
            st.print_ping()

    def speed_test(self):
        pass

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