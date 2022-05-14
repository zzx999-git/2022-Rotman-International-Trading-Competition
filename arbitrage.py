# -*- coding: utf-8 -*-

import executions
import config

# 0: no position, 1: buy ETF sell stock, -1: sell ETF buy stock
ARBITRAGE_STATUS = 0
# arbQuantity = 0

# check if arbitrage opportunity exists
# action: "enter" or "exit"
def check_arbitrage(s, action):
    global arbQuantity
    USDbid, USDask = executions.ticker_bid_ask(s, 'USD')
    RITCbid, RITCask, RITCbidQuant, RITCaskQuant = executions.ticker_bid_ask_and_quant(s, 'RITC')
    Bullbid, Bullask, BullbidQuant, BullaskQuant = executions.ticker_bid_ask_and_quant(s, 'BULL')
    Bearbid, Bearask, BearbidQuant, BearaskQuant  = executions.ticker_bid_ask_and_quant(s, 'BEAR')

    # print("USD bid:", USDbid, "RITC bid:", RITCbid, "BullAsk:", Bullask, "BearAsk:", Bearask)
    # print(ETF_overvalue)
    # print("USD bid:", USDbid, "RITC ask:", RITCbid, "BullAsk:", Bullask, "BearAsk:", Bearask)
    # print(stock_overvalue)
    if action == "enter":
        ETF_overvalue = USDbid * RITCbid - Bullask - Bearask - config.fee * 2 - config.fee * USDask
        stock_overvalue = Bullbid + Bearbid - USDask * RITCask - config.fee * 2 - config.fee * USDask
        # print(ETF_overvalue)
        # print(stock_overvalue)
        if ETF_overvalue > config.ARB_ENTER_THRESHOLD:
            if min(RITCbidQuant, BullaskQuant, BearaskQuant) >= config.ARB_TRADE_SHARES:
                print("enter1")
                return -1 # sell ETF, buy stocks
        if stock_overvalue > config.ARB_ENTER_THRESHOLD:
            if min(BullbidQuant, BearbidQuant,  RITCaskQuant) >= config.ARB_TRADE_SHARES:
                print("enter2")
                return 1 # Buy ETF sell stocks
            return 0
        return 0
    elif action == "exit":
        ETF_overvalue = USDask * RITCask - Bullbid - Bearbid - config.fee * 2 - config.fee * USDask
        stock_overvalue = Bullask + Bearask - USDask * RITCbid - config.fee * 2 - config.fee * USDask
        # print(ETF_overvalue)
        # print(stock_overvalue)
        if ARBITRAGE_STATUS == -1:
            if ETF_overvalue < config.ARB_EXIT_THRESHOLD:
                print("exit1", ETF_overvalue, config.ARB_EXIT_THRESHOLD)
                return -1 # buy ETF, sell stocks to close position
            else:
                return 0
        elif ARBITRAGE_STATUS == 1:
            if stock_overvalue < config.ARB_EXIT_THRESHOLD:
                print("exit2", stock_overvalue, config.ARB_EXIT_THRESHOLD)
                return 1 # Sell ETF Buy stocks to close position
            else:
                return 0
        else: 
            return 0
    else:
        print("Action incorrect! Either enter or exit!")


def trade_arbitrage(session):
    global ARBITRAGE_STATUS
    overvalue = check_arbitrage(session, "enter")

    if overvalue == -1:
        executions.make_order('RITC', 'MARKET', config.ARB_TRADE_SHARES, 'SELL')
        executions.make_order('BULL', 'MARKET', config.ARB_TRADE_SHARES, 'BUY')
        executions.make_order('BEAR', 'MARKET', config.ARB_TRADE_SHARES, 'BUY')
        ARBITRAGE_STATUS = -1
    elif overvalue == 1:
        executions.make_order('RITC', 'MARKET', config.ARB_TRADE_SHARES, 'BUY')
        executions.make_order('BULL', 'MARKET', config.ARB_TRADE_SHARES, 'SELL')
        executions.make_order('BEAR', 'MARKET', config.ARB_TRADE_SHARES, 'SELL')
        ARBITRAGE_STATUS = 1
    else:
        print(executions.get_tick(session), ": no arb opportunity")


    
def close_arbitrage(session):
    global ARBITRAGE_STATUS
    
    if ARBITRAGE_STATUS != 0:
        overvalue = check_arbitrage(session, "exit")
       
        # bought ETF sold stock, stock overvalued
        if ARBITRAGE_STATUS == 1:
            if overvalue == 1: 
                executions.make_order('RITC', 'MARKET', config.ARB_TRADE_SHARES, 'SELL')
                executions.make_order('BULL', 'MARKET', config.ARB_TRADE_SHARES, 'BUY')
                executions.make_order('BEAR', 'MARKET', config.ARB_TRADE_SHARES, 'BUY')
                ARBITRAGE_STATUS = 0
            else:
                print("Doesn't meet close postion criteria!")
        # sold ETF bought stock, ETF overvalued
        elif ARBITRAGE_STATUS == -1:
            if overvalue == -1: 
                executions.make_order('RITC', 'MARKET', config.ARB_TRADE_SHARES, 'BUY')
                executions.make_order('BULL', 'MARKET', config.ARB_TRADE_SHARES, 'SELL')
                executions.make_order('BEAR', 'MARKET', config.ARB_TRADE_SHARES, 'SELL')
                ARBITRAGE_STATUS = 0
            else:
                print("Doesn't meet close postion criteria!")
    else:
        print("Arbitrage postion: 0")
