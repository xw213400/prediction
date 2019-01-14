import math
import contract

PERIOD_MA = 7
BAND_MA = 0.005

PERIOD_GRID = 3
BAND_GRID = 0.023

TICK_PRICE = 1
SLIDE = 2 * TICK_PRICE
COST = 0.5 * TICK_PRICE

class GridOrder:
    def __init__(self, direction):
        self.name = 'grid'
        self.price = 0
        self.lower = 1 - BAND_GRID
        self.upper = 1 + BAND_GRID
        self.direction = direction
        self.profit = 0

    def floatProfit(self, price):
        fp = 0

        if self.price > 0:
            fp = (price - self.price)*self.direction
        
        return self.profit + fp
    
    def trade(self, ma, price, isOpen=False):
        trades = []
        if self.direction == 1: #buy open & sell close
            if self.price == 0:
                mount = ma * self.lower
                if price <= mount:
                    if isOpen:
                        mount = price
                    self.price = math.ceil(mount/TICK_PRICE)*TICK_PRICE
                    trades.append({'op':'open', 'price':self.direction * self.price})
            else:
                mount = ma * self.upper
                if price >= mount:
                    if isOpen:
                        mount = price
                    p = math.floor(mount/TICK_PRICE)*TICK_PRICE
                    self.profit += p - self.price - COST
                    self.price = 0
                    trades.append({'op':'close', 'price':self.direction * p})
        else:
            if self.price == 0:
                mount = ma * self.upper
                if price >= mount:
                    if isOpen:
                        mount = price
                    self.price = math.floor(mount/TICK_PRICE)*TICK_PRICE
                    trades.append({'op':'open', 'price':self.direction * self.price})
            else:
                mount = ma * self.lower
                if price <= mount:
                    if isOpen:
                        mount = price
                    p = math.ceil(mount/TICK_PRICE)*TICK_PRICE
                    self.profit += self.price - p - COST
                    self.price = 0
                    trades.append({'op':'close', 'price':self.direction * p})
        return trades

class MAOrder:
    def __init__(self):
        self.name = 'ma'
        self.price = 0
        self.upper = 1 + BAND_MA
        self.lower = 1 - BAND_MA
        self.direction = 0
        self.profit = 0

    def floatProfit(self, price):
        return self.profit + (price - self.price)*self.direction
    
    def trade(self, ma, price, isOpen=False):
        upper = ma * self.upper
        lower = ma * self.lower
        trades = []

        if self.direction == 1 and price <= lower:
            self.direction = 0
            deal = price if isOpen else lower
            p = math.floor(deal/TICK_PRICE)*TICK_PRICE
            self.profit += p - self.price - COST - SLIDE
            trades.append({'op':'close', 'price':p})
        elif self.direction == -1 and price >= upper:
            self.direction = 0
            deal = price if isOpen else upper
            p = math.ceil(deal/TICK_PRICE)*TICK_PRICE
            self.profit += self.price - p - COST - SLIDE
            trades.append({'op':'close', 'price':-p})

        
        if self.direction == 0:
            if price >= upper:
                self.direction = 1
                deal = price if isOpen else upper
                self.price = math.ceil(deal/TICK_PRICE) * TICK_PRICE + SLIDE
                trades.append({'op':'open', 'price':self.price})
            elif price <= lower:
                self.direction = -1
                deal = price if isOpen else lower
                self.price = math.floor(deal/TICK_PRICE) * TICK_PRICE - SLIDE
                trades.append({'op':'open', 'price':-self.price})

        return trades

class Trader:
    # 400000, 55, 0.125, 8
    def __init__(self):
        pass

    def debugTrade(self):
        for trade in self.trades:
            print("%d, %s, %f" % (trade['date'], trade['op'], trade['price']))

    def update(self, date, price, isOpen=False):
        for order in self.orders:
            trades = None
            if order.name == 'ma':
                trades = order.trade(self.ma_MA, price, isOpen)
            else:
                trades = order.trade(self.ma_GRID, price, isOpen)

            for trade in trades:
                trade['date'] = date
                self.trades.append(trade)

    def traceback(self, bars, orders):
        self.orders = orders
        self.ma_MA = 0
        self.ma_GRID = 0

        self.profits = []
        self.trades = []
        self.dates = []
        self.prices = []

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
                if len(days) < PERIOD_MA:
                    self.ma_MA += (lastbar.close - self.ma_MA) / (len(days)+1)
                else:
                    self.ma_MA += (lastbar.close - days[-PERIOD_MA]) / PERIOD_MA

                if len(days) < PERIOD_GRID:
                    self.ma_GRID += (lastbar.close - self.ma_GRID) / (len(days)+1)
                else:
                    self.ma_GRID += (lastbar.close - days[-PERIOD_GRID]) / PERIOD_GRID

                days.append(lastbar.close)
                if volume > 1000:
                    start = True
                volume = 0

            volume += bar.volume

            if not start:
                continue

            date = bar.date# - 20180101

            if bar.volume >= 10:
                self.update(date, bar.open, True)
                self.update(date, bar.low)
                self.update(date, bar.high)
                self.update(date, bar.close)

            if bar.date != lastbar.date:
                self.dates.append(date)
                self.prices.append(bar.close)
                profit = 0
                for order in self.orders:
                    # profit += order.profit
                    profit += order.floatProfit(bar.close)
                self.profits.append(profit)
