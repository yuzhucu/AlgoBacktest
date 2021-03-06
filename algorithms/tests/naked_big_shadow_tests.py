import unittest
import datetime
from algorithms.naked_big_shadow import NakedBigShadow
from backtest.backtest_orderbook_persist import BacktestOrderbookPersist
from data.dummy_symbol_provider import DummySymbolProvider
from market.interfaces.orderrouter import OrderRouter
from market.market_data import MarketDataPeriod
from market.order import State, Direction
from market.orderbook import OrderBook
from market.position import Position
from market.price import Quote, Tick

from market.symbol import Symbol
from strategy.strategy import Context

class TestOrderRouter(OrderRouter):
    def __init__(self):
        OrderRouter.__init__(self)
        self.orders = []
        self.positions = []
        self.tick = None

    def register_tick(self, tick):
        self.tick = tick

    def place_order(self, order):
        self.orders.append(order)
        [f(order, State.PENDING_NEW) for f in self.orderStatusObservers]

        position = Position(order, self.tick)
        [f(order, State.FILLED) for f in self.orderStatusObservers]
        self.positions.append(position)
        [f(position, None) for f in self.positionObservers]

    def cancel_order(self, order):
        pass

    def close_position(self, position):
        pass

    def modify_order(self, order):
        pass


class NakedTests(unittest.TestCase):
    def setUp(self):
        Symbol.set_info_provider(DummySymbolProvider())
        self.order_router = TestOrderRouter()
        self.algo = NakedBigShadow(10, 50, 100, MarketDataPeriod.HOUR_1)
        self.context = Context(10000, OrderBook(self.order_router, BacktestOrderbookPersist()), self.algo.analysis_symbols(), self.algo.quote_cache_size())

    def testStrongCandleBear(self):
        start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
        symbol = self.algo.analysis_symbols()[0]

        t = (0.8, 1.0, 0.0, 0.2)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))

        self.assertTrue(self.algo.is_strong_candle(quote, Direction.SHORT))

        t = (0.8, 1.0, 0.0, 0.4)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))

        self.assertFalse(self.algo.is_strong_candle(quote, Direction.SHORT))

    def testStrongCandleBull(self):
        start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
        symbol = self.algo.analysis_symbols()[0]

        t = (0.2, 0.0, 1.0, 0.8)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))

        self.assertTrue(self.algo.is_strong_candle(quote, Direction.LONG))

        t = (0.2, 0.0, 1.0, 0.7)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))

        self.assertFalse(self.algo.is_strong_candle(quote, Direction.LONG))

    def testBodyEngulfing(self):
        start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
        symbol = self.algo.analysis_symbols()[0]

        t = (0.6, 0.8, 0.2, 0.4)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))

        t = (0.8, 1.0, 0.0, 0.2)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote2 = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote2.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote2.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote2.add_tick(Tick(start_time.timestamp(), t[3], t[3]))

        self.assertFalse(self.algo.is_body_engulfing(quote, quote2))
        self.assertTrue(self.algo.is_body_engulfing(quote2, quote))

    def testLargestCandle(self):
        start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
        symbol = self.algo.analysis_symbols()[0]

        history = []
        t = (0.6, 0.8, 0.2, 0.4)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
        history.append(quote)

        t = (0.7, 0.9, 0.1, 0.3)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
        history.append(quote)

        t = (0.8, 1.0, 0.0, 0.2)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))

        self.assertTrue(self.algo.is_largest(quote, history))

        t = (0.7, 0.8, 0.0, 0.31)
        tick = Tick(start_time.timestamp(), t[0], t[0])
        quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1, tick)
        quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
        quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
        quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
        self.assertFalse(self.algo.is_largest(quote, history))

#     def testEngulfingWithoutSpaceBuyEntry(self):
#         symbol = self.algo.analysis_symbols()[0]
#         start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
#         quotes = []
#
#         # |
#         # |                   |           |
#         # |                 | | |       | | |
#         # | | | | | | | | | |   | | | | |   |  |
#         # |
#         # |
#         # |
#         # |
#         # |_____________________________________
#
# #                 O    H    L    C
#         ticks = ((0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.5, 0.7, 0.2, 0.25),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.5, 0.7, 0.2, 0.25),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.2, 0.3, 0.1, 0.2))
#
#         for t in ticks:
#             tick = Tick(start_time.timestamp(), t[0], t[0])
#             self.order_router.register_tick(tick)
#             quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1 - datetime.timedelta(seconds=1), tick)
#             quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
#             quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
#             quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
#             quotes.append(quote)
#             start_time += MarketDataPeriod.HOUR_1
#
#         for quote in quotes:
#             self.context.add_quote(quote)
#             self.algo.evaluate_tick_update(self.context, quote)
#
#         self.assertEqual(len(self.order_router.orders), 1)
#         # self.assertEqual(s1, s2)
#         # self.assertEqual(id(s1.__dict__), id(s2.__dict__))
#
#     def testBuyEntry(self):
#         symbol = self.algo.analysis_symbols()[0]
#         start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
#         quotes = []
#
#         # |
#         # |                   |
#         # |                 | | |
#         # | | | | | | | | | |   |
#         # |
#         # |
#         # |
#         # |
#         # |_____________________________________
#
# #                 O    H    L    C
#         ticks = ((0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.5, 0.7, 0.2, 0.25),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.2, 0.3, 0.1, 0.2))
#
#         for t in ticks:
#             tick = Tick(start_time.timestamp(), t[0], t[0])
#             self.order_router.register_tick(tick)
#             quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1 - datetime.timedelta(seconds=1), tick)
#             quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
#             quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
#             quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
#             quotes.append(quote)
#             start_time += MarketDataPeriod.HOUR_1
#
#         for quote in quotes:
#             self.context.add_quote(quote)
#             self.algo.evaluate_tick_update(self.context, quote)
#
#         self.assertEqual(len(self.order_router.orders), 1)
#         # self.assertEqual(s1, s2)
#         # self.assertEqual(id(s1.__dict__), id(s2.__dict__))
#
#
#     def testDuplicateBuyEntry(self):
#         symbol = self.algo.analysis_symbols()[0]
#         start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
#         quotes = []
#
#         # |                               |
#         # |                   |           |
#         # |                 | | |       |   |
#         # | | | | | | | | | |   | | | | |   |  |
#         # |
#         # |
#         # |
#         # |
#         # |_____________________________________
#
# #                 O    H    L    C
#         ticks = ((0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.5, 0.7, 0.2, 0.25),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.6, 0.9, 0.2, 0.25),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.2, 0.3, 0.1, 0.2))
#
#         for t in ticks:
#             tick = Tick(start_time.timestamp(), t[0], t[0])
#             self.order_router.register_tick(tick)
#             quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1 - datetime.timedelta(seconds=1), tick)
#             quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
#             quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
#             quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
#             quotes.append(quote)
#             start_time += MarketDataPeriod.HOUR_1
#
#         for quote in quotes:
#             self.context.add_quote(quote)
#             self.algo.evaluate_tick_update(self.context, quote)
#
#         # we should have 2 order, but in reality the first will probably have
#         # hit our stop loss
#         self.assertEqual(len(self.order_router.orders), 2)
#
#     def testEngulfingWithSpaceBuyEntry(self):
#         symbol = self.algo.analysis_symbols()[0]
#         start_time = datetime.datetime(2015, 7, 26, 12, 0, 0)
#         quotes = []
#
#         # |
#         #          |                      |
#         # |      | | |                  | | |
#         # |  | | |   | | | | | | | || | |   |  |
#         # |
#         # |
#         # |
#         # |
#         # |_____________________________________
#
# #                 O    H    L    C
#         ticks = ((0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.5, 0.7, 0.2, 0.25),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.2, 0.3, 0.1, 0.2),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.5, 0.7, 0.2, 0.25),
#                  (0.4, 0.8, 0.3, 0.3),
#                  (0.2, 0.3, 0.1, 0.2))
#
#         for t in ticks:
#             tick = Tick(start_time.timestamp(), t[0], t[0])
#             self.order_router.register_tick(tick)
#             quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1 - datetime.timedelta(seconds=1), tick)
#             quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
#             quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
#             quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
#             quotes.append(quote)
#             start_time += MarketDataPeriod.HOUR_1
#
#         for quote in quotes:
#             self.context.add_quote(quote)
#             self.algo.evaluate_tick_update(self.context, quote)
#
#         # we have hit another entry point, but we should also still have a buy
#         # order on the market, so we shouldn't be taking a position
#         self.assertEqual(len(self.order_router.orders), 1)
