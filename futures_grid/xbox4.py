#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import contract
import box4
import numpy as np
from matplotlib import pyplot as plt
import json

CONTRACTS = {}

def draw(trader):
    plt.plot(trader.dates, trader.profits)
    # plt.plot(trader.dates, trader.prices)
    # plt.plot(trader.uppers)
    # plt.plot(trader.lowers)
    # plt.plot(trader.hhs)
    # plt.plot(trader.lls)
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

def traceback(ct, trader):
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

def tracebackall(cts, trader):
    scores = []
    for i in range(8):
        period = 2 + i
        for j in range(7):
            ratio = 0.3 + 0.1 * j
            ctscores = 0
            tradecount = 0
            for ct in cts:
                ctt = CONTRACTS[ct.name]
                box4.TICK_PRICE = ctt['tick']
                box4.COST = box4.TICK_PRICE * 0.5
                box4.SLIDE = box4.TICK_PRICE * 1
                trader.init(period, ratio)
                trader.traceback(ct.bars)
                score = trader.profits[-1] / ctt['marg'] * ctt['unit'] / 2
                ctscores += score
                tradecount += len(trader.trades)
            ctscores /= len(cts)
            tradecount /= len(cts)
            print("[%d,%.3f]\t%.4f\t%d"%(period,ratio,ctscores,tradecount))
            scores.append({'w':ctscores, 'p':period, 'r':ratio, 'tn':tradecount})

    print('\n')
    scores.sort(key = lambda score: score['w'], reverse = True)
    for i in range(30):
        score = scores[i]
        print("{%d,%.3f}\t%.4f\t%d" % (score['p'], score['r'], score['w'], score['tn']))


def main():
    global CONTRACTS

    with open('contracts.json') as json_data:
        CONTRACTS = json.load(json_data)

    # cts = []
    # files = [f for f in listdir('../futures-data') if f[-4:] == '.txt']
    # for f in files:
    #     with open('../futures-data/'+f) as text:
    #         ct = contract.Contract(f[3:-8], text)
    #         cts.append(ct)

    trader = box4.Trader()

    with open('../futures-data/28#TA1901.txt') as text:
        ct = contract.Contract('TA', text)
    # for ct in cts:
        box4.TICK_PRICE = CONTRACTS[ct.name]['tick']
        box4.COST = box4.TICK_PRICE * 0.5
        box4.SLIDE = box4.TICK_PRICE * 2

        trader.init(10, 0.7)
        trader.traceback(ct.bars)
        print("%s: %.3f, %d" % (ct.name, trader.profits[-1], len(trader.trades)))
        draw(trader)
    
    # trader.debugTrade()

    # tracebackall(cts, trader)


if __name__ == '__main__':
    main()