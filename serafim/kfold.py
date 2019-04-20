from serafim.nb import NaiveBayesV2
from serafim.model import converter
from collections import namedtuple

SingleRowResult = namedtuple('SingleRowResult', ['vector', 'target', 'id', 'system', 'similarity'])
PartResult = namedtuple('PartResult', ['rows_result', 'accuracy', 'total_hit', 'total_miss'])
WholeResult = namedtuple('WholeResult', ['parts_result', 'accuracy', 'total_hit', 'total_miss'])

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def kfold(dataset, k=10):
    partitions = list(split(dataset, k))
    total_hit = 0
    total_miss = 0
    total_accuracy = 0
    parts_result = []
    for idx in range(k):
        test = partitions[idx]
        train = [ x for i in range(k) if i != idx for x in partitions[i] ]
        nb = NaiveBayesV2(train, 6)
        part_result = test_part(nb, test)
        parts_result.append(part_result)
        total_hit += part_result.total_hit
        total_miss += part_result.total_miss
        total_accuracy += part_result.accuracy

    accuracy = total_accuracy * 1.0 / k
    return WholeResult(
        parts_result=parts_result,
        accuracy=accuracy,
        total_hit=total_hit,
        total_miss=total_miss
    )

def test_part(nb, test_data):
    rows_result = []
    for vector, target, id in test_data:
        single_result = nb.run(vector)
        single_row_result = SingleRowResult(
                              vector=vector,
                              target=target,
                              id=id,
                              system=single_result['max_nb_class_id'],
                              similarity=single_result['max_knn_sim'])
        rows_result.append(single_row_result)

    total_sim = 0
    total_hit = 0
    for result in rows_result:
        if result.target == result.system:
            total_hit += 1
        total_sim += result.similarity
    total_miss = (len(test_data)) - total_hit
    accuracy = 1.0 * total_hit / len(test_data)

    return PartResult(
        rows_result=rows_result,
        accuracy=accuracy,
        total_hit=total_hit,
        total_miss=total_miss
    )