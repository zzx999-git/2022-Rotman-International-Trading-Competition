# -*- coding: utf-8 -*-

API_KEY = {'X-API-key  ': '2Q904VYC'}
fee = 0.02 # transaction cost

# tender parameters
TENDER_THRESHOLD = 0.1 # target profit per share when trade tender at the current market
TENDER_CLEAR_SHARES = 500
TENDER_TREND_THRESHOLD = 0.1


# arbitrage parameters
ARB_ENTER_THRESHOLD = 0.1
ARB_EXIT_THRESHOLD = 0
# 0: no position, 1: buy ETF sell stock, -1: sell ETF buy stock
ARB_TRADE_SHARES = 500

# currency parameters
USD_PER_TRADE = 500000
USD_CLEAR_INTERVAL = 10
