from collections import namedtuple
import csv
import math
from werkzeug.local import LocalProxy
from serafim.model.ThreeLevelEnum import ThreeLevelEnum

Rule = namedtuple('Rule', ['terms', 'target'])

TLE_LOW = ThreeLevelEnum.RENDAH
TLE_MID = ThreeLevelEnum.SEDANG
TLE_HI = ThreeLevelEnum.TINGGI

def three_int(three):
    if three == TLE_LOW: return 1
    elif three == TLE_MID: return 2
    elif three == TLE_HI: return 3
    else:
        raise Exception(f"Unknown three: {three}")

def int_three(x):
    if x == 1: return TLE_LOW
    elif x == 2: return TLE_MID
    elif x == 3: return TLE_HI
    else:
        raise Exception(f"Unknown int: {x}")

def euclid_distance(x, y):
    if (len(x) != len(y)):
        raise Exception(f"length of x and y differ: (x={x}) (y={y})")
    inner = [ pow(xi - yi, 2) for xi, yi in zip(x, y) ]
    return math.sqrt(sum(inner))

class NbRuleBase:
    def __init__(self, path):
        self.path = path
        self.data = None

    def load(self):
        data = None
        to_ints = lambda xs: tuple( int(x) for x in xs )
        with open(self.path) as f:
            reader = csv.reader(f)
            # data = [ xs for xs in reader]
            data = [ to_ints(xs) for xs in reader ]
        if data is None:
            raise Exception(f"Fail to read data")
        self.data = [ tuple(int_three(x) for x in xs) for xs in data ]

    def write(self):
        if self.data is None:
            raise Exception(f"self.data is None")
        with open(self.path, 'w') as f:
            writer = csv.writer(f)
            to_ints = lambda xs: tuple(three_int(x) for x in xs)
            for xs in map(to_ints, self.data):
                # print('xs=', xs)
                writer.writerow(xs)
        # print('data=', self.data)

    def add_rule(self, xs):
        if self.data is None:
            raise Exception(f"self.data is None")
        self.data.append(xs)

    def remove_rule(self, pos):
        self.data.pop(pos)
        self.write()

    def check_complete(self, row):
        if self.data is None:
            raise Exception(f"self.data is None")
        return row in self.data

    def check(self, row):
        if self.data is None:
            raise Exception(f"self.data is None")
        # print('row=', row)
        for xs in self.data:
            # print('xs=', xs[:-1])
            # input()
            if (row == xs[:-1]):
                return xs[-1]
        # print(row)
        # raise Exception("Fuck you")
        return None

    def check_drow(self, drow):
        row = (drow.mamulu_kaki_code, drow.mamulu_polos_code, drow.kuda_code, drow.kerbau_code, drow.sapi_code, drow.uang_code)
        return self.check(row)

    def find_most_sim(self, row):
        int_row = list(map(three_int, row))
        min_dist = 1000
        result = -1
        ints_data = [ list(map(three_int, xs)) for xs in self.data ]
        for xs in ints_data:
            dist = euclid_distance(int_row, xs[:-1])
            if dist <= min_dist:
                min_dist = dist
                result = xs[-1]
        if result == -1:
            raise Exception(f"Can't find most similar case")
        return int_three(result)

    def prediksi_code(self, drow):
        row = (
        drow.mamulu_kaki_code, drow.mamulu_polos_code, drow.kuda_code, drow.kerbau_code, drow.sapi_code, drow.uang_code)
        in_base =self.check(row)
        if (in_base == None):
            return self.find_most_sim(row)
        return in_base

    def close(self):
        pass
