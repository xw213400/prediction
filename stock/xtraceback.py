#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import stock
import policy
import numpy as np
from matplotlib import pyplot as plt

def draw(history, prices):
    list2 = [p / prices[0] for p in prices]
    plt.plot(history)
    plt.plot(list2)
    plt.show()

def sharpe(profits, cash=1):
    a = [p/cash for p in profits]
    # for p in profits:
    #     a.append(p / cash)
    mean = np.mean(a)
    stdev = np.std(a)

    if stdev != stdev or stdev == 0:
        return 0

    return mean / stdev


def main():
    with open('etf/510300.txt') as text:
        st = stock.Stock(text)
        py = policy.Policy(400000)

        #10, 4, 0.056, 1.2997

        py.init(11, 0.076, 4)
        history = py.traceback(st.bars)
        print(history[-1])
        print(sharpe(history))
        draw(history, py.closes)

        # scores = []
        # for i in range(10):
        #     period = 5 + i
        #     for j in range(5):
        #         step = 4 + j
        #         for k in range(40):
        #             delta = 0.04 + 0.001 * k
        #             py.init(period, delta, step)
        #             history = py.traceback(st.bars)
        #             score = history[-1]
        #             scores.append({'w':score, 'p':period, 's':step, 'd':delta, 'sp':sharpe(history), 'tn':py.trade})
        #     print(period)

        # scores.sort(key = lambda score: score['w'], reverse = True)
        # for i in range(30):
        #     score = scores[i]
        #     print("%d, %.3f, %d, %.4f, %f, %d" % (score['p'], score['d'], score['s'], score['w'], score['sp'], score['tn']))


if __name__ == '__main__':
    main()