from collections import namedtuple
from serafim.model.ThreeLevelEnum import ThreeLevelEnum

Rule = namedtuple('Rule', ['terms', 'target'])

TLE_LOW = ThreeLevelEnum.RENDAH
TLE_MID = ThreeLevelEnum.SEDANG
TLE_HI = ThreeLevelEnum.TINGGI

RULES = (
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_MID,TLE_LOW),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_MID,TLE_MID,TLE_LOW),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_MID,TLE_MID,TLE_MID,TLE_MID),
    (TLE_LOW,TLE_LOW,TLE_MID,TLE_MID,TLE_MID,TLE_MID,TLE_MID),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_HI,TLE_LOW),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_HI,TLE_HI,TLE_MID),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_HI,TLE_HI,TLE_HI,TLE_HI),
    (TLE_LOW,TLE_LOW,TLE_HI,TLE_HI,TLE_HI,TLE_HI,TLE_HI),
    (TLE_MID,TLE_MID,TLE_MID,TLE_MID,TLE_MID,TLE_HI,TLE_MID),
    (TLE_MID,TLE_MID,TLE_MID,TLE_MID,TLE_HI,TLE_HI,TLE_HI),
    (TLE_MID,TLE_MID,TLE_MID,TLE_HI,TLE_HI,TLE_HI,TLE_HI),
    (TLE_MID,TLE_MID,TLE_HI,TLE_HI,TLE_HI,TLE_HI,TLE_HI),
    (TLE_LOW,TLE_LOW,TLE_MID,TLE_MID,TLE_MID,TLE_HI,TLE_MID),
    (TLE_LOW,TLE_LOW,TLE_MID,TLE_MID,TLE_HI,TLE_HI,TLE_HI),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_MID,TLE_MID,TLE_HI,TLE_MID),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_MID,TLE_HI,TLE_HI,TLE_HI),
    (TLE_LOW,TLE_LOW,TLE_LOW,TLE_LOW,TLE_MID,TLE_HI,TLE_MID)
)

def create_terms(row):
    d = {}
    for term in row:
        if term not in d:
            d[term] = 0
        d[term] += 1
    return d


# Sort by string representation of ThreeLevelEnum
sort_pair = lambda pair: pair[0].value
def terms_equal(a, b):
    a_pairs = list(a.items())
    b_pairs = list(b.items())
    a_pairs = sorted(a_pairs, key=sort_pair)
    b_pairs = sorted(b_pairs, key=sort_pair)
    for a_pair, b_pair in zip(a_pairs, b_pairs):
        a_key, a_val = a_pair
        b_key, b_val = b_pair
        if (a_key != b_key): return False
        if (a_val != b_val): return False
    return True

def create_rules_dict():
    result = []
    for *rule, target in RULES:
        terms = create_terms(rule)
        result.append(Rule(terms=terms, target=target))
    return result

RULES_DICT = create_rules_dict()

def prediksi(row):
    '''
    Calculate prediksi based on RULES above.
    :param row: List of code of (Mamulu Kaki, Mamulu Polos, Kuda, Kerbau, Sapi, Uang)
    :return: Prediksi Code. (ThreeLevelEnum)
    '''
    input_terms = create_terms(row)
    # print('input_terms: ', input_terms)
    for idx, rule in enumerate(RULES_DICT):
        # print(f'rule-{idx}=', rule)
        if terms_equal(input_terms, rule.terms):
            return rule.target
    return TLE_LOW