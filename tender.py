import requests
import executions
import time
import config
import arbitrage

TENDER_STATUS = 0 
TENDER_POSITION = 0 # current tender position
TENDER_ID = "NA"

def accept_tender(session, t_id):
    resp = session.post('http://localhost:9999/v1/tenders/{}'.format(t_id))
    if not resp.ok:
        print("tender posting failed")
        return False
    else:
        print(resp)
        print("tender accepted")
        return True
    

def reject_tender(session, t_id):
    resp = session.delete('http://localhost:9999/v1/tenders/{}'.format(t_id))
    if not resp.ok:
        print("tender rejection failed")
        return False
    else:
        print("tender rejected")
        return True

    
def select_tender(session):
    global TENDER_STATUS
    global TENDER_POSITION
    global TENDER_ID
    
    resp = session.get('http://localhost:9999/v1/tenders')
    if resp.ok:
        # USDbid, USDask = executions.ticker_bid_ask(session, 'USD')
        
        all_tenders = resp.json()
        for tender in all_tenders:
            t_id, quantity, price, action, expiry = tender['tender_id'], tender['quantity'], tender['price'], tender['action'], tender['expires']
            print(t_id, quantity, price, action, expiry)
            RITCbid_1, RITCask_1 = executions.ticker_bid_ask(session, 'RITC')
            time.sleep(1)
            RITCbid_2, RITCask_2 = executions.ticker_bid_ask(session, 'RITC')
            
            tick = executions.get_tick(session)
            # BUY cheap tender and sell at the market bid
            if action == 'BUY':
                # profit per share if accept the tender and trade at the market
                spread = RITCbid_2 - price - config.fee
                time_left = expiry - tick
                bid_change = RITCbid_2 - RITCbid_1
                print(spread >= config.TENDER_THRESHOLD, time_left >= 1, bid_change > -config.TENDER_TREND_THRESHOLD)
                if spread >= config.TENDER_THRESHOLD and time_left >= 1 and bid_change > -config.TENDER_TREND_THRESHOLD:
                    response = accept_tender(session, t_id)
                    if response:
                        TENDER_STATUS = 1
                        TENDER_POSITION += quantity
                        TENDER_ID = t_id
                        print("BUY tender {} accepted with spread {}".format(t_id, spread))
                # else:
                #     reject_tender(session, t_id)
                #     print("SELL tender {} rejected with spread {}".format(t_id, spread))
                    
            # SELL expensive tender and buy at the market ask      
            elif action == 'SELL':
                # profit per share if accept the tender and trade at the market
                spread = price - RITCask_2 - config.fee
                time_left = expiry - tick
                ask_change = RITCask_2 - RITCask_1
                print(spread >= config.TENDER_THRESHOLD, time_left >= 1, ask_change < config.TENDER_TREND_THRESHOLD)
                if spread >= config.TENDER_THRESHOLD and time_left >= 1 and ask_change < config.TENDER_TREND_THRESHOLD:
                    response = accept_tender(session, t_id)
                    if response:
                        TENDER_STATUS = -1
                        TENDER_POSITION -= quantity
                        TENDER_ID = t_id
                        print("SELL tender {} accepted with spread {}".format(t_id, spread)) 
                # else:
                #     reject_tender(session, t_id)
                #     print("BUY tender {} rejected with spread {}".format(t_id, spread))

    
def reverse_tender(session):
    global TENDER_STATUS
    global TENDER_POSITION
    global TENDER_ID
        
    # bought cheap tender, now sell them out
    if TENDER_STATUS == 1:
        # clear all tender positionz   
        while TENDER_POSITION > 0:
            amount = min(config.TENDER_CLEAR_SHARES, TENDER_POSITION)
            executions.make_order("RITC", "MARKET", amount, "SELL")
            TENDER_POSITION -= amount
            print("tender {} cleared once, {} shares remains".format(TENDER_ID, TENDER_POSITION))
            time.sleep(0.1)
            if arbitrage.ARBITRAGE_STATUS != 0:
                arbitrage.close_arbitrage(session)
        
        print("tender {} cleared!".format(TENDER_ID))
        TENDER_STATUS = 0
        TENDER_ID = 'NA'
        
    # sold expensive tender, now buy them back    
    elif TENDER_STATUS == -1:
        while TENDER_POSITION < 0:
            amount = min(config.TENDER_CLEAR_SHARES, abs(TENDER_POSITION))
            executions.make_order("RITC", "MARKET", amount, "BUY")
            TENDER_POSITION += amount
            print("tender {} cleared once, {} shares remains".format(TENDER_ID, TENDER_POSITION))
            time.sleep(0.1)
            if arbitrage.ARBITRAGE_STATUS != 0:
                arbitrage.close_arbitrage(session)
        
        print("tender {} cleared!".format(TENDER_ID))
        TENDER_ID = 'NA'
        TENDER_STATUS = 0
        
       