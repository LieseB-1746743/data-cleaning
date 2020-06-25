import pandas as pd
import numpy as np
from .actions import OnOutlierDetect


class OutlierDetection:
    def __init__(self, data):
        """
        :param data: The data as a Pandas.Series object
        """
        self.original_data = data
        self.interval = None
        self.action = OnOutlierDetect.FLAG

    def set_action(self, action):
        """
        Set action (action = what must happen on outlier detection), type(action) == <class: Action>
        :param action: integer representing the action (1,2,3 or 4)
        """
        if action in set([action.value for action in OnOutlierDetect]):
            self.action = OnOutlierDetect(action)

    def absolute_deviation_from_median(self, value, median):
        abs_dev = abs(value - median)
        return abs_dev

    def MAD(self, median, values):
        """ Calculate the median absolute deviation. """
        absolute_deviations = values.apply(self.absolute_deviation_from_median, args=(median,))
        mad = absolute_deviations.median()
        return mad

    def calc_interval(self):
        """
        Calculate the interval containing all non-outlier values, according to the Hampel X84 technique.
        Interval will be saved as a tuple (min,max) in self.interval.
        """
        values = self.original_data.copy()
        values.dropna(inplace=True)
        if np.issubdtype(self.original_data.dtype, np.datetime64):
            values = (values - pd.Timestamp("1970-01-01")) // pd.Timedelta("1d")
        median = values.median()
        mad = self.MAD(median, values)

        nDeviations = 2
        hampel_constant = 1.4826
        interval_min = median - (nDeviations * hampel_constant * mad)
        interval_max = median + (nDeviations * hampel_constant * mad)
        if np.issubdtype(self.original_data.dtype, np.datetime64):
            interval_min = pd.to_datetime(interval_min, unit='d', origin=pd.Timestamp("1970-01-01"))
            interval_min = interval_min.strftime("%Y-%m-%d")
            interval_max = pd.to_datetime(interval_max, unit='d', origin=pd.Timestamp("1970-01-01"))
            interval_max = interval_max.strftime("%Y-%m-%d")
        interval = (interval_min, interval_max)
        self.interval = interval
