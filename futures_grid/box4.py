import math
import contract

RATIO = 0.9

TICK_PRICE = 1
SLIDE = 2 * TICK_PRICE
COST = 0.5 * TICK_PRICE

WAIT, UPPER_B, UPPER_A, LOWER_B, LOWER_V = range(5) 


class Order:
    def __init__(self):
        self.price = 0
        self.state = WAIT
        self.profit = 0

    def floatProfit(self, price):
        fp = 0

        if self.state != WAIT:
            fp = price - self.price
            if self.state == LOWER_B or self.state == UPPER_A:
                fp = -fp
        
        return self.profit + fp
    
    def trade(self, upper, lower, price, isOpen=False):
        band = (upper - lower) * 0.5 * RATIO
        middle = (upper + lower) * 0.5
        upper0 = middle + band
        lower0 = middle - band
        trades = []

        oldstate = self.state

        if self.state == UPPER_B and price <= upper0:
            deal = price if isOpen else upper0
            deal = math.floor(deal/TICK_PRICE)*TICK_PRICE - SLIDE
            self.profit += deal - self.price - COST
            self.state = WAIT
            trades.append({'op':'close', 'price':deal, 'state':self.state})
        
        if self.state == LOWER_B and price >= lower0:
            deal = price if isOpen else lower0
            deal = math.floor(deal/TICK_PRICE)*TICK_PRICE + SLIDE
            self.profit += self.price - deal - COST
            self.state = WAIT
            trades.append({'op':'close', 'price':-deal, 'state':self.state})

        if self.state == UPPER_A:
            if price > upper:
                deal = price if isOpen else upper
                deal = math.floor(deal/TICK_PRICE)*TICK_PRICE + SLIDE
                self.profit += self.price - deal - COST
                self.state = WAIT
                trades.append({'op':'close', 'price':-deal, 'state':self.state})
            elif price <= lower0:
                deal = price if isOpen else lower0
                deal = math.floor(deal/TICK_PRICE)*TICK_PRICE
                self.profit += self.price - deal - COST
                self.state = WAIT
                trades.append({'op':'close', 'price':-deal, 'state':self.state})
            
        if self.state == LOWER_V:
            if price < lower:
                deal = price if isOpen else lower
                deal = math.floor(deal/TICK_PRICE)*TICK_PRICE - SLIDE
                self.profit += deal - self.price - COST
                self.state = WAIT
                trades.append({'op':'close', 'price':deal, 'state':self.state})
            elif price >= upper0:
                deal = price if isOpen else upper0
                deal = math.floor(deal/TICK_PRICE)*TICK_PRICE
                self.profit += deal - self.price - COST
                self.state = WAIT
                trades.append({'op':'close', 'price':deal, 'state':self.state})

        state2 = self.state

        if self.state == WAIT:
            if price > upper:
                deal = price if isOpen else upper
                self.price = math.floor(deal/TICK_PRICE)*TICK_PRICE + SLIDE
                self.state = UPPER_B
                trades.append({'op':'open', 'price':self.price, 'state':self.state})
            elif price < lower:
                deal = price if isOpen else lower
                self.price = math.floor(deal/TICK_PRICE)*TICK_PRICE - SLIDE
                self.state = LOWER_B
                trades.append({'op':'open', 'price':-self.price, 'state':self.state})
            elif price >= upper0:
                deal = price if isOpen else upper0
                self.price = math.floor(deal/TICK_PRICE)*TICK_PRICE + SLIDE
                self.state = UPPER_A
                trades.append({'op':'open', 'price':-self.price, 'state':self.state})
            elif price <= lower0:
                deal = price if isOpen else lower0
                self.price = math.floor(deal/TICK_PRICE)*TICK_PRICE - SLIDE
                self.state = LOWER_V
                trades.append({'op':'open', 'price':self.price, 'state':self.state})

        for trade in trades:
            print("%d, %d, %d, %d, %d" % (upper, upper0, lower0, lower, price))
            print("%s, %d, %d, %d, %d\n" % (trade['op'], trade['price'], oldstate, state2, trade['state']))

        return trades

class Trader:
    def __init__(self):
        pass

    def init(self, period, ratio):
        global RATIO

        self.period = period
        self.order = Order()

        self.profits = []
        self.trades = []
        self.dates = []
        self.prices = []

        self.uppers = []
        self.lowers = []
        self.hhs = []
        self.lls = []

    def debugTrade(self):
        for trade in self.trades:
            print("%d, %s, %f, %d" % (trade['date'], trade['op'], trade['price'], trade['state']))

    def update(self, date, upper, lower, price, isOpen=False):
        trades = self.order.trade(upper, lower, price, isOpen)
        for trade in trades:
            trade['date'] = date
            self.trades.append(trade)

    def traceback(self, bars):
        i = 1
        n = len(bars)

        volume = bars[0].volume
        start = False

        high = upper = bars[0].high
        low = lower = bars[0].low

        while i < n:
            lastbar = bars[i-1]
            bar = bars[i]
            i += 1

            if bar.date != lastbar.date:
                self.uppers.append(upper)
                self.lowers.append(lower)

                pd = self.period
                if len(self.uppers) < self.period:
                    pd = len(self.uppers)
                high = max(self.uppers[-pd:])
                low = min(self.lowers[-pd:])

                self.hhs.append(high)
                self.lls.append(low)

                upper = bar.high
                lower = bar.low

                if volume > 1000:
                    start = True
                volume = 0
            else:
                if bar.high > upper:
                    upper = bar.high

                if bar.low < lower:
                    lower = bar.low

            volume += bar.volume

            if not start:
                continue

            date = bar.date - 20180101

            if bar.volume >= 10:
                self.update(date, high, low, bar.open, True)
                self.update(date, high, low, bar.low)
                self.update(date, high, low, bar.high)
                self.update(date, high, low, bar.close)

            if bar.date != lastbar.date:
                self.dates.append(date)
                self.prices.append(bar.close)
                self.profits.append(self.order.profit)
