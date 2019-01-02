#!/usr/bin/python


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
            record.date = int(words[0].strip('/'))
            record.time = float('0.' + words[1])
            record.open = float(words[2])
            record.high = float(words[3])
            record.low = float(words[4])
            record.close = float(words[5])
            record.volume = int(words[6])
            record.openInterest = int(words[7])
            record.settlement = float(words[8])

    def __validVolume(self, datas):
        for record in datas:
            if record.volume < 10:
                return False
        return True

    def getDataset(self, ni, no):
        inputs = []
        output = []
        N = len(self.records)
        i = 0
        n = i + ni + no

        while n <= N:
            di = self.records[i:i+ni]
            do = self.records[i+ni:n]

            if self.__validVolume(di) and self.__validVolume(do):
                inputs.append(di)
                output.append(do)

            i += 1
            n += 1
            if abs(self.records[n].time - self.records[n-1].time) > 0.03:
                i = n
                n = i + ni + no
