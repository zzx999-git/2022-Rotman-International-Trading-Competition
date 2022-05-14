import requests
import time
import arbitrage
import config
import tender
import executions


def main():
    LAST_USD_CLEAR_TICK = 0 # the last time that usd got cleared
    count = 0
    executions.refresh_parameters()
    with requests.Session() as s:
        s.headers.update(config.API_KEY)
        tick = executions.get_tick(s)
        while tick >= 1 and tick <= 295:
            with requests.Session() as s:
                s.headers.update(config.API_KEY)
                
                # arbitrage
                if arbitrage.ARBITRAGE_STATUS == 0:
                    arbitrage.trade_arbitrage(s)
                else:
                    print("try close!")
                    arbitrage.close_arbitrage(s)
                    
                # tender
                if tender.TENDER_STATUS == 0:
                    tender.select_tender(s)
                else:
                    tender.reverse_tender(s)
                    print(tender.TENDER_STATUS)
                    print(tender.TENDER_POSITION)
                
                tick = executions.get_tick(s)
                if tick - LAST_USD_CLEAR_TICK >= config.USD_CLEAR_INTERVAL:
                    executions.clear_USD(s)
                    LAST_USD_CLEAR_TICK = tick
                    count += 1
                    print("{} {}".format(tick, count))
                    
   

if __name__ == '__main__':
    main()

