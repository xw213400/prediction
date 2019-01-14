#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import contract
import key
import numpy as np
from matplotlib import pyplot as plt
import json
import math

CONTRACTS = {}

def draw(profits):
    plt.plot(profits)
    plt.show()

def sharpe(profits, cash=1):
    a = [p/cash for p in profits]
    mean = np.mean(a)
    stdev = np.std(a)

    if stdev != stdev or stdev == 0:
        return 0

    return mean / stdev

def optimize(ct):
    ctt = CONTRACTS[ct.name]
    key.TICK_PRICE = ctt['tick']
    key.COST = 0#key.TICK_PRICE * 0.5
    key.SLIDE = 0#key.TICK_PRICE * 1
    trader = key.Trader(ct.bars)
    scores = []
    costmoney = ctt['marg'] / ctt['unit']
    for i in range(7):
        period = i + 3
        for j in range(period):
            ndays = period-j
            trader.initKey(period, ndays)
            trader.traceback()
            score = trader.profits[-1] / costmoney
            trade = len(trader.trades)
            name = "%d_%d"%(period, ndays)
            scores.append({'name':name, 'score':score, 'trade':trade, 'nKeys':trader.nKeys, 'sharpe':sharpe(trader.profits, costmoney)})

    scores.sort(key = lambda record: record['score'], reverse = True)

    return scores

def simulate(cts, period, ndays):
    results = []
    for ct in cts:
        ctt = CONTRACTS[ct.name]
        key.TICK_PRICE = ctt['tick']
        key.COST = key.TICK_PRICE * 0.5
        key.SLIDE = key.TICK_PRICE * 1
        costmoney = ctt['marg'] / ctt['unit']
        trader = key.Trader(ct.bars)
        trader.initKey(period, ndays)
        trader.traceday()
        score = trader.profits[-1] / costmoney
        text = "%s\t%.3f\t%.3f\t%d\t%d" % (ct.name, score, sharpe(trader.profits, costmoney), trader.nKeys, len(trader.trades))
        results.append({'text':text, 'score':score})
        print("%s\t%d" % (ct.name, len(trader.days)))

    results.sort(key = lambda result: result['score'], reverse = True)
    for result in results:
        print(result['text'])


def optimizeAll(cts):
    records = {}
    for ct in cts:
        ctt = CONTRACTS[ct.name]
        key.TICK_PRICE = ctt['tick']
        key.COST = key.TICK_PRICE * 0.5
        key.SLIDE = key.TICK_PRICE * 1
        costmoney = ctt['marg'] / ctt['unit']
        trader = key.Trader(ct.bars)
        for i in range(7):
            period = i + 3
            for j in range(period):
                ndays = period-j
                trader.initKey(period, ndays)
                trader.traceday()
                score = trader.profits[-1] / costmoney
                trade = len(trader.trades)
                nKeys = trader.nKeys
                name = "%d_%d"%(period, ndays)
                record = records.get(name)
                if record is None:
                    records[name] = {'name':name, 'score':score, 'trade':trade, 'nKeys':nKeys, 'profits':trader.profits.copy()}
                else:
                    record['score'] += score
                    record['trade'] += trade
                    record['nKeys'] += nKeys
                    ppp = record['profits']
                    n1 = len(ppp)
                    n2 = len(trader.profits)
                    n = min(n1, n2)
                    dn = n2 - n1
                    ii = 1
                    while ii <= n:
                        ppp[-ii] += trader.profits[-ii] / costmoney
                        ii += 1
                    ii = 0
                    while ii < dn:
                        ppp.insert(0, trader.profits[ii] / costmoney)
                        ii += 1
        print(ct.name)

    scores = []
    for name in records:
        record = records[name]
        record['score'] /= len(cts)
        record['trade'] /= len(cts)
        record['nKeys'] /= len(cts)
        record['sharpe'] = sharpe(record['profits'], len(cts))
        scores.append(record)

    scores.sort(key = lambda record: record['score'], reverse = True)
    for record in scores:
        print("%s\t%.3f\t%.3f\t%d\t%d" % (record['name'], record['score'], record['sharpe'], record['nKeys'], record['trade']))

    return scores


def main():
    global CONTRACTS

    with open('contracts.json') as json_data:
        CONTRACTS = json.load(json_data)

    folder = 'fdata_15_18_9/'
    cts = []
    files = [f for f in listdir(folder) if f[-4:] == '.txt']
    for f in files:
        with open(folder+f) as text:
            ct = contract.Contract(f[0:-6], text)
            cts.append(ct)

    # results = []
    # for ct in cts:
    #     scores = optimize(ct)
    #     score = scores[0]
    #     result = "%s\t%s\t%.3f\t%.3f\t%d\t%d" % (ct.name, score['name'], score['score'], score['sharpe'], score['nKeys'], score['trade'])
    #     results.append({'text':result, 'score':score['score'], 'sharpe':score['sharpe']})
    #     print(result)
    # print("==========")
    # results.sort(key = lambda result: result['score'], reverse = True)
    # for result in results:
    #     print(result['text'])
    # print("==========")
    # results.sort(key = lambda result: result['sharpe'], reverse = True)
    # for result in results:
    #     print(result['text'])

    # scores = optimizeAll(cts)
    # draw(scores[0]['profits'])

    simulate(cts, 8, 8)

    # name = 'RB'
    # with open('../futures-data/30#'+name+'1901.txt') as text:
    #     ct = contract.Contract(name, text)
    #     ctt = CONTRACTS[ct.name]
    #     key.TICK_PRICE = ctt['tick']
    #     key.COST = key.TICK_PRICE * 0.5
    #     key.SLIDE = key.TICK_PRICE * 1
    #     cash = ctt['marg'] * ctt['unit']
    #     trader = key.Trader(ct.bars)
    #     trader.initKey(8, 7)
    #     trader.traceback()
    #     trader.debugTrade()
    #     sss = sharpe(trader.profits, cash)
    #     print("%s: %.3f, %d, %f" % (ct.name, trader.profits[-1], len(trader.trades), sss))
    #     draw(trader.profits)


if __name__ == '__main__':
    main()