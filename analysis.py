import config
import matplotlib.pyplot as plt
import datetime as dt

def plotXY(X, Y):
    plt.plot_date(X, Y, fmt='k-')
    plt.tight_layout()
    plt.show()


def get_datetimes_and_postids(get_time=True):
    datetimes = []
    post_count = 0
    post_ids = []
    with open(config.datetimes_file, 'r') as fin:
        for line in fin:
            if get_time:
                line = line.replace('.000Z\n', '')
            else:
                line = line.split('T')[0]
            datetime = dt.datetime.fromisoformat(line)
            datetimes.append(datetime)
            post_ids.append(post_count)
            post_count -= 1
    return datetimes, post_ids


def compress(dates, values):
    """
    inputs:
        dates      | values
        -----------+--------
        25-12-2019 | 5
        25-12-2019 | 6
        25-12-2019 | 7
        25-12-2019 | 8
        25-12-2019 | 9
        25-12-2019 | 10
        29-12-2019 | 11
        29-12-2019 | 12
        29-12-2019 | 13
        03-01-2020 | 14
        03-01-2020 | 15
        03-01-2020 | 16
        03-01-2020 | 17

    returns:
        dates      | values
        -----------+--------
        25-12-2019 | 10
        29-12-2019 | 13
        03-01-2020 | 17
    """
    if len(dates) != len(values):
        raise Exception("Length of dates and values must match.")

    dates.sort()
    values.sort()

    compressed_dates = []
    compressed_values = []

    compresser = {}

    for d, v in zip(dates, values):
        compresser[d] = v
    
    for d, v in compresser.items():
        compressed_dates.append(d)
        compressed_values.append(v)

    return compressed_dates, compressed_values


def interpolate(dates, values):
    """
    inputs:
        dates      | values
        -----------+--------
        25-12-2019 | 5
        29-12-2019 | 8
        03-01-2020 | 10

    returns:
        dates      | values
        -----------+--------
        25-12-2019 | 5
        26-12-2019 | 5
        27-12-2019 | 5
        28-12-2019 | 5
        29-12-2019 | 8
        30-12-2019 | 8
        31-12-2019 | 8
        01-01-2020 | 8
        02-01-2020 | 8
        03-01-2020 | 10
    """
    if len(dates) != len(values):
        raise Exception("Length of dates and values must match.")

    index = 0

    dates.sort()
    values.sort()

    filled_in_dates = []
    filled_in_values = []

    while True:
        current_date = dates[index]
        current_value = values[index]
        
        filled_in_dates.append(current_date)
        filled_in_values.append(current_value)
        
        prev_value = current_value
        
        expected_next_date = current_date + dt.timedelta(days=1)
        index += 1

        if index == len(dates):
            break

        while expected_next_date != dates[index]:
            if expected_next_date > dates[index]:
                raise Exception('dates and values must be compressed before interpolation.')

            filled_in_dates.append(expected_next_date)
            filled_in_values.append(prev_value)
            expected_next_date = expected_next_date + dt.timedelta(days=1)
        
    return filled_in_dates, filled_in_values


def get_postrate(dates, values, rate):
    """
    rate: number of days

    input:
        rate: 2
        -----------+--------
        dates      | values
        -----------+--------
        25-12-2019 | 5
        26-12-2019 | 5
        27-12-2019 | 5
        28-12-2019 | 5
        29-12-2019 | 8
        30-12-2019 | 8
        31-12-2019 | 8
        01-01-2020 | 8
        02-01-2020 | 8
        03-01-2020 | 10

    returns:
        dates      | values
        -----------+--------
        25-12-2019 | 0
        26-12-2019 | 0
        27-12-2019 | 3
        28-12-2019 | 3
        29-12-2019 | 0
        30-12-2019 | 0
        31-12-2019 | 0
        01-01-2020 | 2
    """
    if len(dates) != len(values):
        raise Exception("Length of dates and values must match.")

    index = 0
    
    rate_dates = []
    rate_values = []

    while True:
        first_date = dates[index]
        first_value = values[index]

        if index + rate >= len(dates):
            break

        next_value = values[index + rate]
        rate_value = next_value - first_value

        rate_dates.append(first_date)
        rate_values.append(rate_value)

        index += 1

    return rate_dates, rate_values


"""
script
"""
dates, postids = get_datetimes_and_postids(False)
dates, postids = compress(dates, postids)
dates, postids = interpolate(dates, postids)
rdates, rates = get_postrate(dates, postids, 7)
plotXY(dates, postids)
plotXY(rdates, rates)