#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import contract
from matplotlib import pyplot as plt

def drawHist(data):
    plt.hist(data, 100)
    plt.xlabel('X')
    plt.ylabel('y')
    plt.title('OUT')
    plt.show()

def train(datas):
    print(len(datas))
    for i in range(10):
        print(datas[i]['O'])

def main():
    files = [f for f in listdir('data') if f[-4:] == '.txt']
    for f in files:
        with open('data/'+f) as text:
            c = contract.Contract(text)
            datas = c.getDataset(20, 1)
            n = len(datas)
            print(n)
            datas.sort(key = lambda rec: abs(rec['O'][-1]), reverse = True)
            train(datas[0:int(n/10)])


if __name__ == '__main__':
    main()