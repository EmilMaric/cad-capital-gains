import requests
from datetime import date, timedelta, datetime
from click import ClickException


class ExchangeRate:
    indicative_rate_min_date = date(2017, 1, 3)
    noon_rate_min_date = date(2007, 5, 1)
    valet_obs_url = 'https://www.bankofcanada.ca/valet/observations'
    observations = "observations"
    currency_to = 'CAD'
    date = 'd'
    value = 'v'
    supported_currencies = ['CAD', 'USD']
    noon_rate_forex_str = {'USD': 'IEXE0101'}

    def __init__(self, currency_from, start_date, end_date):
        self._currency_from = currency_from
        self._start_date = start_date
        self._end_date = end_date
        self._rates = dict()

        if currency_from not in self.supported_currencies:
            raise ClickException(
                "Currency ({}) is not currently supported. The supported "
                "currencies are {}" .format(currency_from,
                                            self.supported_currencies))

        if end_date < start_date:
            raise ClickException(
                "End date must be after start date")
        if start_date < self.noon_rate_min_date:
            raise ClickException(
                "We do not support having transactions before {}"
                .format(self.noon_rate_min_date.isoformat()))
        if end_date > datetime.today().date():
            raise ClickException(
                "We do not support having transactions past today's date")

        if currency_from == self.currency_to:
            # Nothing to do if currencies are the same
            return

        noon_rates = self._fetch_noon_rates(start_date, end_date)
        indicative_rates = self._fetch_indicative_rates(start_date, end_date)
        self._rates.update(noon_rates)
        self._rates.update(indicative_rates)

    def _fetch_rates(self, start_date, end_date, forex_str):
        """Fetch exchange rates from the supplied URL"""
        rates = {}
        # Always move the start date back 7 days in case the start
        # date, end date, and all days in between are all weekends/holidays
        # where no exchange rate can be found
        start_date -= timedelta(days=7)
        params = {"start_date": start_date.isoformat(),
                  "end_date": end_date.isoformat()}
        url = "{}/{}/json".format(self.valet_obs_url, forex_str)
        response = None
        try:
            response = requests.get(url=url, params=params)
        except requests.ConnectionError as e:
            raise ClickException(
                "Error with internet connection to URL {} : {}".format(url, e))
        except requests.HTTPError as e:
            raise ClickException(
                "HTTP request for URL {} was unsuccessful : {}".format(url, e))
        except requests.exceptions.Timeout as e:
            raise ClickException(
                "Request timeout on URL {} : {}".format(url, e))
        except requests.exceptions.TooManyRedirects as e:
            raise ClickException(
                "URL {} was bad : {}".format(url, e))
        except requests.exceptions.RequestException as e:
            raise ClickException(
                "Catastrophic error with URL {} : {}".format(url, e))
        try:
            rates_json = response.json()[self.observations]
        except KeyError:
            raise ClickException(
                "No observations were found using currency {}"
                .format(self._currency_from))
        for day_rate in rates_json:
            date_str = day_rate[self.date]
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            rate = float(day_rate[forex_str][self.value])
            rates[date] = rate
        return rates

    def _fetch_noon_rates(self, start_date, end_date):
        """Get the historical noon rates from the Bank of Canada"""
        if start_date >= self.indicative_rate_min_date:
            # No available noon dates for this date range
            return {}
        if end_date >= self.indicative_rate_min_date:
            # Our date range overlaps with the noon rate and indicative rate
            # boundary
            end_date = self.indicative_rate_min_date - timedelta(days=1)
        forex_str = self.noon_rate_forex_str[self._currency_from]
        return self._fetch_rates(start_date, end_date, forex_str)

    def _fetch_indicative_rates(self, start_date, end_date):
        """Get the indicative rates from the Bank of Canada"""
        if end_date < self.indicative_rate_min_date:
            # No available indicative rates for this date range
            return {}
        if start_date < self.indicative_rate_min_date:
            # Our date range overlaps with the noon rate and indicative rate
            # boundary
            start_date = self.indicative_rate_min_date
        forex_str = "FX{}{}".format(self._currency_from, self.currency_to)
        return self._fetch_rates(start_date, end_date, forex_str)

    def _get_closest_rate_for_day(self, date):
        """Gets the exchange rate for the closest preceeding date with a
        rate
        """
        if date in self._rates:
            return self._rates[date]
        dates_preceeding = [d for d in self._rates if d < date]
        if dates_preceeding:
            closest_date = min(dates_preceeding, key=lambda d: (date - d))
            return self._rates[closest_date]
        return None

    def get_rate(self, date):
        """Gets the exchange rate either:
        (1) for the day if an exchange rate exists for that day
        (2) for the closest preceeding day if an exchange rate does
            not exist for that day"""
        if self._currency_from == self.currency_to:
            # Converting CAD to CAD
            rate = 1.00
        else:
            # Converting Non-CAD to CAD
            rate = self._get_closest_rate_for_day(date)
        if not rate:
            raise ClickException(
                "Unable to find exchange rate on {}".format(date))
        return rate
