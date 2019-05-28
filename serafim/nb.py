from collections import namedtuple
from serafim.model import DsetRow

Classification = namedtuple('Classification', ['max_prob', 'clazz'])
KnnResult = namedtuple('KnnResult', ['similarity', 'selected_ids'])

class NaiveBayesV2:
    '''
      Multinomial naive bayes for binary category implementation with ordered attributes.
      rows: array of ( set([ attributes here.. ]), target, id )
    '''

    def __init__(self, rows, n_attr):
        if len(rows) == 0:
            raise Exception("Failure: Rows can't be empty")
        self.rows = rows
        self.n_attr = n_attr
        self.attributes_summary = None
        self.class_summary = None

    def summarize_classes(self):
        result = {}
        for _, target, __ in self.rows:
            if (target not in result):
                result[target] = 0
            result[target] += 1
        return result

    def summarize_attributes_by_class(self, _class):
        result = [
            dict() for i in range(self.n_attr)
        ]
        filter_by_class = lambda row: row[1] == _class
        # print('class=', _class)
        # print('items=', list(filter(filter_by_class, self.rows)))
        for attr_row, _, __ in filter(filter_by_class, self.rows):
            # print('our list object=', list(enumerate(attr_row)))
            # input()
            for attr_idx, attr_val in enumerate(attr_row):
                if attr_val not in result[attr_idx]:
                    result[attr_idx][attr_val] = 0
                result[attr_idx][attr_val] = result[attr_idx][attr_val] + 1
                # print(result)
                # input()
        #     print('after loop result=', result)
        # print('after func result=', result)
        return result

    def build(self):
        self.class_summary = self.summarize_classes()
        self.attributes_summary = {}
        for _class in self.class_summary.keys():
            summ = self.summarize_attributes_by_class(_class)
            self.attributes_summary[_class] = summ
        # for k in self.attributes_summary.keys():
        #     print(f"\t{k}")
        #     for _dict in self.attributes_summary[k]:
        #         for _k, _v in _dict.items():
        #             print(f"\t\t{_k} = {_v}")
        #         print()

    def classify(self, attr_row):
        total_case = len(self.rows)
        result = []
        print(self.attributes_summary)
        for clz in self.class_summary.keys():
            # This could be zero
            count_clz = self.class_summary.get(clz, 0) * 1.0  # Multiply by float to promote the type
            # print('count_clz=', count_clz)
            # print('total_case=', total_case)
            prob_clz = (count_clz + 1) / (total_case + 1)

            prob_attrs = [
                # This could be zero
                self.attributes_summary[clz][attr_idx].get(attr_val, 0.0) / (count_clz + 1)
                # This will be float, because we divided by float
                for (attr_idx, attr_val) in enumerate(attr_row)]
            total_prod = 1
            for prob_attr in prob_attrs:
                total_prod *= prob_attr
            total_prod *= prob_clz
            print(f'{clz} --> {total_prod}')
            # print()

            result.append((clz, total_prod))

        sorted_result = sorted(result, key=lambda pair: pair[1], reverse=True)
        max_clz, max_prob = sorted_result[0]
        return Classification(max_prob=max_prob, clazz=max_clz)

    def knn(self, attr_row, clazz):
        # Run knn
        max_sim = -1
        max_row_id = -1
        max_row_ids = set()
        rows_with_sim = []
        for row in self.rows:
            attrs, target, id = row
            if target != clazz: continue

            # Count the same element at same position
            total_same_elements = sum([
                1 if input_attr_val == data_attr_val else 0
                for (input_attr_val, data_attr_val) in zip(attr_row, attrs)
            ])
            # Difference between elements just difference between total_element and total_same_element
            # Total element is equal the dimension of input of course.
            total_diff_element = self.n_attr - total_same_elements

            # I guess we could substract directly with self.dimension
            # For now let's follow the rule.
            sim = total_same_elements * 1.0 / (total_same_elements + total_diff_element)

            if sim > max_sim:
                max_sim = sim
                max_row_id = id
            rows_with_sim.append((row, sim))

        # Find all row with highest similarity
        selected_rows = [ row for row, sim in rows_with_sim if sim == max_sim ]
        selected_ids = [ id for _, __, id in selected_rows ]
        return KnnResult(similarity=max_sim, selected_ids=selected_ids)


    def run(self, attr_row):
        if len(attr_row) != self.n_attr:
            raise Exception('Dimension of input not match')

        class_summary = self.summarize_classes()
        attributes_summary = {}
        for _class in class_summary.keys():
            summ = self.summarize_attributes_by_class(_class)
            attributes_summary[_class] = summ

        # print(f"class_summary={class_summary}")
        # print(f"attributes_summary={attributes_summary}")

        total_case = len(self.rows)
        result = []
        for clz in class_summary.keys():
            # This could be zero
            count_clz = class_summary.get(clz, 0) * 1.0 # Multiply by float to promote the type
            prob_clz = (count_clz * 1.0) + 1 / (total_case + 1)

            prob_attrs = [
                # This could be zero
                (attributes_summary[clz][attr_idx].get(attr_val, 0.0) + 1) / count_clz # This will be float, because we divided by float
                for (attr_idx, attr_val) in enumerate(attr_row) ]
            total_prod = 1
            for prob_attr in prob_attrs:
                total_prod *= prob_attr
            total_prod *= prob_clz

            result.append((clz, total_prod))

        sorted_result = sorted(result, key=lambda pair: pair[1], reverse=True)
        # print(class_summary)
        # print()
        max_clz, max_prob = sorted_result[0]

        # Run knn
        max_sim = -1
        max_row_id = -1
        max_row_ids = set()
        rows_with_sim = []
        for row in self.rows:
            attrs, target, id = row
            # Count the same element at same position
            total_same_elements = sum([
                1 if input_attr_val == data_attr_val else 0
                for (input_attr_val, data_attr_val) in zip(attr_row, attrs)
            ])
            # Difference between elements just difference between total_element and total_same_element
            # Total element is equal the dimension of input of course.
            total_diff_element = self.n_attr - total_same_elements

            # I guess we could substract directly with self.dimension
            # For now let's follow the rule.
            sim = total_same_elements * 1.0 / (total_same_elements + total_diff_element)

            if sim > max_sim:
                max_sim = sim
                max_row_id = id
            rows_with_sim.append((row, sim))
        max_sim = max([ sim for _, sim in rows_with_sim ])
        selected_rows = [ row for row, sim in rows_with_sim if sim == max_sim ]

        return {
            'max_nb_class_id': max_clz,
            'max_nb_prob': max_prob,
            'max_knn_row_id': max_row_id,
            'max_knn_sim': max_sim
        }

def construct_solution(db_session, ids):
    selected = db_session.query(DsetRow).filter(DsetRow.id.in_(ids)).all()

    attrs = [
        (s.mamuli_kaki, s.mamuli_polos, s.kuda, s.kerbau, s.sapi, s.uang)
        for s in selected
    ]
    n_sr = len(ids)

    zipped_attrs = list(zip(*attrs))
    attr_result = [ int(sum(xs) * 1.0 / n_sr) for xs in zipped_attrs ]
    return attr_result