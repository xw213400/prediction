#!/usr/bin/python

import conv


class Record:
    def __init__(self):
        self.date = 20010101
        self.time = 0.0901
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0
        self.openInterest = 0
        self.settlement = 0


class Contract:
    def __init__(self, text):
        self.records = []
        for line in text.readlines():
            record = Record()
            words = line.split()
            record.date = int(words[0].replace('/', ''))
            record.time = float('0.' + words[1])
            record.open = float(words[2])
            record.high = float(words[3])
            record.low = float(words[4])
            record.close = float(words[5])
            record.volume = float(words[6])
            record.openInterest = float(words[7])
            record.settlement = float(words[8])
            self.records.append(record)

    def __validVolume(self, records):
        volume = 0
        for record in records:
            volume += record.volume

        return volume > len(records) * 10 

    def getDataset(self, ni, no):
        datas = []
        N = len(self.records)
        i = 0
        n = i + ni + no

        while n <= N:
            ri = self.records[i:i+ni]
            ro = self.records[i+ni:n]

            if self.__validVolume(ri) and self.__validVolume(ro):
                datas.append(conv.ConvData(ri, ro))

            i += 1
            n += 1

        return datas
