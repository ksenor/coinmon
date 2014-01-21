import argparse
from datetime import datetime

import requests


GIVE_ME_COINS_URL = 'https://give-me-coins.com/pool/api-ltc'
BTC_E_TICKER = 'https://btc-e.com/api/2/ltc_usd/ticker'


def coin_str(coin, usd_avg, usd_buy):
    coin = float(coin)
    usd_avg = float(usd_avg)
    usd_buy = float(usd_buy)
    return '%0.5f ($%0.3f, $%0.3f)' % (coin, coin * usd_avg, coin * usd_buy)

def strip_user(username, text):
        return text.replace(username+'.', '')


def status_str(alive, last_share):
    last_share = int(last_share or 0)
    last_share_str = str(datetime.fromtimestamp(last_share))
    down_str = 'DOWN! (%s)' % last_share_str
    status = 'OK' if alive == '1' else down_str
    return status


def print_stats(api_key):

    ticker = requests.get(BTC_E_TICKER).json()['ticker']
    usd_avg = ticker['avg']
    usd_buy = ticker['buy']

    stats = requests.get(GIVE_ME_COINS_URL,
                         params={'api_key': api_key}).json()
    username = stats['username']
    uncashed = stats['confirmed_rewards']
    history = stats['payout_history']
    shares = stats['round_shares']
    estimate = stats['round_estimate']
    total_hashrate = stats['total_hashrate']

    exchange_str = coin_str(1, usd_avg, usd_buy)
    uncashed_str = coin_str(uncashed, usd_avg, usd_buy)
    round_str = coin_str(estimate, usd_avg, usd_buy)
    history_str = coin_str(history, usd_avg, usd_buy)

    print 'LTC/USD: %s' % exchange_str
    print 'Total Hash: %s kh/s, Shares: %s' % (total_hashrate, shares)
    print 'Uncashed: %s' % uncashed_str
    print 'Round Est.: %s' % round_str
    print 'History: %s' % history_str 

    for worker, worker_stats in stats['workers'].iteritems():
        status = status_str(worker_stats['alive'],
                            worker_stats['last_share_timestamp'])
        hashrate = worker_stats['hashrate']
        percent_hashrate = float(hashrate)/float(total_hashrate)*100
        
        worker_vals = (strip_user(username, worker), status,
                       hashrate, percent_hashrate)
        print '%s - S: %s, R: %s kh/s, P: %0.2f%%' % worker_vals


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Give-me-coins API Watcher')
    parser.add_argument('-k', '--apikey',
                        required=True)
    args = parser.parse_args()
    print_stats(args.apikey)