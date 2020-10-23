def generate_stock_price(days, initial_price, volatility):
    '''
    Generates daily closing share prices for a company,
    for a given number of days.
    '''
    # Set stock_prices to be a zero array with length days
    stock_prices = np.zeros(days)
    # Set stock_prices in row 0 to be initial_price
    stock_prices[0] = initial_price
    # Set total_drift to be a zero array with length days
    totalDrift= np.zeros(days)
    # Set up the default_rng from Numpy
    rng = np.random.default_rng()
    # Loop over a range(1, days)
    for day in range(1, days):
        # Get the random normal increment
        inc = rng.normal()
        # Add stock_prices[day-1] to inc to get NewPriceToday
        NewPriceToday=stock_price[day-1]+inc
        # Make a function for the news
        def news(chance, volatility):
            '''
            Simulate the news with %chance
            '''
            # Choose whether there's news today
            news_today = rng.choice([0,1], p=chance)
            if news_today:
                # Calculate m and drift
                m=rng.normal(0,0.3)
                drift = m * volatility
                # Randomly choose the duration
                duration = rng.integers(7,7*12)
                final = np.zeros(duration)
                for i in range(duration):
                    final[i] = drift
                return final
            else:
                return np.zeros(duration)
        # Get the drift from the news
        d = news(1, volatility)
        # Get the duration
        duration = len(d)
        # Add the drift to the next days
        totalDrift[day:day+duration] =d
        # Add today's drift to today's price
        NewPriceToday+=totalDrift[day]
        # Set stock_prices[day] to NewPriceToday or to NaN if it's negative
        if NewPriceToday <=0:
            stock_prices[day] = np.nan
        else:
            stock_prices[day] = NewPriceToday
    return stock_prices
