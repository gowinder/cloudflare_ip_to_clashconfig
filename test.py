from ruamel.yaml import YAML
import ruamel
import sys

def test():
    d = {}
    ll = ruamel.yaml.comments.CommentedSeq()
    ll.fa.set_flow_style()
    ll.append('asdf1')
    ll.append('asdf23')
    ll.append('asdf2')
    d['arr'] = ll
    mm = {}
    mm['bb'] = '122'
    mm['cc'] = '23'
    d['dd'] = mm
    yaml_dump = YAML()
    yaml_dump.indent(mapping=2, sequence=4, offset=2)
    yaml_dump.compact(seq_seq=False)
    yaml_dump.dump(d, sys.stdout)




test()