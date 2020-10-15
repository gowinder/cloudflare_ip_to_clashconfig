import yaml


class speed_test(object):
    def __init__(self, ip:str):
        self.ip = ip
        self.ping_max = 5000
        self.ping_min = 5000
        self.ping_avg = 5000
        self.speed_max = 0
        self.speed_min = 0
        self.speed_avg = 0
    
    def ping(self, count:int):
        pass

    def speed_test(self, count: int, time):
        pass

class cf_speed(object):
    def __init__(self):
        self.ip_list = []

    def load_config(self, cfg):
        self.cfg = cfg

    def load_ip_list(self):
        pass

    def ping(self):
        pass

    def speed_test(self):
        pass
    
