import math


class Policy:
    # 400000, 55, 0.125, 8
    def __init__(self, money):
        self.money = money
        self.cash = money

        self.shares = 0
        self.MA = 0
        self.trade = 0

    def init(self, period, deltaRatio, steps):
        self.period = period
        self.unitRatio = deltaRatio * 2 / steps
        self.steps = steps
        self.trade = 0

    def updatePosition(self, price, isOpen=False):
        ma = round(self.MA * 1000) * 0.001
        unitShares = round(self.money / ma / self.steps * 0.01) * 100
        unitPrice = ma * self.unitRatio
        levelPrice = ma + (self.steps * 0.5 - self.level) * unitPrice
        levelPrice = round(levelPrice * 1000) * 0.001

        dLevel = math.floor(abs(price - levelPrice) / unitPrice)
        d = 1
        if price > levelPrice:
            d = -1
            dLevel = -dLevel

        if self.level + dLevel > self.steps:
            dLevel = self.steps - self.level
        elif self.level + dLevel < 0:
            dLevel = -self.level

        if dLevel == 0:
            return

        if isOpen:
            dShare = unitShares * dLevel
            self.shares += dShare
            if self.shares < 0:
                dShare -= self.shares
                self.shares = 0
            dCash = dShare * price
            cost = round(abs(dCash) * 0.02) * 0.01
            if cost < 5:
                cost = 5
            self.cash -= dCash + cost
            self.level += dLevel
            self.trade += 1

            # print("X%d, %d" % (self.shares, self.level))
            # print("X%d, POS: %d, $: %.2f, ALL: %.2f\n" %
            #       (self.trade, self.shares, self.cash, self.cash+self.shares*price))
        else:
            n = abs(dLevel)
            i = 1
            while i < n:
                dShare = unitShares * d
                self.shares += dShare
                if self.shares < 0:
                    dShare -= self.shares
                    self.shares = 0
                dCash = dShare * (levelPrice - round(i * d * unitPrice * 1000) * 0.001)

                cost = round(abs(dCash) * 0.02) * 0.01
                if cost < 5:
                    cost = 5
                self.cash -= dCash + cost
                self.level += d
                self.trade += 1
                i += 1

                # print("%d, %d" % (self.shares, self.level))
                # print("%d, POS: %d, $: %.2f, ALL: %.2f\n" %
                #       (self.trade, self.shares, self.cash, self.cash+self.shares*price))

    def traceback(self, bars):
        self.MA = bars[0].close
        self.level = math.floor(self.steps / 2)
        unitShares = round(self.money / self.MA / self.steps * 0.01) * 100
        self.shares = unitShares * self.level
        self.cash = self.money - self.shares * self.MA

        i = 1
        n = len(bars)
        history = [1]

        mincash = self.cash
        minpos = self.shares

        while i < n:
            bar = bars[i-1]
            if i <= self.period:
                self.MA += (bar.close - self.MA) / (i+1)
            else:
                self.MA += (bar.close -
                            bars[i-self.period-1].close) / self.period

            bar = bars[i]

            # print("%d, %.3f, %.3f, %.3f, %.3f, MA:%.3f" %
            #       (bar.date, bar.open, bar.high, bar.low, bar.close, self.MA))

            self.updatePosition(bar.open, True)
            self.updatePosition(bar.high)
            self.updatePosition(bar.low)
            self.updatePosition(bar.close)

            i += 1

            win = (self.cash+self.shares*bar.close)/self.money
            history.append(win)
            if self.cash < mincash:
                mincash = self.cash
            if self.shares < minpos:
                minpos = self.shares

        # print("%d, %d" % (mincash, minpos))

        return history
