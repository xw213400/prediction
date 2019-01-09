import math
import contract

TICK_PRICE = 1
GRID_BAND = 0.005
MA_BAND = 0.01
COST = 0.5 * TICK_PRICE


class GridOrder:
    def __init__(self, direction):
        self.price = 0
        self.upper = 1 + GRID_BAND
        self.lower = 1 - GRID_BAND
        self.direction = direction
        self.profit = 0

    def floatProfit(self, price):
        fp = 0
        # if self.price > 0:
        #     fp = (price - self.price)*self.direction
        
        return self.profit + fp
    
    def trade(self, ma, price, isOpen=False):
        if self.direction == 1: #buy open & sell close
            if self.price == 0:
                mount = ma * self.lower
                if price <= mount:
                    if isOpen:
                        mount = price
                    self.price = math.ceil(mount/TICK_PRICE)*TICK_PRICE
                    return {'op':'open', 'price':self.direction * self.price}
            else:
                mount = ma * self.upper
                if price >= mount:
                    if isOpen:
                        mount = price
                    p = math.floor(mount/TICK_PRICE)*TICK_PRICE
                    self.profit += p - self.price - COST
                    self.price = 0
                    return {'op':'close', 'price':self.direction * p}
        else:
            if self.price == 0:
                mount = ma * self.upper
                if price >= mount:
                    if isOpen:
                        mount = price
                    self.price = math.floor(mount/TICK_PRICE)*TICK_PRICE
                    return {'op':'open', 'price':self.direction * self.price}
            else:
                mount = ma * self.lower
                if price <= mount:
                    if isOpen:
                        mount = price
                    p = math.ceil(mount/TICK_PRICE)*TICK_PRICE
                    self.profit += self.price - p - COST
                    self.price = 0
                    return {'op':'close', 'price':self.direction * p}
        return None

class Grid:
    # 400000, 55, 0.125, 8
    def __init__(self):
        pass

    def init(self, period, band):
        global GRID_BAND
        GRID_BAND = band

        self.period = period
        self.orders = [GridOrder(1), GridOrder(-1)]
        self.MA = 0

        self.profits = []
        self.trades = []
        self.dates = []
        self.prices = []
        self.mas = []

    def debugTrade(self):
        for trade in self.trades:
            print("%d, %s, %f" % (trade['date'], trade['op'], trade['price']))

    def update(self, date, price, isOpen=False):
        for order in self.orders:
            trade = order.trade(self.MA, price, isOpen)
            if trade is not None:
                trade['date'] = date
                self.trades.append(trade)

    def traceback(self, bars):
        i = 1
        n = len(bars)
        days = []

        volume = bars[0].volume
        start = False

        while i < n:
            lastbar = bars[i-1]
            bar = bars[i]
            i += 1

            if bar.date != lastbar.date:
                if len(days) < self.period:
                    self.MA += (lastbar.close - self.MA) / (len(days)+1)
                else:
                    self.MA += (lastbar.close - days[-self.period]) / self.period
                days.append(lastbar.close)
                if volume > 1000:
                    start = True
                volume = 0

            volume += bar.volume

            if not start:
                continue

            date = bar.date - 20180101

            if self.MA > 0 and bar.volume >= 10:
                self.update(date, bar.open, bar.date != lastbar.date)
                self.update(date, bar.low)
                self.update(date, bar.high)
                self.update(date, bar.close)

            if bar.date != lastbar.date:
                self.dates.append(date)
                self.prices.append(bar.close)
                self.mas.append(self.MA)
                profit = 0
                for order in self.orders:
                    profit += order.floatProfit(bar.close)
                self.profits.append(profit)