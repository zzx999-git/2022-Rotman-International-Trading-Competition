# -*- coding: utf-8 -*-

import requests
import config
import time
import tender
import arbitrage

class ApiException(Exception):
    pass

# get currect time elasped
def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick']
    raise ApiException('Authorization error. Please check API key.')


# get the current bid and ask price of ticker
def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return (book['bids'][0]['price'], book['asks'][0]['price'])   
    raise ApiException('Authorization error. Please check API key.')

# get the current bid and ask price & quantity of ticker
def ticker_bid_ask_and_quant(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json() 
        return (book['bids'][0]['price'], book['asks'][0]['price'], book['bids'][0]['quantity'], book['asks'][0]['quantity'])
    raise ApiException('Authorization error. Please check API key.')    

    

def get_position(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities', params=payload)
    info = resp.json()
    return info[0]['position']
    
    
def make_order(ticker, orderType, quantity, action):
    order_status = order(ticker, orderType, quantity, action)
    
    while not order_status:
        time.sleep(1)
        print("Try submitting again!")
        order_status = order(ticker, orderType, quantity, action)
    
    
def order(ticker, orderType, quantity, action):
    with requests.Session() as s:
        s.headers.update(config.API_KEY)
        RITCbid, RITCask = ticker_bid_ask(s, 'RITC')
        Bullbid, Bullask = ticker_bid_ask(s, 'BULL')
        Bearbid, Bearask = ticker_bid_ask(s, 'BEAR') 
        mkt_params = {'ticker': ticker, 'type': orderType, 'quantity': quantity, 
                      'action': action}
            
        resp = s.post('http://localhost:9999/v1/orders', params=mkt_params)
        # print(mkt_params)
        
        if resp.ok:
            mkt_order = resp.json()
            print('time:', mkt_order['tick'], 'ticker:', mkt_order['ticker'], 
                  'action:', mkt_order['action'], 'was successfully submited!')
            return True
        else:
            return False
        
def clear_USD(session):
    USDbid, USDask = ticker_bid_ask(session, "USD")
    position = get_position(session, "USD")
    while position > 0:
        amount = min(position, config.USD_PER_TRADE)
        make_order("USD", "MARKET", amount, "SELL")
        time.sleep(0.1)
        position = get_position(session, "USD")
    while position < 0:
        amount = min(abs(position), config.USD_PER_TRADE)
        make_order("USD", "MARKET", amount, "BUY")
        time.sleep(0.1)
        position = get_position(session, "USD")
    
    
    # if USDbid <= 0.99 and position > 0:
    #     make_order("USD", "MARKET", position, "SELL")
    #     time.sleep(0.1)
    # elif USDask >= 1.01 and position < 0:
    #     make_order("USD", "MARKET", abs(position), "BUY")
    #     time.sleep(0.1)
    
def refresh_parameters():
    tender.TENDER_STATUS = 0
    tender.TENDER_ID = "NA"
    arbitrage.ARBITRAGE_STATUS = 0
    
