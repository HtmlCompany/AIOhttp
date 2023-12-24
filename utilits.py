from datetime import datetime, timedelta

from defines import AVAILABLE_CURRENCIES


def count_days(argv):
    try:
        days = int(argv[1]) if len(argv) > 1 else 1
    except ValueError:
        days = 1
    if not 0 < days <= 10:
        days = 1
    return days


def get_date(total_days=1):
    today = datetime.now()
    res = []
    for day in range(total_days):
        d = datetime.strftime(today - timedelta(days=day), '%d.%m.%Y')
        res.append(d)
    return res


def get_currencies(argv):
    currencies = list(argv[2:])
    for cr in currencies:
        if cr not in AVAILABLE_CURRENCIES:
            currencies.remove(cr)
    if not currencies:
        currencies = ['EUR', 'USD']
    
    return set(currencies)