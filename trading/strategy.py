# Functions to implement our trading strategy.
import numpy as np
import trading.process as proc
import trading.indicators as ind
import matplotlib.pyplot as plt

def random(stock_prices, period = 7, amount = 5000, fees = 20, ledger = 'random_ledger.txt'):
    '''
    Randomly decide, every period, which stocks to purchase, do nothing, or sell (with equal probability). Spend a maximum of amount on every purchase. Records transaction data in given ledger.

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
    
    # loop over each period, we buy on first day so start from 'periodth' day
    for day in range(period, number_of_days, period):
                         
        # draw integers for each stock, 1 is buy, -1 is sell, 0 do nothing
        random_array = rng.integers(-1, 2, size = N)
      
        # decide which stocks to buy and sell
        stocks_to_buy = np.where(random_array == 1)[0]
        stocks_to_sell = np.where(random_array == -1)[0]
        
        
        # if there are stocks to buy, buy them
        if len(np.atleast_1d(stocks_to_buy)) > 0:
            for stock in stocks_to_buy:
                proc.buy(day, stock, amount, stock_prices, fees, portfolio, ledger)
        
        # if there are stocks to sell, sell them
        if len(np.atleast_1d(stocks_to_sell)) > 0:            
            for stock in stocks_to_sell:                
                # only sell if we have them
                if portfolio[stock] > 0:
                    proc.sell(day, stock, stock_prices, fees, portfolio, ledger)

    # if number is equal to 2 we do nothing and go to next period and sell our portfolio at the end        
    for stock_number in range(N):
        proc.sell(number_of_days - 1, stock_number, stock_prices, fees, portfolio, ledger)
    
    
def crossing_averages(stock_prices, amount = 5000, cool_down_period = 5, n = 200, m = 50, n_weights = [], m_weights = [], plot = False, fees = 20, ledger = 'crossing_average_ledger.txt'):
    '''
    Decide to buy shares when the m-day moving average crosses the n-day moving average from below, and decide to sell shares when the m-day moving average crosses the n-day mving average from above.
    Records transactions in ledger.
    
    Input:
        stock_prices (ndarray): the stock price data
        amount (float, default 5000): how much we spend on each purchase
            (must cover fees)
        cool_down_period (int, default = 5): how long to wait before making another trade (nb days after a trade is made)
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
    m_day_MA = np.zeros(stock_prices.shape)
    n_day_MA = np.zeros(stock_prices.shape)
    
    # initialize cool down matrix which indicates a cool down period
    buy_cool_down_matrix = np.zeros(stock_prices.shape)
    sell_cool_down_matrix = np.zeros(stock_prices.shape)
    
    # get n_day MA
    n_day_MA = ind.moving_average(stock_prices, n, n_weights) 

    # get m_day MA
    m_day_MA = ind.moving_average(stock_prices, m, m_weights) 
    
    # now loop through each day starting from day n + 1 (index n) and buy, sell as appropriate
    for day in range(n, total_days):
            
        # find stocks that cross from below and check that they are out of cool down period
        stocks_to_buy = np.where((m_day_MA[day - 1] < n_day_MA[day - 1]) & (m_day_MA[day] > n_day_MA[day]) & (buy_cool_down_matrix[(day - cool_down_period - 1)] != 1))[0]
        # if there are stocks to buy, buy them
        if np.any(stocks_to_buy):
            for stock in stocks_to_buy:
                proc.buy(day, stock, amount, stock_prices, fees, portfolio, ledger)

            # indicate not to buy during cool down period
            buy_cool_down_matrix[(day - cool_down_period) : day, stocks_to_buy] = 1

        # if it crosses from above, we sell
        # find stocks that cross from above and check that they are out of cool down period
        stocks_to_sell = np.where((m_day_MA[day - 1] > n_day_MA[day - 1]) & (m_day_MA[day] < n_day_MA[day]) & (sell_cool_down_matrix[(day - cool_down_period - 1)] != 1))[0]
        # if there are stocks to sell, buy them
        if np.any(stocks_to_sell):
            for stock in stocks_to_sell:
                proc.sell(day, stock, stock_prices, fees, portfolio, ledger)

            # indicate not to buy during cool down period
            sell_cool_down_matrix[(day - cool_down_period) : day, stocks_to_sell] = 1
    
    # sell portfolio at end
    for stock_number in range(N):
        proc.sell(total_days - 1, stock_number, stock_prices, fees, portfolio, ledger)
    
    # option to see plot
    if plot == True:
        for i in range(N):            
            plt.plot(stock_prices[:, i], label = f'Stock Price {i}')
            plt.plot(n_day_MA[:, i], label = f'Stock {i} {n}-day MA')
            plt.plot(m_day_MA[:, i], label = f'Stock {i} {m}-day MA')
        plt.legend()
        plt.xlabel('Time (days)')
        plt.ylabel('Price ($)')
        plt.title(f'{n}-day MA vs {m}-day MA')
        plt.grid()
        plt.show()
    
def momentum(stock_prices, osc_type = 'stochastic', lower = 0.25, upper = 0.75, n = 7, wait_time = 3, plot = False, smoothing_period = False, amount = 5000, fees = 20, ledger = 'momentum_ledger.txt'):
    '''
    Decide to sell shares in a portfolio when chosen oscillator is above upper threshold and buy when below lower threshold.
    Only buys/sells after wait_time (days) and only buys/sells once every time threshold is crossed.
    
    Input:
        stock_prices (ndarray): the stock price data
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.
        lower (float, default 0.25): lower threshold
        upper (float, default 0.75): upper threshold
        n (int, default 7): period of the oscillator (in days).
        wait_time (int, default 10): period (in days) to wait before buying/selling stock if price remains below/above threshold.               
        plot (boolean, default False): shows plot of oscillator if True.
        smoothing_period (int, default = False): period of moving average to be applied to the oscillator.
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
    oscillator= ind.oscillator(stock_prices, n, osc_type, smoothing_period)
    
    # get starting day of trading
    if smoothing_period != False and smoothing_period != 0:        
        day_1 = n + smoothing_period - 1
    
    else:
        day_1 = n - 1
    
    if wait_time > 0:
        # initialize indicator matrix which indicates we can buy after waiting time
        buy_indicator_matrix = np.zeros(oscillator.shape)
        sell_indicator_matrix = np.zeros(oscillator.shape)
        # now loop through each day to decide whether to buy or sell and implement the wait time
        for day in range(day_1, total_days):

           # check if oscillator is below lower threshold and this is first time we cross threshold
            stocks_to_buy_later = np.where((oscillator[day] < lower) & (oscillator[(day - 1)] >= lower))[0]
            # indicate to buy later
            buy_indicator_matrix[day, stocks_to_buy_later] = 1

            # check indicator matrix, if 1 and stock remained below threshold we buy
            stocks_to_buy_now = np.where((buy_indicator_matrix[(day - wait_time)] == 1) & (np.all(oscillator[(day - wait_time) : (day + 1)] < lower, axis = 0)))[0]
            # if there are stocks to buy, buy them
            if np.any(stocks_to_buy_now):
                for stock in stocks_to_buy_now:
                    proc.buy(day, stock, amount, stock_prices, fees, portfolio, ledger)

           # check if oscillator is above upper threshold and this is first time we cross threshold
            stocks_to_sell_later = np.where((oscillator[day] > upper) & (oscillator[(day - 1)] <= upper))[0]
            # indicate to sell later
            sell_indicator_matrix[day, stocks_to_sell_later] = 1

            # check indicator matrix, if 1 and stock remained below threshold we buy
            stocks_to_sell_now = np.where((sell_indicator_matrix[(day - wait_time)] == 1) & (np.all(oscillator[(day - wait_time) : (day + 1)] > upper, axis = 0)))[0]
            # if there are stocks to sell, sell them
            if np.any(stocks_to_sell_now) != 0:
                for stock in stocks_to_sell_now:
                    proc.sell(day, stock, stock_prices, fees, portfolio, ledger)          

    else:
        # now loop through each day to decide whether to buy or sell and implement the wait time
        for day in range(day_1, total_days):

           # check if oscillator is below lower threshold and this is first time we cross threshold
            stocks_to_buy_now = np.where((oscillator[day] < lower) & (oscillator[(day - 1)] >= lower ))[0]
           
            # if there are stocks to buy, buy them
            if np.any(stocks_to_buy_now):
                for stock in stocks_to_buy_now:
                    proc.buy(day, stock, amount, stock_prices, fees, portfolio, ledger)

           # check if oscillator is above upper threshold and this is first time we cross threshold
            stocks_to_sell_now = np.where((oscillator[day] > upper) & (oscillator[(day - 1)] <= upper))[0]
            
            # if there are stocks to sell, sell them
            if np.any(stocks_to_sell_now) != 0:
                for stock in stocks_to_sell_now:
                    proc.sell(day, stock, stock_prices, fees, portfolio, ledger)                              
    # sell portfolio at the end
    for stock_number in range(N):
        proc.sell(total_days - 1, stock_number, stock_prices, fees, portfolio, ledger)
    
    # option to plot oscillator with thresholds
    if plot == True:
        for i in range(N):
            plt.plot(oscillator[:, i], label = f'Stock {i}')
        plt.hlines(upper, n, total_days, colors = 'r', linestyles = '--', label = 'Upper')
        plt.hlines(lower, n, total_days, colors = 'r', linestyles = '--', label = 'Lower')
        plt.xlabel('Time (days)')
        plt.ylabel('Value')
        plt.legend()
        plt.title(f'{osc_type} Oscillator, Upper Threshold = {upper}, Lower Threshold = {lower}')
        plt.grid()
    