#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import contract
import level4
import numpy as np
from matplotlib import pyplot as plt
import json

CONTRACTS = {}

def draw(trader):
    plt.plot(trader.dates, trader.profits)
    # plt.plot(trader.dates, trader.prices)
    # plt.plot(trader.dates, trader.mas)
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

def optimize(ct, trader):
    scores = []
    for i in range(8):
        period = 2 + i
        for k in range(20):
            band = 0.005 + 0.001 * k
            trader.init(period, band)
            trader.traceback(ct.bars)
            scores.append({'w':trader.profits[-1], 'p':period, 'b':band, 'sp':sharpe(trader.profits), 'tn':len(trader.trades)})
            # print("i:%d, k:%d" % (i, k))

    scores.sort(key = lambda score: score['w'], reverse = True)
    for i in range(10):
        score = scores[i]
        print("%d, %.3f, %.1f, %d" % (score['p'], score['b'], score['w'], score['tn']))

def optimizeGRID(cts, trader):
    scores1 = []
    for i in range(5):
        level4.PERIOD_GRID = 2 + i
        for j in range(10):
            level4.BAND_GRID = 0.02 + 0.001 * j
            ctscores = 0
            tradecount = 0
            for ct in cts:
                ctt = CONTRACTS[ct.name]
                level4.TICK_PRICE = ctt['tick']
                level4.COST = level4.TICK_PRICE * 0.5
                level4.SLIDE = level4.TICK_PRICE * 1
                trader.traceback(ct.bars, [level4.GridOrder(1), level4.GridOrder(-1)])
                score = trader.profits[-1] / ctt['marg'] * ctt['unit']
                ctscores += score
                tradecount += len(trader.trades)
            ctscores /= len(cts)
            tradecount /= len(cts)
            print("[%d, %.3f]\t%.4f\t%d"%(level4.PERIOD_GRID, level4.BAND_GRID, ctscores,tradecount))
            scores1.append({'w':ctscores, 'p':level4.PERIOD_GRID, 'b':level4.BAND_GRID, 'tn':tradecount})

    print('\n')
    scores1.sort(key = lambda score: score['w'], reverse = True)
    for i in range(20):
        score = scores1[i]
        print("{%d, %.3f}\t%.4f\t%d" % (score['p'], score['b'], score['w'], score['tn']))

def optimizeMA(cts, trader):
    scores2 = []
    for i in range(5):
        level4.PERIOD_MA = 5 + i*3
        for j in range(10):
            level4.BAND_MA = 0.01 + 0.005 * j
            ctscores = 0
            tradecount = 0
            for ct in cts:
                ctt = CONTRACTS[ct.name]
                level4.TICK_PRICE = ctt['tick']
                level4.COST = level4.TICK_PRICE * 0.5
                level4.SLIDE = level4.TICK_PRICE * 1
                trader.traceback(ct.bars, [level4.MAOrder()])
                score = trader.profits[-1] / ctt['marg'] * ctt['unit']
                ctscores += score
                tradecount += len(trader.trades)
            ctscores /= len(cts)
            tradecount /= len(cts)
            print("[%d, %.3f]\t%.4f\t%d"%(level4.PERIOD_MA, level4.BAND_MA, ctscores,tradecount))
            scores2.append({'w':ctscores, 'p':level4.PERIOD_MA, 'b':level4.BAND_MA, 'tn':tradecount})

    print('\n')
    scores2.sort(key = lambda score: score['w'], reverse = True)
    for i in range(10):
        score = scores2[i]
        print("{%d, %.3f}\t%.4f\t%d" % (score['p'], score['b'], score['w'], score['tn']))


def main():
    global CONTRACTS

    with open('contracts.json') as json_data:
        CONTRACTS = json.load(json_data)

    cts = []
    files = [f for f in listdir('../futures-data') if f[-4:] == '.txt']
    for f in files:
        with open('../futures-data/'+f) as text:
            ct = contract.Contract(f[3:-8], text)
            cts.append(ct)

    trader = level4.Trader()

    level4.PERIOD_MA = 14
    level4.BAND_MA = 0.035

    level4.PERIOD_GRID = 3
    level4.BAND_GRID = 0.03

    # with open('../futures-data/30#PB1901.txt') as text:
    #     ct = contract.Contract('JM', text)

    for ct in cts:
        level4.TICK_PRICE = CONTRACTS[ct.name]['tick']
        level4.COST = level4.TICK_PRICE * 0.5
        level4.SLIDE = level4.TICK_PRICE * 1

        trader.traceback(ct.bars, [level4.MAOrder()])
        print("%s: %.3f, %d" % (ct.name, trader.profits[-1], len(trader.trades)))
        # draw(trader)

    # optimizeGRID(cts, trader)
    # optimizeMA(cts, trader)


if __name__ == '__main__':
    main()