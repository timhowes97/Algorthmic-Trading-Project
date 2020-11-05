# import numpy
import numpy as np

# define the news function first
def news(probability, volatility):
    '''
    Creates array of float drift values of length n = len(volatility) arising from a random news events that affects n stock prices over a number of days drawn from a Uniform(3, 14) distribution. Takes 2 input arguments:
    1) probability - a float probability of news event happening, and
    2) volatility - an array or list of floats of length n representing volatilities of underlying stock prices
    '''
    
    # convert volatility to array
    volatility = np.array(volatility)
    
    # determine number of stocks
    n = len(np.atleast_1d(volatility))
    
    # set default random number generator
    rng = np.random.default_rng()
    
    # determine if news event occurs
    chance_of_news = rng.choice([1, 0], p = [probability, 1 - probability])
        
    # if there is news on the day, calculate the drift and it's duration
    if chance_of_news == 1:
            
        # m is N(0,2^2) variable
        m = rng.normal(0, 2)

        # determine duration of the effect of the news
        news_duration = rng.integers(3, 15)
        
        # initialize a zero matrix where the effect of news on each day for each stock will be stored
        drift_matrix = np.zeros((news_duration, n))
        
        # add the drift to the drift on those days it effects
        drift_matrix += m * volatility
        
    # if there is no news return 0    
    else:
        drift_matrix = np.zeros(1)
          
    # return the cumulative drift matrix
    return drift_matrix

# simulate data function
def generate_stock_price(days, initial_prices, volatility, news_probability = 0.01):
    '''
    Generates daily closing share prices for a given list of stock,
    for a given number of days. Takes 3 input arguments:
    1) days - integer representing number of days in the simulation
    2) initial_prices - a float array/list of inital share prices
    3) volatility - a float array/list of volatility values for the given stock 
    '''
    
    # change intial_price and volatility to numpy array
    initial_prices = np.array(initial_prices)
    volatility = np.array(volatility)
    
    # determine number of stock
    n = len(np.atleast_1d(initial_prices))
    
    # initialize matrix of zeros for share prices
    share_price_matrix = np.zeros((days, n))
    
    # set first row to be initial prices
    share_price_matrix[0] = initial_prices
    
    # check if any of the initial prices are 0 and set to nan if true
    if np.any(initial_prices == 0) or np.any(initial_prices == np.nan) == True:
        
        # find which share prices are already 0 or NaN
            idx_where_initial_zero = np.where(initial_prices == 0)
            share_price_matrix[:, idx_where_initial_zero] = np.nan
    
    # set default random number generator
    rng = np.random.default_rng()
    
    # get random walk increments for share prices
    increment_matrix = rng.normal(0, volatility, size = (days - 1, n))
    
    # loop over each day
    for day in range(1, days):
        
        # add the increments starting on day 1 (not day 0)
        share_price_matrix[day] = share_price_matrix[day - 1] + increment_matrix[day - 1]
        
        # get the effect of news for each day and get it's duration
        news_drift = news(news_probability, volatility)
        duration = news_drift.shape[0]
        
        # add the effect of this news to the price of the duration of the news effect
        # if day + duration exceeds the amount of days we truncate the duration
        if day + duration > days - 1:
            # add news drift to the remaining prices
            share_price_matrix[day:] += news_drift[0]
        
        # otherwise do as normal
        else:
            share_price_matrix[day : (day + duration)] += news_drift

        # if any share price reaches 0 or below then it is closed
        # check if any entries are 0
        if np.any(share_price_matrix[day] <= 0) or np.any(share_price_matrix == np.nan) == True:
            
            # find which share prices have hit 0 or are NaN
            index_where_zero = np.where(share_price_matrix[day, ] <= 0)
            
            # set the remaining values of those columns to nan
            share_price_matrix[day:, index_where_zero] = np.nan
    
    # return as a matrix of prices
    return share_price_matrix


def get_data(method = 'read', filename = 'stock_data_5y.txt', initial_prices = [], volatility = [], days = 5 * 365):
    '''
    Generates or reads simulation data for one or more stocks over 5 years,
    given their initial share price and volatility.
    
    Input:
        method (str): either 'generate' or 'read' (default 'read').
            If method is 'generate', use generate_stock_price() to generate
                the data from scratch.
            If method is 'read', use Numpy's loadtxt() to read the data
                from the file stock_data_5y.txt.
            
        initial_price (list): list of initial prices for each stock (default None)
            If method is 'generate', use these initial prices to generate the data.
            If method is 'read', choose the column in stock_data_5y.txt with the closest
                starting price to each value in the list, and display an appropriate message.
        
        volatility (list): list of volatilities for each stock (default None).
            If method is 'generate', use these volatilities to generate the data.
            If method is 'read', choose the column in stock_data_5y.txt with the closest
                volatility to each value in the list, and display an appropriate message.
        
        days (int): Number of days used if method is 'generate' (default 5 * 365)
        

        If no arguments are specified, read price data from the whole file.
        
    Output:
        sim_data (ndarray): NumPy array with N columns, containing the price data
            for the required N stocks each day over 5 years.
    
    Examples:
        Returns an array with 2 columns:
            >>> get_data(method='generate', initial_price=[150, 250], volatility=[1.8, 3.2])
            
        Displays a message and returns None:
            >>> get_data(method='generate', initial_price=[150, 200])
            Please specify the volatility for each stock.
            
        Displays a message and returns None:
            >>> get_data(method='generate', volatility=[3])
            Please specify the initial price for each stock.
        
        Returns an array with 2 columns and displays a message:
            >>> get_data(method='read', initial_price=[210, 58])
            Found data with initial prices [200, 50] and volatilities [1.5, 0.7].
        
        Returns an array with 1 column and displays a message:
            >>> get_data(volatility=[5.1])
            Found data with initial prices [850] and volatilities [5].
        
        If method is 'read' and both initial_price and volatility are specified,
        volatility will be ignored (a message is displayed to indicate this):
            >>> get_data(initial_price=[210, 58], volatility=[5, 7])
            Found data with initial prices [200, 50] and volatilities [1.5, 0.7].
            Input argument volatility ignored.
    
        No arguments specified, all default values, returns price data for all stocks in the file:
            >>> get_data()
     '''

    # if user chose method = 'read'
    if method == 'read':
        
        # remove first line of 'stock_data_5y.txt'
        if filename == 'stock_data_5y.txt':
            
            # use numpy loadtxt function to read in the txt/csv file and store in a numpy array
            text_data = np.loadtxt(filename)
            text_data = text_data[1:]
        
        else:
            text_data = np.loadtxt(filename)
        
        # loop through each day to find NaN's and closed business
        for day in range(text_data.shape[0]):
            
            #find any prices below zero or NaN
            if np.any(text_data[day] <= 0) or np.any(text_data[day] == np.nan) == True:

                # find which share prices have hit 0 or are NaN
                index_where_zero = np.where(text_data[day] <= 0)
                index_where_nan = np.where(text_data[day] == np.nan)
            
                # set the remaining values of those columns to nan
                text_data[day:, [index_where_zero, index_where_nan]] = np.nan
        
        # now find closest initial prices if this input is given
        if len(np.atleast_1d(initial_prices)) > 0:
           
            # number of stock to choose
            N = len(np.atleast_1d(initial_prices))
            
            # initialize data
            sim_data = np.zeros((text_data.shape[0], N))
            
            # loop through each initial price
            i = 0
            while i < N:
    
                # get column where initial price is closest to test price
                stock = (np.abs(text_data[0] - initial_prices[i])).argmin()
                
                # add this column to stock price data 
                sim_data[:, i] = text_data[:, stock]
                
                # now effectively remove this column from the data so that we don't choose it again
                text_data = np.delete(text_data, stock, 1)
                
                i += 1
          
            # find volatilities
            volatilities = [np.std(sim_data[:, i]) for i in range(N)]

            # display messages
            print(f'Found data with initial prices {initial_prices} and volatilities {volatilities}.')
            
            if len(np.atleast_1d(volatility)) > 0:
                print('Input argument volaility ignored.')
                
        
        
        # now find columns with closest volatility if this input is given
        elif len(np.atleast_1d(volatility)) > 0:
            
           # number of stock to choose
            N = len(np.atleast_1d(volatility)) 
           
           # loop through each volatility
            i = 0
            while i < N:
    
                # get column where initial price is closest to test price
                stock = (np.abs(np.std(text_data[:, ]) - volatility[i])).argmin()
                
                # add this column to stock price data 
                sim_data[:, i] = text_data[:, stock]
                
                # now effectively remove this column from the data so that we don't choose it again
                text_data = np.delete(text_data, stock, 1)
                
                i += 1
                
            # get initial prices and volatilities
            initial = [sim_data[0, i] for i in range(N)]
            volatilities = [np.std(sim_data[:, i]) for i in range(N)]
            
            # display messages
            print(f'Found data with initial prices {initial} and volatilities {volatilities}')
                  
        else:    
            # use numpy loadtxt function to read in the txt/csv file and store in a numpy array
            sim_data = text_data
                                           
    # if user chose method = 'generate'                       
    elif method == 'generate':
        
        # get number of stock to generate
        N = len(np.atleast_1d(initial_prices))
        
        # display error message if input is not correct
        if N == 0:
            print('Please specify the initial price for each stock')
        
        elif len(np.atleast_1d(volatility)) < N:
            print('Please specify the volatility for each stock')
        
        else:      
            # generate the stock data using generate_stock_price()
            sim_data = generate_stock_price(days, initial_prices, volatility)
    
    return sim_data
        
