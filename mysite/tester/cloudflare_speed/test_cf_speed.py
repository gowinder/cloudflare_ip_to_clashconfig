import pytest
import os
import pathlib
import yaml
from .cf_speed import speed_test, open_clash, util


def get_open_clash_template():
    template_file = os.path.join(pathlib.Path(__file__).parent.absolute(), '../../../openclash.template.yaml')
    with open(template_file, 'r', encoding='utf-8') as f:
        d = f.read()
        template = yaml.load(d, Loader=yaml.Loader)
        return template

def get_v2ray_list():
    return [
        {'alias': 'v1',
        'uuid': 'test-uuid-1',
        'alterId': '1',
        'ws-path': '/test_path_1/',
        'host': 'test_host_1'},
        {'alias': 'v2',
        'uuid': 'test-uuid-2',
        'alterId': '2',
        'ws-path': '/test_path_2/',
        'host': 'test_host_2'},
        {'alias': 'v3',
        'uuid': 'test-uuid-3',
        'alterId': '3',
        'ws-path': '/test_path_3/',
        'host': 'test_host_3'}
    ]

def test_generate_config():
    tempate_file = get_open_clash_template()
    speed_list = [speed_test('1.1.1.1'), 
        speed_test('2.2.2.2'),
        speed_test('3.3.3.3')]
    clash_config = {}
    clash_config['dns'] = '114.114.114.114'
    v2ray_list = get_v2ray_list()
    oc = open_clash(tempate_file, speed_list, clash_config, v2ray_list)
    oc_config = oc.generate_config(len(speed_list))
    assert(oc_config is not None)
    test_output_openclash = 'test/openclash_test_generated.yaml'
    util.openclash_to_yaml(oc_config, test_output_openclash)
    
    loaded_file = os.path.join(pathlib.Path(__file__).parent.absolute(), test_output_openclash)
    with open(loaded_file, 'r', encoding='utf-8') as f:
        d = f.read()
        oc_loaded = yaml.load(d, Loader=yaml.Loader)
        assert(len(oc_loaded['Proxy']) == len(v2ray_list) * len(speed_list))

    