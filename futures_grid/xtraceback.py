#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import contract
import gridma
import numpy as np
from matplotlib import pyplot as plt

CONTRACTS = {
    '28#FG1901.txt':{
        'tick':1,
        'cost':0.5,
        'marg':3154 / 20 / 2
    },
    '29#JM1901.txt': {
        'tick':0.5,
        'cost':0.25,
        'marg':11366 / 60 / 2
    }
}

def draw(grid):
    plt.plot(grid.dates, grid.profits)
    # plt.plot(grid.dates, grid.prices)
    # plt.plot(grid.dates, grid.mas)
    plt.show()

def sharpe(history):
    a = [1]
    i = 1
    while i < len(history):
        a.append((history[i]+1000000)/(history[i-1]+1000000)-1)
        i+=1
    mean = np.mean(a)
    stdev = np.std(a)
    return mean / stdev

def traceback(ct, grid):
    scores = []
    for i in range(8):
        period = 1 + i
        for k in range(20):
            band = 0.005 + 0.001 * k
            grid.init(period, band)
            grid.traceback(ct.bars)
            scores.append({'w':grid.profits[-1], 'p':period, 'b':band, 'sp':sharpe(grid.profits), 'tn':len(grid.trades)})
            # print("i:%d, k:%d" % (i, k))

    scores.sort(key = lambda score: score['w'], reverse = True)
    for i in range(10):
        score = scores[i]
        print("%d, %.3f, %.1f, %d" % (score['p'], score['b'], score['w'], score['tn']))

def tracebackall(cts, grid):
    scores = []
    for i in range(8):
        period = 1 + i
        for k in range(20):
            band = 0.005 + 0.001 * k
            ctscores = 0
            for ct in cts:
                gridma.TICK_PRICE = CONTRACTS[ct.name]['tick']
                gridma.COST = CONTRACTS[ct.name]['cost']
                grid.init(period, band)
                grid.traceback(ct.bars)
                ctscores += grid.profits[-1] / CONTRACTS[ct.name]['marg']
            scores.append({'w':ctscores, 'p':period, 'b':band})

    scores.sort(key = lambda score: score['w'], reverse = True)
    for i in range(10):
        score = scores[i]
        print("%d, %.3f, %.1f, %d" % (score['p'], score['b'], score['w'], score['tn']))

def main():
    grid = gridma.Grid()

    # with open('data/28#SR1901.txt') as text:
    #     ct = contract.Contract(text)
    #     traceback(ct, grid)
        # grid.init(1, 0.03)
        # grid.traceback(ct.bars)
        # grid.debugTrade()
        # draw(grid)

    cts = []

    files = [f for f in listdir('../futures-data') if f[-4:] == '.txt']
    for f in files:
        with open('../futures-data/'+f) as text:
            gridma.TICK_PRICE = CONTRACTS[f]['tick']
            gridma.COST = CONTRACTS[f]['cost']
            ct = contract.Contract(f, text)
            cts.append(ct)

    tracebackall(cts, grid)
    
    # for ct in cts:
    #     print(ct.name)
    #     traceback(ct, grid)
    #     print('\n')


if __name__ == '__main__':
    main()