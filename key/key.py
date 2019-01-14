import math
import contract


TICK_PRICE = 1
SLIDE = 2 * TICK_PRICE
COST = 0.5 * TICK_PRICE

class Order:
    def __init__(self):
        self.price = 0
        self.direction = 0
        self.profit = 0

    def floatProfit(self, price):
        return self.profit + (price - self.price)*self.direction
    
    def trade(self, date, price, upper, lower, trades, isOpen=False):
        if self.direction == 1 and price <= lower:
            self.direction = 0
            deal = price if isOpen else lower
            p = math.floor(deal/TICK_PRICE)*TICK_PRICE
            self.profit += p - self.price - COST - SLIDE
            trades.append({'date':date, 'op':'close', 'price':p})
        elif self.direction == -1 and price >= upper:
            self.direction = 0
            deal = price if isOpen else upper
            p = math.ceil(deal/TICK_PRICE)*TICK_PRICE
            self.profit += self.price - p - COST - SLIDE
            trades.append({'date':date, 'op':'close', 'price':-p})

        
        if self.direction == 0:
            if price >= upper:
                self.direction = 1
                deal = price if isOpen else upper
                self.price = math.ceil(deal/TICK_PRICE) * TICK_PRICE + SLIDE
                trades.append({'date':date, 'op':'open', 'price':self.price})
            elif price <= lower:
                self.direction = -1
                deal = price if isOpen else lower
                self.price = math.floor(deal/TICK_PRICE) * TICK_PRICE - SLIDE
                trades.append({'date':date, 'op':'open', 'price':-self.price})

class Key:
    def __init__(self, upper, lower):
        self.upper = upper
        self.lower = lower

class Day:
    def __init__(self, bar):
        self.date = bar.date
        self.high = bar.high
        self.low = bar.low
        self.open = bar.open
        self.volume = bar.volume
        self.key = None

class Trader:
    def __init__(self, bars):
        self.bars = bars
        self.days = [Day(bars[0])]
        self.dates = [bars[0].date]
        i = 1
        n = len(bars)
        while i < n:
            bar = bars[i]
            if bars[i-1].date != bar.date:
                self.days.append(Day(bar))
                self.dates.append(bar.date)
            else:
                day = self.days[-1]
                day.high = max(bar.high, day.high)
                day.low = min(bar.low, day.low)
                day.volume += bar.volume
                day.close = bar.close
            i += 1

    def debugTrade(self):
        for trade in self.trades:
            print("%d, %s, %f" % (trade['date'], trade['op'], trade['price']))

    def update(self, bar, day):
        self.order.trade(bar.date, bar.open, day.key.upper, day.key.lower, self.trades, True)
        if bar.close >= bar.open:
            self.order.trade(bar.date, bar.low, day.key.upper, day.key.lower, self.trades)
            self.order.trade(bar.date, bar.high, day.key.upper, day.key.lower, self.trades)
        else:
            self.order.trade(bar.date, bar.high, day.key.upper, day.key.lower, self.trades)
            self.order.trade(bar.date, bar.low, day.key.upper, day.key.lower, self.trades)
        self.order.trade(bar.date, bar.close, day.key.upper, day.key.lower, self.trades)

    def initKey(self, period, ndays):
        i = period
        n = len(self.days)
        key = None
        self.nKeys = 0
        while i < n:
            hdays = sorted(self.days[i-period:i], key = lambda day: day.high, reverse = True)
            ldays = sorted(self.days[i-period:i], key = lambda day: day.low)
            upper = hdays[ndays-1].high
            lower = ldays[ndays-1].low
            if upper > lower:
                key = Key(upper, lower)
                self.nKeys += 1
            if key is not None:
                self.days[i].key = key
            i += 1

    def traceday(self):
        self.profits = [0]
        self.trades = []
        self.order = Order()

        start = False
        i = 1
        n = len(self.days)
        while i < n:
            day = self.days[i]
            lastDay = self.days[i-1]
            if lastDay.volume > 1000:
                start = True

            if start and lastDay.key is not None:
                self.order.trade(day.date, day.open, lastDay.key.upper, lastDay.key.lower, self.trades, True)
            
            self.profits.append(self.order.floatProfit(day.close))
            i += 1

    def traceback(self):
        self.profits = []
        self.trades = []
        self.order = Order()

        n = len(self.bars)
        i = 1
        iday = 0
        day = None
        start = False
        while i < n:
            bar = self.bars[i]
            if self.bars[i-1].date != bar.date:
                self.profits.append(self.order.floatProfit(self.bars[i-1].close))
                day = self.days[iday]
                iday += 1
                if day.volume >= 1000:
                    start = True


            if start and day.key is not None:
                self.update(bar, day)

            i += 1

        self.profits.append(self.order.floatProfit(self.bars[-1].close))
