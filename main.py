#!/usr/bin/python

import sys
from os.path import isfile, join
from os import listdir
import contract

def main():
    files = [f for f in listdir('data') if f[-4:] == '.txt']
    for f in files:
        with open('data/'+f) as text:
            c = contract.Contract(text)



if __name__ == '__main__':
    main()