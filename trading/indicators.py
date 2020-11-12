import numpy as np

def moving_average(stock_prices, n = 7, weights = []):
    '''
    Calculates the n-day (possibly weighted) moving average for a given stock over time.

    Input:
        stock_price (ndarray): share prices over time for several stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        weights (list, default []): must be of length n if specified. Indicates the weights
            to use for the weighted average. If empty, return a non-weighted average.

    Output:
        ma (ndarray): the n-day (possibly weighted) moving average of the share prices over time.
    '''

    # get number of days and number of stock
    number_of_days = stock_prices.shape[0]
    N = len(np.atleast_1d(stock_prices[0]))
            
    # convert weights to a numpy array
    weights_array = np.array(weights) 
            
    # initialize moving average array
    ma = np.zeros(stock_prices.shape)
    
    # set first n-1 values for MA to NaN since we cannot calculate these
    ma[:(n - 1)] = np.nan
    
    # condition for no weights
    if weights == []:
        # loop through each day starting from first day of available data for calculation
        for day in range(n - 1, number_of_days):
            
            # calculate averages for the last n-days for each stock
            ma[day] = np.mean(stock_prices[(day - (n - 1)) : (day + 1)], axis = 0)
                
    # condition for weights
    elif weights != []:
        # loop through each day starting from first day of available data for calculation
        for day in range(n - 1, number_of_days):
                
                # calculate weighted average using matrix multiplication
                ma[day] = np.sum(np.matmul(weights_array, stock_prices[(day - (n - 1)) : (day + 1)]), axis = 0)
           
    #return n-day ma
    return ma

def oscillator(stock_prices, n = 7, osc_type = 'stochastic', smoothing_period = False):
    '''
    Calculates the level of the stochastic or RSI oscillator with a period of n days.

    Input:
        stock_price (ndarray): share prices over time for several stock,
            up to the current day.
        n (int, default 7): period of the oscillator (in days).
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.
        smoothing_period (int, default = False): period of moving average to be applied to the oscillator.

    Output:
        osc (ndarray): the (possibly smoothed) oscillator level with period $n$ for the stocks over time.
    '''
   
    # get number of days and number of stocks
    number_of_days = stock_prices.shape[0]
    N = len(np.atleast_1d(stock_prices[0]))
    
    # inititalize oscillator array
    osc = np.zeros((number_of_days, N))
    
    # set first n values to NaN since we cannot caculate these
    osc[:(n - 1)] = np.nan
    
    # if the user chooses a stochastic oscillator
    if osc_type == 'stochastic':
        
        # loop over each day, cannot get n-day oscillator before n + 1 days
        for day in range(n - 1, number_of_days):
                
            # get the maximum and minimum prices over the last n days for each stock and get difference
            max_price = np.amax(stock_prices[(day - (n - 1)) : (day + 1)], axis = 0)
            min_price = np.amin(stock_prices[(day - (n - 1)) : (day + 1)], axis = 0)
            max_min_difference = max_price - min_price

            # calculate n-day stohastic oscillator and add to osc
            osc[day] = (stock_prices[day] - min_price) / max_min_difference
      
    # if the user chooses an RSI oscillator          
    elif osc_type == 'RSI':
        
        # loop over each day
        for day in range(n - 1, number_of_days):
                
            # get differences of consecutive prices
            differences = stock_prices[(day - (n - 2)) : (day + 1)] - stock_prices[(day - (n - 1)) : day] 
            # get the right shape to operate on the array
            differences = differences.reshape((n - 1, N))
            
            # separate positive and negative
            positive_differences = np.where(differences > 0, differences, np.nan)
            negative_differences = np.where(differences < 0, differences, np.nan)
            
            # set indicators which show if there is a stock with no negative differences or no positive differences
            x = 0
            y = 0
            
            # manage the case where there is no negative differences
            if np.any(np.all(np.isnan(negative_differences), axis = 0)):
                
                # get the stocks where there ar eno negative differences 
                stock_where_no_neg = np.where(np.all(np.isnan(negative_differences), axis = 0))[0]
                # set the column to 0
                negative_differences[:, stock_where_no_neg] = 0
                # indicate for later that such stock exists 
                x = 1
                
            # manage the case where there is no positive differences
            if np.any(np.all(np.isnan(positive_differences), axis = 0)):
                
                # get the stocks where there ar eno negative differences 
                stock_where_no_pos = np.where(np.all(np.isnan(positive_differences), axis = 0))[0]
                # set the column to 0
                positive_differences[:, stock_where_no_pos] = 0
                # indicate for later that such stock exists 
                y = 1
            
            # for the other stock we get RSI as normal
            if np.all(positive_differences == 0) == False and np.all(negative_differences == 0) == False:
                
                # calculate average of positive differences excluding NaNs
                average_positive = np.nanmean(positive_differences, axis = 0)
                
                # set average positive for stock with no positive differences to NaN, ensuring no division by 0
                if y == 1:
                    average_positive[stock_where_no_pos] = np.nan
                
                # get absolute value of mean of negative differences
                average_negative = np.abs(np.nanmean(negative_differences, axis = 0))
                
                # set average for stock with no negative differences to NaN, ensuring no division by 0
                if x ==1:                    
                    average_negative[stock_where_no_neg] = np.nan
                
                # get relative strength
                RS = average_positive / average_negative
                        
                # get RSI and add to osc
                osc[day] = 1 - (1 / (1 + RS))
            
            # no negative differences means we set the RSI for that stock to 1
            if x == 1:                
                osc[day, stock_where_no_neg] = 1
            
            # no positive differences means we set RSI to 0    
            if y == 1:                
                osc[day, stock_where_no_pos] = 0

    # if the user chose a smoothing period, apply it
    if smoothing_period != False and smoothing_period != 0:
        
        # initialize the smoothed oscillator
        smoothed_oscillator = np.zeros(osc.shape)
        # set first n - 1 values to NaN since we cannot calculate them
        smoothed_oscillator[:(n - 1)] = np.nan
        
        # apply smoothing to the oscillator using moving average function
        smoothed_oscillator[(n - 1):] = moving_average(osc[(n - 1):], n = smoothing_period)
        
        # return smoothed oscillator
        return smoothed_oscillator
    
    # if no smoothing applied, return normal oscillator
    else:            
        return osc
            