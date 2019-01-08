import math


class Grid:
    # 400000, 55, 0.125, 8
    def __init__(self, tickprice, cost):
        self.tickprice = tickprice
        self.cost = cost
        self.short = 0
        self.buy = 0
        self.MA = 0
        self.trade = 0

    def init(self, period, steps, band):
        self.period = period
        self.steps = steps
        self.band = band

        self.position = 0
        self.MA = 0
        self.trade = 0

    def updatePosition(self, price, isOpen=False):
        bandPosition = round(
            self.money / self.MA / self.step * 0.01) * 100
        bandprice = self.MA * self.band
        levelprice = self.MA + self.level * bandprice
        levelprice = round(levelprice * 1000) * 0.001

        deltaLevel = math.floor(abs(price - levelprice) / bandprice)
        d = 1
        if price < levelprice:
            d = -1
            deltaLevel = -deltaLevel

        maxlevel = math.floor(self.step / 2)

        if self.level + deltaLevel > maxlevel:
            deltaLevel = maxlevel - self.level
        elif self.level + deltaLevel < -maxlevel:
            deltaLevel = -maxlevel - self.level


        if deltaLevel == 0:
            return

        if isOpen:
            deltaPosition = math.floor(deltaLevel * bandPosition * 0.01) * 100
            self.position -= deltaPosition
            deltaCash = deltaPosition * price
            cost = round(abs(deltaCash) * 0.02) * 0.01
            if cost < 5:
                cost = 5
            self.cash += deltaCash
            self.cash -= cost
            self.level += deltaLevel
            self.trade += 1

            # print("%d, bp:%.3f, POS: %d, $: %.2f, ALL: %.2f\n" %
            #         (self.trade, bandprice, self.position, self.cash, self.cash+self.position*price))
        else:
            n = abs(deltaLevel)
            i = 1
            while i < n:
                deltaLevel = i * d
                deltaPosition = math.floor(deltaLevel * bandPosition * 0.01) * 100
                self.position -= deltaPosition
                deltaCash = deltaPosition * (levelprice + deltaLevel * bandprice)

                cost = round(abs(deltaCash) * 0.02) * 0.01
                if cost < 5:
                    cost = 5
                self.cash += deltaCash
                self.cash -= cost
                self.level += deltaLevel
                self.trade += 1
                i+=1


                # print("%d, bp:%.3f, POS: %d, $: %.2f, ALL: %.2f\n" %
                #     (self.trade, bandprice, self.position, self.cash, self.cash+self.position*price))

    def traceback(self, bars):
        self.lastclose = self.firsclose = self.MA = bars[0].close
        self.level = 0
        self.position = round(self.money / self.MA * 0.5 * 0.01) * 100
        self.cash = self.money - self.position * self.MA

        i = 1
        n = len(bars)
        history = [1]

        while i < n:
            bar = bars[i-1]
            if i <= self.period:
                self.MA += (bar.close - self.MA) / (i+1)
            else:
                self.MA += (bar.close - bars[i-self.period-1].close) / self.period

            self.MA = round(self.MA * 1000) * 0.001

            bar = bars[i]

            # print("%d, %.3f, %.3f, %.3f, %.3f, MA:%.3f" % (bar.date, bar.open, bar.high, bar.low, bar.close, self.MA))

            self.updatePosition(bar.open, True)
            self.updatePosition(bar.high)
            self.updatePosition(bar.low)
            self.updatePosition(bar.close)

            i += 1

            win = (self.cash+self.position*bar.close)/self.money
            history.append(win)
        # print("period:%d, step:%d, m:%.4f" %
        #       (self.period, self.step, win))

        return history
