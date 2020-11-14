from .util import util
import pathlib
import os
import shutil


def test_load_yaml_file():
    file = os.path.join(pathlib.Path(__file__).parent.absolute(), 
        '../../../openclash.template.yaml')
    data = util.load_yaml_file(file)
    assert data != None
    assert data['Proxy'] != None
    assert data['Proxy'][0]['name'] == 'vmess-template'

def test_extract_ip_range_to_ip():
    test_ip_list = ['192.168.2.1', '192.168.1.0/24', '10.0.0.1/32']
    result_ip_list = util.extract_ip_range_to_ip(test_ip_list)
    assert result_ip_list != None
    assert len(result_ip_list) == (1 + 256 + 1)
    assert result_ip_list[0] == '192.168.2.1'

def test_mkdir():
    path = os.path.join(pathlib.Path(__file__).parent.absolute(),
        'test/test_mkdir')
    shutil.rmtree(path, ignore_errors=True)
    assert not os.path.exists(path)
    util.mkdir(path)
    assert os.path.exists(path)
    shutil.rmtree(path)