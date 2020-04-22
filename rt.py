from datetime import date
import matplotlib.pyplot as plt
import numpy as np
import math

# constants
T = 5 # length of days a person is contageous

def compute_sum(data):
    sum_data = []
    the_sum = 0
    
    for val in data:
        the_sum += val
        sum_data.append(the_sum)

    return sum_data

# read the data
def read_data(fname):
    data = {}
    with open(fname, 'r') as f:
        lines = f.read().split('\n')
        headers = lines[0].split(',')

        # print(f'read headers: {headers} and lines {lines}')

        for header in headers:
            data[header] = []

        data['d'] = []
        data['days'] = []

        for i, line in enumerate(lines[1:]):
            fields = zip(headers, line.split(','))
            # print(f'read fields: {fields}')
            for field in fields:
                # print(f'read field: {field}')
                var = field[0]
                val = field[1]

                if len(val) == 0:
                    continue

                if var == 'date':
                    dfields = val.split('-')
                    mon = int(dfields[0])
                    mday = int(dfields[1])
                    year = int(dfields[2])
                    d = date(year, mon, mday)
                    data['d'].append(d)
                    data['days'].append(i)
                    data[var].append(val)
                else:
                    data[var].append(int(val))
            

    # compute total_cases / total_deaths
    data['total_cases'] = compute_sum(data['daily_cases'])
    data['total_deaths'] = compute_sum(data['daily_deaths'])

    print(f'read in data {data}')
    return data


def compute_r0(k, t):
    r0 = math.exp(k*t)
    print(f' r0 {r0} = e^({k} * {t})')
    return r0

# compute k at a given index, where that index is the last day in the sample
def compute_k(total_cases, last_i):
    # we need to compute doubling time.. we will find how many days backward until cases is >= 0.5 cases(i)
    n_cases = total_cases[last_i]
    n_cases_over_2 = n_cases / 2
    for i, total_cases_i in enumerate(total_cases):
        if total_cases[i] > n_cases_over_2:
            break

    # if i == 0:
    if last_i - i - 1 <= 0:
        return 0

    # linear interpolation
    t_2x = (last_i - i) * (n_cases_over_2 - total_cases[i-1]) / (total_cases[i] - total_cases[i-1]) + (last_i - i - 1) * (total_cases[i] - n_cases_over_2) / (total_cases[i] - total_cases[i-1])
    # t_2x = last_i - i
    # t_2x = last_i - i - 1

    if t_2x < 2:
        t_2x = 2
    

    # print(f'{(last_i - i)} * {(n_cases_over_2 - total_cases[i-1])} / {total_cases[i] - total_cases[i-1]} + {(last_i - i - 1)} * {(total_cases[i] - n_cases_over_2)} / {total_cases[i] - total_cases[i-1]}')
    # print(f't_2x: {t_2x} i:{i} last_i:{last_i} total_cases[i]: {total_cases[i]} total_cases[i-1]: {total_cases[i-1]} n_cases:{n_cases} n_cases_over_2:{n_cases_over_2}')

    K = np.log(2) / t_2x

    return K 


def compute_r0_over_dataset(data):
    r0_data = []
    for i, val in enumerate(data):
        K = compute_k(data, i)
        r0 = compute_r0(K, T)
        r0_data.append(r0)

    return r0_data

def single_plot(ax, y, x, y_label, x_label, fontsize=12, ploty=None):
    ax.plot(x, y)
    if ploty:
        y = np.ones((len(x))) * ploty 
        ax.plot(x, y)

    # ax.locator_params(nbins=3)
    ax.set_xlabel(x_label, fontsize=fontsize)
    ax.set_ylabel(y_label, fontsize=fontsize)
    # ax.set_title('Title', fontsize=fontsize)
      

def plot_data(data, start_i=0):
    plt.close('all')

    fig, ((ax1, ax2, ax5), (ax3, ax4, ax6)) = plt.subplots(nrows=2, ncols=3)
    single_plot(ax1, data['total_cases'][start_i:], data['days'][start_i:], 'total_cases', 'days')
    single_plot(ax2, data['daily_cases'][start_i:], data['days'][start_i:], 'daily_cases', 'days')
    single_plot(ax5, data['r0_cases'][start_i:], data['days'][start_i:], 'r0_cases', 'days', ploty=1)
    single_plot(ax3, data['total_deaths'][start_i:], data['days'][start_i:], 'total_deaths', 'days')
    single_plot(ax4, data['daily_deaths'][start_i:], data['days'][start_i:], 'daily_deaths', 'days')
    single_plot(ax6, data['r0_deaths'][start_i:], data['days'][start_i:], 'r0_deaths', 'days', ploty=1)

    plt.show()

data = read_data('data_mexico.csv')
data['r0_cases'] = compute_r0_over_dataset(data['total_cases'])
data['r0_deaths'] = compute_r0_over_dataset(data['total_deaths'])
plot_data(data, start_i = 20)
