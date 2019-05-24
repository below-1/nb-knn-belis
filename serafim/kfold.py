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
    # print('len_parts=', len(partitions))
    # print('len_part_1=', len(partitions[0]))
    # print('len_part_2=', len(partitions[1]))
    # print('len_part_3=', len(partitions[2]))
    total_hit = 0
    total_miss = 0
    total_accuracy = 0
    parts_result = []
    for idx in range(k):
        test = partitions[idx]
        train = [ x for i in range(k) if i != idx for x in partitions[i] ]
        # print('train======')
        # print()
        # print('part=', idx+1)
        # print(f"len_train: {len(train)}")
        total_1 = [ x[1] for x in train if x[1] == 1 ]
        total_2 = [ x[1] for x in train if x[1] == 2 ]
        total_0 = [ x[1] for x in train if x[1] == 0 ]
        # print('total_0 = ', len(total_0))
        # print('total_1 = ', len(total_1))
        # print('total_2 = ', len(total_2))

        test_1 = [x[1] for x in test if x[1] == 1]
        test_2 = [x[1] for x in test if x[1] == 2]
        test_0 = [x[1] for x in test if x[1] == 0]
        # print('test_0 = ', len(test_0))
        # print('test_1 = ', len(test_1))
        # print('test_2 = ', len(test_2))
        nb = NaiveBayesV2(train, 6)
        part_result = test_part(nb, test)
        # print()
        # if (idx > 0):
        #     print('part_result=', part_result)
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
    nb.build()
    for vector, target, id in test_data:
        classification = nb.classify(vector)
        knn_result = nb.knn(vector, classification.clazz)
        single_result = nb.run(vector)
        single_row_result = SingleRowResult(
                              vector=vector,
                              target=target,
                              id=id,
                              system=classification.clazz,
                              similarity=knn_result.similarity)
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