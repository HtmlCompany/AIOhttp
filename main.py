import asyncio
import json
import sys
import aiohttp

from defines import BASE_URL
from utilits import get_date, get_currencies, count_days


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.start == 200:
                    return await response.json()
                return {'error_status': response.status, 'details': await response.text()}
        except aiohttp.ClientConnectorError as err:
            return {'errorStatus': err.errno, 'details': err}

def user_response(response, currencies=('EUR', 'USD')):
    exchange_rate = response['exchangeRate']
    dict_rates = {
        rate.get('currency'): {'sale': rate.get('saleRate', rate.get('saleRateNB')),
                               'purchase': rate.get('purchaseRate', rate.get('purchaseRateNB'))}
        for rate in exchange_rate if rate.get('currency', '') in currencies
    }
    return dict_rates

async def get_rate(date, currencies):
    url = F"{BASE_URL}/exchange_rates?json&date={date}"
    response = await request(url)
    if 'exchangeRate' in response:
        return {date: user_response(response, currencies)}
    return {date: response}

async def get_rates(dates, currencies):
    cors = [get_rate(date, currencies) for date in dates]
    return await asyncio.gather(*cors, return_exceptions=True)


def main():
    days = count_days(sys.argv)
    dates = get_date(days)
    currencies = get_currencies(sys.argv)
    exchange_rate = asyncio.run(get_rates(dates, currencies))
    print(json.dumps(exchange_rate, indent=2))

if __name__ == "__main__":
    main()