#!/usr/bin/env python3
import time
import json
import tortools
import sys

url_template = "https://graphs.coinmarketcap.com/currencies/{currency}/{t1}/{t2}/"
time_period = 365  # days

tor_session = tortools.get_tor_session()


def download(currency: str, t1: int, t2: int) -> list:
    global tor_session

    t1 *= 1000
    t2 *= 1000

    for i in range(20):
        try:
            url = url_template.format(currency=currency, t1=t1, t2=t2)
            resp = tor_session.get(url)
            data = json.loads(resp.content.decode())
            resp.close()

            return data['price_usd']

        except KeyboardInterrupt:
            raise

        except:
            time.sleep(10)
            tortools.change_tor_ip()
            tor_session = tortools.get_tor_session()
            print('Changed Tor IP')

    raise Exception('We tried to change tor IP 20 times - no success')


def download_all(currency: str) -> list:
    """
    Download data for currency day-by-day
    """
    now = int(time.time())
    start = now - 86400 * time_period
    data = []

    for i, t in enumerate(range(start, now, 86400)):
        data += download(currency, t, t + 86400 - 1)
        print('Fetching {currency} data: {percent:3.1f}%'.format(
            currency=currency, percent=100 * i / time_period))

    return data


if __name__ == '__main__':
    if len(sys.argv) > 1:
        currency = sys.argv[1]
    else:
        currency = 'bitcoin'

    data = download_all(currency)
    print(len(data))
    with open('data/%s.json' % currency, 'w') as f:
        json.dump(data, f)
