# Functions to implement our trading strategy.
import numpy as np
import trading.process as proc
import trading.indicators as ind
import matplotlib.pyplot as plt

def random(stock_prices, period = 7, amount = 5000, fees = 20, ledger = 'random_ledger.txt'):
    '''
    Randomly decide, every period, which stocks to purchase,
    do nothing, or sell (with equal probability).
    Spend a maximum of amount on every purchase.

    Input:
        stock_prices (ndarray): the stock price data
        period (int, default 7): how often we buy/sell (days)
        amount (float, default 5000): how much we spend on each purchase
            (must cover fees)
        fees (float, default 20): transaction fees
        ledger (str, default 'ledger_random.txt'): path to the ledger file

    Output: None
    '''
    
    # get number of stocks and number of days
    number_of_days, N = stock_prices.shape

    # initialize portfolio
    portfolio = proc.create_portfolio(N * [amount], stock_prices, fees, ledger)
    
    # set default random number generator
    rng = np.random.default_rng()
    
    # loop over each period
    for day in range(period, number_of_days, period):
                         
        # set probabilities equal to 1/3
        random_number = rng.choice([0, 1, 2], p = 3 * [1 / 3])
                         
        # if number is equal to 0, we buy
        if random_number == 0:
            
            # if we only have one stock in our portfolio buy it
            if N == 1:
                proc.buy(day, 0, amount, stock_prices, fees, portfolio, ledger)
                            
            # randomly decide which stocks to purchase
            # draw a random amount of stock numbers which are themsleves chosen at random
            else:
                stocks = rng.integers(0, N, rng.integers(0, N))

                # buy each of these stocks
                for i in stocks:
                    proc.buy(day, i, amount, stock_prices, fees, portfolio, ledger)
        
        # if number is equal to 1, we sell
        elif random_number == 1:
            
            # if we only have one stock in our portfolio sell it (if we have shares)
            if N == 1 and portfolio[0] > 0:
                proc.sell(day, 0, stock_prices, fees, portfolio, ledger)
                
            # randomly decide which stocks to sell
            # draw a random amount of stock numbers which are themsleves chosen at random
            else:
                stocks = rng.integers(0, N, rng.integers(0, N))
                for i in stocks:
                    # if we have stocks to sell, sell them
                    if portfolio[i] > 0:
                        proc.sell(day, i, stock_prices, fees, portfolio, ledger)

    # if number is equal to 2 we do nothing and go to next period and sell our portfolio at the end        
    for stock_number in range(N):
        proc.sell(number_of_days - 1, stock_number, stock_prices, fees, portfolio, ledger)
    
    
def crossing_averages(stock_prices, amount = 5000, n = 200, m = 50, n_weights = [], m_weights = [], plot = False, fees = 20, ledger = 'crossing_average_ledger.txt'):
    '''
    Decide to buy shares when the m-day moving average crosses the n-day moving average from below, and decide to sell shares when the m-day moving average crosses the n-day mving average from above.
    
    Input:
        stock_prices (ndarray): the stock price data
        amount (float, default 5000): how much we spend on each purchase
            (must cover fees)
        n (int, default 200): period in days for the slow moving average (n > m)
        m (int, default 50): period in days for the fast moving average (m < n)
        n_weights (list, default []): must be of length n if specified. Indicates the weights
            to use for the weighted average. If empty, return a non-weighted average.
        m_weights (list, default []): must be of length m if specified. Indicates the weights
            to use for the weighted average. If empty, return a non-weighted average.
        plot (boolean, default False): Plots moving averages if True.
        fees (float, default 20): transaction fees
        ledger (str, default 'crossing_average_ledger.txt'): path to the ledger file
        
    Output: None
    '''
    # get number of stocks and number of days
    total_days, N = stock_prices.shape
    
    # initialize portfolio
    portfolio = proc.create_portfolio(N * [amount], stock_prices, fees, ledger)
    
    # initialize MA arrays, both must have same size to match up the dates
    m_day_MA = np.zeros((total_days, N))
    n_day_MA = np.zeros((total_days, N))
    
    # start by getting n-day and m-day MA arrays for each stock
    for stock in range(N):
        
        # get n_day MA
        n_day_MA[:, stock] = ind.moving_average(stock_prices[:, stock], n, n_weights) 
        
        # get m_day MA
        m_day_MA[:, stock] = ind.moving_average(stock_prices[:, stock], m, m_weights) 
    
    # now loop through each day starting from day n + 1 (index n) and buy, sell as appropriate
    for day in range(n, total_days):
        # loop through each stock
        for stock in range(N):
            # if it crosses from below, we buy
            if m_day_MA[day - 1, stock] < n_day_MA[day - 1, stock] and m_day_MA[day, stock] > n_day_MA[day, stock]:
                proc.buy(day, stock, amount, stock_prices, fees, portfolio, ledger)
            # if it crosses from above, we sell
            elif m_day_MA[day - 1, stock] > n_day_MA[day - 1, stock] and m_day_MA[day, stock] < n_day_MA[day, stock]:
                proc.sell(day, stock, stock_prices, fees, portfolio, ledger)
    
    
    # sell portfolio at end
    for stock_number in range(N):
        proc.sell(total_days - 1, stock_number, stock_prices, fees, portfolio, ledger)
    
    # option to see plot
    if plot == True:
        plt.plot(n_day_MA)
        plt.plot(m_day_MA)
        plt.legend([f'{n}-day MA', f'{m}-day MA'])
        plt.xlabel('Time (days)')
        plt.ylabel('Price ($)')
        plt.title(f'{n}-day MA vs {m}-day MA')
    
def momentum(stock_prices, osc_type = 'stochastic', lower = 0.25, upper = 0.75, n = 7, wait_time = 3, plot = False, smoothing_period = False, amount = 5000, fees = 20, ledger = 'momentum_ledger.txt'):
    '''
    Decide to sell shares in a portfolio when chosen oscillator is above upper threshold and buy when below lower threshold.
    
    Input:
        stock_prices (ndarray): the stock price data
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.
        lower (float, default 0.25): lower threshold
        upper (float, default 0.75): upper threshold
        n (int, default 7): period of the oscillator (in days).
        wait_time (int, default 10): period (in days) to wait before buying/selling stock if price remains below/above threshold.
        smoothing_period (int, default = False): period of moving average to be applied to the oscillator.
        plot (boolean, default False): shows plot of oscillator if True.
        
        amount (float, default 5000): how much we spend on each purchase
            (must cover fees)
        
        fees (float, default 20): transaction fees
        ledger (str, default 'crossing_average_ledger.txt'): path to the ledger file
        
    Output: None
    '''
    
    # get number of stocks and number of days
    total_days, N = stock_prices.shape
    
    # initialize portfolio
    portfolio = proc.create_portfolio(N * [amount], stock_prices, fees, ledger)
    
    # initialize oscillator array
    oscillator = np.zeros(stock_prices.shape)
    
        
    
    # get the oscillator for each stock
    for stock in range(N):

        oscillator[:, stock] = ind.oscillator(stock_prices[:, stock], n, osc_type, smoothing_period)
    
    # get starting day of trading
    if smoothing_period != False and smoothing_period != 0:        
        day_1 = n + smoothing_period - 1
    
    else:
        day_1 = n - 1
        
    # initialize indicator matrix which indicates we can buy after waiting time
    indicator_matrix = np.zeros(oscillator.shape)
    
    
    # now loop through each day to decide whether to buy or sell and implement the wait time
    for day in range(day_1, total_days):
        
        #loop through each stock 
        for stock in range(N):

            # check if oscillator is below lower threshold and this is first time we cross threshold
            if oscillator[day, stock] < lower:

                # if this is first time we cross then indicate to buy after waiting time
                if oscillator[(day - 1), stock] >= lower:
                    indicator_matrix[day, stock] = 1 

                # check indicator matrix, if 1 and stock remained below threshold we buy
                elif indicator_matrix[(day - wait_time), stock] == 1 and np.all(oscillator[(day - wait_time) : day, stock] < lower) == True:

                    # buy the stock
                    proc.buy(day, stock, amount, stock_prices, fees, portfolio, ledger)

            # check if oscillator is oscillator is above upper threshold and if we have shares to sell. Implement waiting time method
            elif oscillator[day, stock] > upper and portfolio[stock] != 0:
                
                # if this is first time we cross then indicate to sell after waiting time
                if oscillator[day - 1, stock] <= upper:
                    indicator_matrix[day, stock] = -1 

               # check indicator matrix, if -1 and stock remained above threshold we sell
                elif indicator_matrix[(day - wait_time), stock] == -1 and np.all(oscillator[(day - wait_time) : day, stock] > upper) == True:

                    # sell the stock
                    proc.sell(day, stock, stock_prices, fees, portfolio, ledger)           
                
     
    # sell portfolio at the end
    for stock_number in range(N):
        proc.sell(total_days - 1, stock_number, stock_prices, fees, portfolio, ledger)
    
    # option to plot oscillator with thresholds
    if plot == True:
        plt.plot(oscillator)
        plt.hlines(upper, n, total_days, colors = 'r', linestyles = '--')
        plt.hlines(lower, n, total_days, colors = 'r', linestyles = '--')
        plt.xlabel('Time (days)')
        plt.ylabel('Value')
        plt.legend(['Oscillator', 'Upper Threshold', 'Lower Threshold'])
        plt.title(f'{osc_type} Oscillator, Upper Threshold = {upper}, Lower Threshold = {lower}')
    
    