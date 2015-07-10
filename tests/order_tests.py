from datetime import datetime, timedelta
import unittest

from strategycontainer.order import Order, Entry, Direction, State
from strategycontainer.symbol import Symbol
from strategycontainer.price import Tick


class OrderTest(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider("1")

    def testMarketOrder(self):
        s = Symbol("TEST")
        order = Order(s, 1, Entry(Entry.Type.MARKET), Direction.LONG)
        tick = Tick(datetime.utcnow(), 11.0, 11.1)

        r = order.shouldFill(tick)
        self.assertEqual(True, r)

    def testLimitOrder(self):
        s = Symbol("TEST")
        order = Order(s, 1, Entry(Entry.Type.LIMIT, 10.0), Direction.LONG)

        tick = Tick(datetime.utcnow(), 11.0, 11.1)
        r = order.shouldFill(tick)
        self.assertEqual(False, r)

        tick = Tick(datetime.utcnow(), 9.0, 9.1)
        r = order.shouldFill(tick)
        self.assertEqual(True, r)

    def testStopEntryOrder(self):
        s = Symbol("TEST")
        order = Order(s, 1, Entry(Entry.Type.STOP_ENTRY, 10.0), Direction.LONG)

        tick = Tick(datetime.utcnow(), 9.0, 9.1)
        r = order.shouldFill(tick)
        self.assertEqual(False, r)

        tick = Tick(datetime.utcnow(), 11.0, 11.1)
        r = order.shouldFill(tick)
        self.assertEqual(True, r)

    def testExpireTime(self):
        s = Symbol("TEST")
        order = Order(s, 1, Entry(Entry.Type.STOP_ENTRY, 10.0), Direction.LONG, expireTime=timedelta(seconds=1))

        tick = Tick(datetime.utcnow(), 9.0, 9.1)
        r = order.shouldFill(tick)
        self.assertEqual(False, r)

        tick = Tick(datetime.utcnow() + timedelta(seconds=2), 9.0, 9.1)
        r = order.shouldFill(tick)
        self.assertEqual(False, r)
        self.assertEqual(order.state, State.EXPIRED)

