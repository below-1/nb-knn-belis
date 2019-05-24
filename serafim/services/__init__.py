from werkzeug.local import LocalProxy
from flask import g
from serafim.model.rules import NbRuleBase

def _get_nrb():
    if 'nrb' not in g:
        path = 'serafim/model/rule.csv'
        nrb = NbRuleBase(path)
        nrb.load()
        g.nrb = nrb
    # print('nrb.data=', g.nrb.data)
    return g.nrb

nrb = LocalProxy(_get_nrb)
