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
            record.date = int(words[0].replace('/', ''))
            record.time = float('0.' + words[1])
            record.open = float(words[2])
            record.high = float(words[3])
            record.low = float(words[4])
            record.close = float(words[5])
            record.volume = int(words[6])
            record.openInterest = int(words[7])
            record.settlement = float(words[8])
            self.records.append(record)

    def __validVolume(self, records):
        volume = 0
        for record in records:
            volume += record.volume

        return volume > len(records) * 10 

    def __scaleNumber(self, number):
        return (number - 1) * 1000

    def __getData(self, ri, ro):
        datai = []
        datao = []
        open0 = ri[0].open
        volume0 = ri[0].volume
        if volume0 == 0:
            volume0 = 1
        openInterest0 = ri[0].openInterest
        if openInterest0 == 0:
            openInterest0 = 1

        for record in ri:
            d = []
            d.append(self.__scaleNumber(record.open / open0))
            d.append(self.__scaleNumber(record.high / open0))
            d.append(self.__scaleNumber(record.low / open0))
            d.append(self.__scaleNumber(record.close / open0))
            d.append(self.__scaleNumber(record.volume / volume0))
            d.append(self.__scaleNumber(record.openInterest / openInterest0))
            d.append(self.__scaleNumber(record.settlement / open0))
            datai.append(d)

        close0 = ro[0].open

        for record in ro:
            datao.append(self.__scaleNumber(record.close / close0))

        return {'I':datai, 'O':datao}

    def getDataset(self, ni, no):
        datas = []
        N = len(self.records)
        i = 0
        n = i + ni + no

        while n <= N:
            ri = self.records[i:i+ni]
            ro = self.records[i+ni:n]

            if self.__validVolume(ri) and self.__validVolume(ro):
                d = self.__getData(ri, ro)
                datas.append(d)

            i += 1
            n += 1

        return datas
