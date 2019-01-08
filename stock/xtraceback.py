#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
from matplotlib import pyplot as plt
import stock
import policy
import numpy as np
from matplotlib import pyplot as plt

def draw(history):
    plt.plot(history)
    plt.show()

def sharpe(history):
    a = [1]
    i = 1
    while i < len(history):
        a.append(history[i]/history[i-1]-1)
        i+=1
    mean = np.mean(a)
    stdev = np.std(a)
    return mean / stdev


def main():
    with open('513050.txt') as text:
        st = stock.Stock(text)
        py = policy.Policy(400000)

        #10, 4, 0.052, 1.2997

        py.init(10, 0.052, 4)
        history = py.traceback(st.bars)
        print(history[-1])
        # draw(history)

        # scores = []
        # for i in range(10):
        #     period = 5 + i
        #     for j in range(10):
        #         step = 3 + j
        #         for k in range(40):
        #             delta = 0.03 + 0.001 * k
        #             py.init(period, delta, step)
        #             history = py.traceback(st.bars)
        #             score = history[-1]
        #             scores.append({'w':score, 'p':period, 's':step, 'd':delta, 'sp':sharpe(history)})
        #         print("i:%d, j:%d" % (i, j))

        # scores.sort(key = lambda score: score['w'], reverse = True)
        # for i in range(100):
        #     score = scores[i]
        #     print("%d, %d, %.3f, %.4f, %f" % (score['p'], score['s'], score['d'], score['w'], score['sp']))


if __name__ == '__main__':
    main()