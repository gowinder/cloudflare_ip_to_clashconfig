from ruamel.yaml import YAML
import pathlib
import os
import yaml
from ipaddress import IPv4Address, IPv4Network


class util():  
    from .cf_speed import open_clash
    @staticmethod
    def openclash_to_yaml(oc:open_clash, filename):
        file = os.path.join(pathlib.Path(__file__).parent.absolute(), filename)
        with open(file, 'w+', encoding='utf-8') as writer:
            #yaml.dump(clash, writer, indent=4, mapping=2, sequence=4)
            yaml_dump = YAML()
            yaml_dump.indent(mapping=2, sequence=4, offset=2)
            yaml_dump.dump(oc, writer)

    @staticmethod
    def load_yaml_file(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            d = f.read()
            return yaml.load(d, Loader=yaml.Loader)
        return None

    @staticmethod
    def extract_ip_range_to_ip(ip_list:list):
        '''extract ip range to ip, exg: 103.31.4.0/22 to 103.31.4.1 ....'''
        new_list = []
        print('ip_list count:', len(ip_list))
        for ip in ip_list:
            if ip.find('/') == -1:
                new_list.append(ip)
            else:
                ip_range = IPv4Network(ip)                
                print('range', ip, 'count:', ip_range.num_addresses)
                for ip_addr in ip_range:
                    new_list.append(str(ip_addr))
        return new_list
