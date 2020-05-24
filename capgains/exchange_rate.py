import requests
from datetime import date, timedelta
from click import ClickException


class ExchangeRate:
    min_date = date(2017, 1, 3)
    valet_obs_url = 'https://www.bankofcanada.ca/valet/observations'
    observations = "observations"
    currency_to = 'CAD'
    date = 'd'
    value = 'v'

    def __init__(self, currency_from, start_date, end_date):
        self._currency_from = currency_from
        self._start_date = start_date
        self._end_date = end_date

        if end_date < start_date:
            raise ClickException(
        "End date must be after start date")
        if end_date < self.min_date:
            raise ClickException(
        "Date range before minimum date {}".format(self.min_date.isoformat()))

        # always move the start date back 7 days in case the start
        # date, end date, and all days in between are all weekends/holidays
        # where no exchange rate can be found
        start_date -= timedelta(days=7)

        # Query for all the exchange rates in the range specified, and
        # populates a dictionary that maps dates to exchange rates.
        try:
            params = {"start_date": start_date.isoformat(),
                      "end_date": end_date.isoformat()}
            format_str = "FX{}{}".format(self._currency_from, self.currency_to)
            url = "{}/{}/json".format(self.valet_obs_url, format_str)
            response = requests.get(url = url, params=params)
            try:
                rates = response.json()[self.observations]
            except KeyError:
                raise ClickException(
            "No observations were found using currency {}"
            .format(self._currency_from))
            self._rates = dict()
            for rate in rates:
                self._rates[rate[self.date]] = float(rate[format_str][self.value])
        except requests.exceptions.Timeout as e:
            raise ClickException(
                "Request timeout on URL {} : {}".format(url, e))
        except requests.exceptions.TooManyRedirects as e:
            raise ClickException(
                "URL {} was bad".format(url))
        except requests.exceptions.RequestException as e:
            raise ClickException(
                "Catastrophic error with URL {} : {}".format(url, e))

    @property
    def currency_from(self):
        return self._currency_from

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    def _get_last_rate_in_range(self, date):
        """Gets the exchange rate for the closest preceeding date with a rate"""
        while date > self.min_date:
            date_str = date.isoformat()
            if date_str in self._rates:
                return self._rates[date_str]
            date = date - timedelta(days=1)
        return None


    def get_rate(self, date):
        """Gets the exchange rate either:
        (1) for the day if an exchange rate exists for that day
        (2) for the closest preceeding day if an exchange rate does
            not exist for that day"""
        rate = self._get_last_rate_in_range(date)
        if not rate:
            raise ClickException(
            "Unable to find exchange rate on {}".format(date))
        return rate
        
        
            
