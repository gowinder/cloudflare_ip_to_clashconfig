import copy
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
import humanfriendly
import ssl
from ruamel.yaml import YAML
import ruamel

class MySSLContext(ssl.SSLContext):
    def __new__(cls, server_hostname):
            return super(MySSLContext, cls).__new__(cls, ssl.PROTOCOL_SSLv23)

    def __init__(self, server_hostname):
            super(MySSLContext, self).__init__(ssl.PROTOCOL_SSLv23)
            self._my_server_hostname = server_hostname

    def change_server_hostname(self, server_hostname):
            self._my_server_hostname = server_hostname

    def wrap_socket(self, *args, **kwargs):
            kwargs['server_hostname'] = self._my_server_hostname
            return super(MySSLContext, self).wrap_socket(*args, **kwargs)

PING_MAX = 5000
SPEED_MIN = 99999999999


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
        self.speed_lost_rate = 1.0

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
                    print('ping', self.ip)
                    p = ping3.verbose_ping(self.ip)
                    print('ping result', self.ip)
                else:
                    p = ping3.ping(self.ip)
                p *= 1000  # get as ms
                #if self.ping_max == PING_MAX:
                self.ping_max = max(p, self.ping_max)
                #if self.ping_min == PING_MAX:
                self.ping_min = min(p, self.ping_min)
                all_time += p
            except Exception as ex:
                if log:
                    print('ping except: ', ex)
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
        # s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        url = 'https://%s%s' % (self.ip, path)
        headers = {'HOST': host}

        adapter = requests.adapters.HTTPAdapter()
        context = MySSLContext(host)
        adapter.init_poolmanager(10, 10, ssl_context=context)
        s.mount('https://', adapter)

        succ = True
        try:
            response = s.get(url, verify=False,
                headers=headers, stream = True,
                timeout=max_time / + 1)
            # content_size = int(response.headers['content-length'])
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
            succ = False
        if t.seconds == 0:
            t = timedelta(seconds=max_time)
        speed = downloaded / t.seconds
        if log:
            print('ip ', self.ip, ': speed:', humanfriendly.format_size(speed, binary=True))
        return succ, speed, downloaded, t

    def speed_test(self, host, path, chunk_size, max_size, max_time, log, count: int, progress_bar):
        total = 0
        all_t = timedelta(seconds=0)
        succ_count = 0
        for i in range(count):
            succ, speed, downloaded, t = self.download_test(host, path, chunk_size, max_size, max_time, log)
            if succ:
                self.speed_max = max(speed, self.speed_max)
                self.speed_min = min(speed, self.speed_min)
                total += downloaded
                all_t += t
                succ_count += 1
            progress_bar.update(1)
        if succ_count > 0 and all_t.seconds > 0:
            self.speed_avg = total / all_t.seconds
        else:
            self.speed_avg = 0
        self.speed_lost_rate = (count - succ_count) / count
    
    def print_speed(self):
        print(self.ip, ', lost:', self.speed_lost_rate, ' avg:', humanfriendly.format_size(self.speed_avg), 
            ', max:', humanfriendly.format_size(self.speed_max), 
            ', min:', humanfriendly.format_size(self.speed_min))

class cf_speed(object):
    def __init__(self):
        colorama.init()
        self.ip_list = []
        self.speed_list = []
        self.pinged_count = 0
        self.pinged_mutex = threading.Lock()

    def load_config(self, data):
        self.cfg = yaml.load(data, Loader=yaml.Loader)

    def load_config_from_dict(self, d:dict):
        self.cfg = d

    def load_ip_list(self):
        url = self.cfg['cloudflare']['ip_list']['url']
        from_file = self.cfg['cloudflare']['ip_list']['from_file']
        if from_file is not None and from_file != '':
            print('load from file...')
            with open(from_file, 'r') as reader:
                self.ip_list = reader.readlines()
        else:
            print('get ip list from ', colorama.Fore.YELLOW,
                url, colorama.Style.RESET_ALL)
            result = requests.get(url)
            r = result.content.decode('utf-8')
            self.ip_list = r.splitlines()
            if self.cfg['cloudflare']['log']['ip_list']:
                print(self.ip_list)
            
        self.speed_list = []
        for ip in self.ip_list:
            st = speed_test(ip.rstrip('\n'))
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
        t = self.cfg['cloudflare']['test']
        test_count = t['speed_test_count']
        total = len(self.speed_list) * test_count
        with tqdm(total=total) as pbar:
            for st in self.speed_list:
                st.speed_test(t['host'], t['path'], 
                    t['download_chunk'], t['download_size'], 
                    t['download_time'], self.cfg['cloudflare']['log']['speed'],
                    test_count, pbar)

        self.speed_list.sort(key=lambda st: (st.speed_lost_rate, -st.speed_avg))
        if self.cfg['cloudflare']['log']['sorted_speed_list']:
            for st in self.speed_list:
                st.print_speed()

    def generate_openclash_config(self, template):
        print(' generate open clash config file')
        clash = open_clash(template, self.speed_list, self.cfg['openclash'])

        return clash.generate_config(self.cfg['openclash']['use_ip'])        

class open_clash(object):
    def __init__(self, template, speed_list:list, clash_cfg, v2ray_list):
        self.template = template
        self.speed_list = speed_list
        self.clash_cfg = clash_cfg
        self.v2ray_list = v2ray_list
    
    def generate_config(self, use_ip:int):
        # proxy_names = ruamel.yaml.comments.CommentedSeq()
        # proxy_names.fa.set_flow_style()
        proxy_names = []
        clash = copy.deepcopy(self.template)
        proxies = clash['Proxy']
        assert(len(proxies) == 1)
        assert(proxies[0]['name'] == 'vmess-template')
        proxy_template = copy.deepcopy(proxies[0])
        clash['Proxy'] = []
        for v2ray in self.v2ray_list:
            for i in range(use_ip):
                st:speed_test = self.speed_list[i]
                new_proxy = copy.deepcopy(proxy_template)
                name = 'vmess-cf-ip-%d' % i
                proxy_names.append(name)
                new_proxy['name'] = name
                new_proxy['server'] = st.ip
                new_proxy['uuid'] = self.clash_cfg['uuid']
                new_proxy['alterId'] = self.clash_cfg['alterId']
                new_proxy['ws-path'] = self.clash_cfg['ws-path']
                new_proxy['ws-headers']['Host'] = self.clash_cfg['host']
                new_proxy['tls-hostname'] = self.clash_cfg['host']
                clash['Proxy'].append(new_proxy)
        
        clash['dns']['nameserver'] = []
        clash['dns']['nameserver'].append(self.clash_cfg['dns'])

        assert(len(proxy_names) > 0)
        fallback = proxy_names[0]
        gp = clash['Proxy Group']
        for p in gp:
            p['proxies'] = ruamel.yaml.comments.CommentedSeq()
            p['proxies'].fa.set_flow_style()
            if p['name'] == 'fallback-auto':
                p['proxies'].append('DIRECT')
            elif p['name'] == 'load-balance' or p['name'] == 'auto':
                for name in proxy_names:
                    p['proxies'].append(name)
        
        return clash


def test():
    sp = cf_speed()
    config_file = os.path.join(pathlib.Path(__file__).parent.absolute(), '../../config.yaml')
    with open(config_file, 'r', encoding='utf-8') as f:
        d = f.read()
        sp.load_config(d)
    
    sp.load_ip_list()
    sp.ping()
    sp.speed_test()

    template_file = os.path.join(pathlib.Path(__file__).parent.absolute(), '../../openclash.template.yaml')
    with open(template_file, 'r', encoding='utf-8') as f:
        d = f.read()
        template = yaml.load(d, Loader=yaml.Loader)
        clash = sp.generate_openclash_config(template)
        file = os.path.join(pathlib.Path(__file__).parent.absolute(), '../../openclash.yaml')
        with open(file, 'w+', encoding='utf-8') as writer:
            #yaml.dump(clash, writer, indent=4, mapping=2, sequence=4)
            yaml_dump = YAML()
            yaml_dump.indent(mapping=2, sequence=4, offset=2)
            yaml_dump.dump(clash, writer)
        
    print('done!')

if __name__ == '__main__':
    test()