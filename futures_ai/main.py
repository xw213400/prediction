#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import contract
from matplotlib import pyplot as plt
import conv

def drawHist(data):
    plt.hist(data, 100)
    plt.xlabel('X')
    plt.ylabel('y')
    plt.title('OUT')
    plt.show()

def train(datas):
    print(len(datas))
    cv = conv.Conv(32)
    conv.train(datas, cv, 10)

def main():
    files = [f for f in listdir('data') if f[-4:] == '.txt']
    for f in files:
        with open('data/'+f) as text:
            ct = contract.Contract(text)
            datas = ct.getDataset(conv.ILen, conv.OLen)
            n = len(datas)
            datas.sort(key = lambda rec: abs(rec.output), reverse = True)
            train(datas[0:int(n/10)])
            # train(datas)


if __name__ == '__main__':
    main()