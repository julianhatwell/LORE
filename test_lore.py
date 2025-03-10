from . import util
from . import lore
from . import neighbor_generator as ng

from sklearn.model_selection import train_test_split
import numpy as np
import warnings
warnings.filterwarnings("ignore")


def main(dataset, path_data, blackbox, log=False):

    X, y = dataset['X'], dataset['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)


    blackbox.fit(X_train, y_train)

    X2E = X_test
    y2E = blackbox.predict(X2E)
    y2E = np.asarray([dataset['possible_outcomes'][i] for i in y2E])

    idx_record2explain = 0

    explanation, infos = lore.explain(idx_record2explain, X2E, dataset, blackbox,
                                      ng_function=ng.genetic_neighborhood,
                                      discrete_use_probabilities=True,
                                      continuous_function_estimation=False,
                                      returns_infos=True,
                                      path=path_data, sep=';', log=log)

    dfX2E = util.build_df2explain(blackbox, X2E, dataset).to_dict('records')
    dfx = dfX2E[idx_record2explain]
    x = util.build_df2explain(blackbox, X2E[idx_record2explain].reshape(1, -1), dataset).to_dict('records')[0]

    print('x = %s' % dfx)
    print('r = %s --> %s' % (explanation[0][1], explanation[0][0]))
    for delta in explanation[1]:
        print('delta', delta)

    covered = lore.get_covered(explanation[0][1], dfX2E, dataset)
    print(len(covered))
    print(covered)

    print(explanation[0][0][dataset['class_name']], '<<<<')

    def eval(x, y):
        return 1 if x == y else 0

    precision = [1-eval(v, explanation[0][0][dataset['class_name']]) for v in y2E[covered]]
    print(precision)
    print(np.mean(precision), np.std(precision))

    return()