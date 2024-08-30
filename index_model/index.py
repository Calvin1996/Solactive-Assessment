import datetime as dt
import pandas as pd


class IndexModel:
    def __init__(self):
        # read price data
        self.price_data = pd.read_csv("./data_sources/stock_prices.csv", parse_dates=["Date"], index_col=["Date"], dayfirst=True)
        self.index_values: pd.DataFrame

    def get_index_constituents(self, date: dt.date, current_index_value: float) -> pd.DataFrame:
        relevant_price_data = self.price_data.loc[str(prev_business_day(date))]
        # assume all companies have 1 share outstanding: price = marketCap
        largest_market_caps = sorted(list(relevant_price_data.values), reverse=True)[:3]
        current_price_data = self.price_data.loc[str(date)]
        number_shares = [float(0.5 / y * current_index_value if x == largest_market_caps[0]
                               else 0.25 / y * current_index_value if x in largest_market_caps[1:]
                               else 0
                               )
                         for x, y in zip(relevant_price_data.values, current_price_data.values)]
        return pd.DataFrame(data=number_shares, index=self.price_data.columns)

    def calc_index_level(self, start_date: dt.date, end_date: dt.date):
        dates = [start_date]
        index_values = [100.0]
        number_shares = self.get_index_constituents(start_date, index_values[0])
        while start_date < end_date:
            previous_day_market_value = float(self.price_data.loc[str(start_date)].dot(number_shares).values[0])
            actual_day_market_value = float(self.price_data.loc[str(next_business_day(start_date))].dot(number_shares).values[0])
            return_rate = actual_day_market_value / previous_day_market_value
            index_value = index_values[-1] * return_rate
            start_date = next_business_day(start_date)
            index_values.append(index_value)
            dates.append(start_date)
            # get new index constituents at the beginning of month
            if start_date.month != prev_business_day(start_date).month:
                number_shares = self.get_index_constituents(start_date, index_value)

        self.index_values = pd.DataFrame({"Date": dates, "index_level": index_values})
        return

    def export_values(self, file_name: str):
        self.index_values.to_csv(file_name, index=False)
        return


def is_weekend(date: dt.date) -> bool:
    return date.isoweekday() == 6 or date.isoweekday() == 7


def next_business_day(date: dt.date) -> dt.date:
    date += dt.timedelta(days=1)
    while is_weekend(date):
        date += dt.timedelta(days=1)
    return date


def prev_business_day(date: dt.date) -> dt.date:
    date -= dt.timedelta(days=1)
    while is_weekend(date):
        date -= dt.timedelta(days=1)
    return date
