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

    def __validVolume(self, records):
        volume = 0
        for record in records:
            volume += record.volume

        return volume > len(records) * 10 
        

    def __getData(self, ri, ro):
        datai = []
        datao = []
        open0 = ri[0].open
        volume0 = ri[0].volume
        openInterest0 = ri[0].openInterest

        for record in ri:
            d = []
            d.append(record.open / open0)
            d.append(record.high / open0)
            d.append(record.low / open0)
            d.append(record.close / open0)
            d.append(record.volume / volume0)
            d.append(record.openInterest / openInterest0)
            d.append(record.settlement / open0)
            datai.append(d)

        close0 = ri[-1].close

        for record in ro:
            datao.append(record.close / close0)

        return datai, datao

    def getDataset(self, ni, no):
        inputs = []
        output = []
        N = len(self.records)
        i = 0
        n = i + ni + no

        while n <= N:
            ri = self.records[i:i+ni]
            ro = self.records[i+ni:n]

            if self.__validVolume(ri) and self.__validVolume(ro):
                di, do = self.__getData(ri, ro)
                inputs.append(di)
                output.append(do)

            i += 1
            n += 1

        return inputs, output
