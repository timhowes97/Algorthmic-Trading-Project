import numpy as np

def moving_average(stock_price, n = 7, weights = []):
    '''
    Calculates the n-day (possibly weighted) moving average for a given stock over time.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        weights (list, default []): must be of length n if specified. Indicates the weights
            to use for the weighted average. If empty, return a non-weighted average.

    Output:
        ma (ndarray): the n-day (possibly weighted) moving average of the share price over time.
    '''
    # get number of days of data
    number_of_days = len(stock_price)
    
    # convert weights to numpy array
    weights_array = np.array(weights)
    
    # initialize moving average array
    ma = np.zeros(number_of_days)
    # set first n-1 values for MA to NaN
    ma[:(n - 1)] = np.nan
    
    # condition for no weights
    if weights == []:
        for day in range(n - 1, number_of_days):
            
            # make sure none are NaN
            if (day - (n - 1)) > (n - 1) and np.any(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True) == False:
                ma[day] = np.mean(stock_price[(day - (n - 1)) : (day + 1)])
            
            # if any are NaN moving average becomes NaN
            elif (day - (n - 1)) > (n - 1) and np.any(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True) == True:
                index_where_nan = np.min(np.where(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True))
                ma[index_where_nan:] = np.nan
                break
            else:
                ma[day] = np.mean(stock_price[(day - (n - 1)) : (day + 1)])
                
    # condition for weights
    elif weights != []:
        for day in range(n - 1, number_of_days):
            
            # make sure none are NaN
            if np.any(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True) == False:
                ma[day] = np.dot(weights_array, stock_price[(day - (n - 1)) : (day + 1)])
                
            # if any are NaN moving average becomes NaN    
            else: 
                index_where_nan = np.min(np.where(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True))
                ma[index_where_nan:] = np.nan
                break    
           
    #return n-day ma
    return ma

def oscillator(stock_price, n = 7, osc_type = 'stochastic', smoothing_period = False):
    '''
    Calculates the level of the stochastic or RSI oscillator with a period of n days.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the oscillator (in days).
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.
        smoothing_period (int, default = False): period of moving average to be applied to the oscillator.

    Output:
        osc (ndarray): the oscillator level with period $n$ for the stock over time.
    '''
    # get number of days of data
    number_of_days = len(stock_price)
    
    # inititalize oscillator array
    osc = np.zeros(number_of_days)
    
    # set first n values to NaN
    osc[:(n - 1)] = np.nan
    
    if osc_type == 'stochastic':
        
        # loop over each day, cannot get n-day oscillator before n + 1 days
        for day in range(n - 1, number_of_days):
            
            # make sure no NaN values
            if np.any(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True) == False:
                
                # get the maximum and minimum prices over the last n days and get difference
                max_price = np.amax(stock_price[(day - (n - 1)) : (day + 1)])
                min_price = np.amin(stock_price[(day - (n - 1)) : (day + 1)])
                max_min_difference = max_price - min_price

                # calculate n-day stohastic oscillator and add to osc
                osc[day] = (stock_price[day] - min_price) / max_min_difference
                
            else:
                index_where_nan = np.min(np.where(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True))
                osc[index_where_nan:] = np.nan
                break 
                
            
                
            
    elif osc_type == 'RSI':
        
        # loop over each day
        for day in range(n - 1, number_of_days):
            
            # make sure no NaN values
            if np.any(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True) == False:
                
                # get differences of consecutive prices
                differences = stock_price[(day - (n - 2)) : (day + 1)] - stock_price[(day - (n - 1)) : day] 

                # separate positive and negative
                positive_differences = differences[differences > 0]
                negative_differences = differences[differences < 0]
            
                # manage the case where there is no negative differences
                if len(np.atleast_1d(negative_differences)) == 0:

                    # no negative differences means we set the RSI to 1
                    osc[day] = 1

                # manage the case where there is no positive differences
                elif len(np.atleast_1d(positive_differences)) == 0:

                    # no positive differences means we set RSI to 0
                    osc[day] = 0

                # otherwise we get RSI as normal
                else:
                    average_positive = np.mean(positive_differences)
                    # get absolute value
                    average_negative = np.abs(np.mean(negative_differences))
               

                    # get RS
                    RS = average_positive / average_negative

                    # get RSI and add to osc
                    osc[day] = 1 - (1 / (1 + RS))
                
            else:
                index_where_nan = np.min(np.where(np.isnan(stock_price[(day - (n - 1)) : (day + 1)]) == True))
                osc[index_where_nan:] = np.nan
                break 
                
    if smoothing_period != False and smoothing_period != 0:
        
        smoothed_oscillator = np.zeros(osc.shape)
        smoothed_oscillator[:(n - 1)] = np.nan
        
        # apply smoothing to the oscillator
        smoothed_oscillator[(n - 1):] = moving_average(osc[(n - 1):], n = smoothing_period)
        
        # return smoothed oscillator
        return smoothed_oscillator
                
    else:            
        # return normal oscillator
        return osc
            