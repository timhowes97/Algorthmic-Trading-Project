# Functions to process transactions.
import numpy as np

def log_transaction(transaction_type, date, stock, number_of_shares, price, fees, ledger_file):
    '''
    Record a transaction in the file ledger_file. If the file doesn't exist, create it.
    
    Input:
        transaction_type (str): 'buy' or 'sell'
        date (int): the date of the transaction (nb of days since day 0)
        stock (int): the stock we buy or sell (the column index in the data array)
        number_of_shares (int): the number of shares bought or sold
        price (float): the price of a share at the time of the transaction
        fees (float): transaction fees (fixed amount per transaction, independent of the number of shares)
        ledger_file (str): path to the ledger file
    
    Output: returns None.
        Writes one line in the ledger file to record a transaction with the input information.
        This should also include the total amount of money spent (negative) or earned (positive)
        in the transaction, including fees, at the end of the line.
        All amounts should be reported with 2 decimal digits.

    Example:
        Log a purchase of 10 shares for stock number 2, on day 5. Share price is 100, fees are 50.
        Writes the following line in 'ledger.txt':
        buy,5,2,10,100.00,-1050.00
            >>> log_transaction('buy', 5, 2, 10, 100, 50, 'ledger.txt')
    '''
    
    # log transaction if we buy
    if transaction_type == 'buy':
        
        # how much do we spend
        amount_spent = - (number_of_shares * price) - fees
        
        # first open the ledger_file, if it does not exist we create a new empty file
        # use 'a' as second argument as we wish to append to the file (creates and append if it doesn't exist)
        file = open(ledger_file, 'a')
    
        # now append the contents to the file
        file.write(f'{transaction_type}, {date}, {stock}, {number_of_shares}, {price}, {fees}, {amount_spent} \n')

        #close the file to any more changes
        file.close()
        
    # log transaction if we sell
    elif transaction_type == 'sell':
        
        # if we have 0 stocks to sell we do nothing
        if number_of_shares > 0:
            
            # how much do we earn
            amount_spent = number_of_shares * price - fees
            
            # first open the ledger_file, if it does not exist we create a new empty file
            # use 'a' as second argument as we wish to append to the file (create and append if it doesn't exist)
            file = open(ledger_file, 'a')

            # now append the contents to the file
            file.write(f'{transaction_type}, {date}, {stock}, {number_of_shares}, {price}, {fees}, {amount_spent} \n')

            #close the file to any more changes
            file.close()
    

def buy(date, stock, available_capital, stock_prices, fees, portfolio, ledger_file):
    '''
    Buy shares of a given stock, with a certain amount of money available.
    Updates portfolio in-place, logs transaction in ledger.
    
    Input:
        date (int): the date of the transaction (nb of days since day 0)
        stock (int): the stock we want to buy
        available_capital (float): the total (maximum) amount to spend,
            this must also cover fees
        stock_prices (ndarray): the stock price data
        fees (float): total transaction fees (fixed amount per transaction)
        portfolio (list): our current portfolio
        ledger_file (str): path to the ledger file
    
    Output: None

    Example:
        Spend at most 1000 to buy shares of stock 7 on day 21, with fees 30:
            >>> buy(21, 7, 1000, sim_data, 30, portfolio)
    '''
    
    # if the price is NaN we do not buy
    if np.isnan(stock_prices[date, stock]) == False:
        
        # see how many shares we can buy with available amount minus fees
        available_stock_to_buy = np.floor((available_capital - fees) / stock_prices[date, stock])

        # buy this amount and change in portfolio
        portfolio[stock] += available_stock_to_buy

        # log in the ledger
        log_transaction('buy', date, stock, available_stock_to_buy, stock_prices[date, stock], fees, ledger_file)
    
    # if price is NaN, set set our shares for this stock to 0 
    else:
        portfolio[stock] = 0
        
def sell(date, stock, stock_prices, fees, portfolio, ledger_file):
    '''
    Sell all shares of a given stock.
    Updates portfolio in-place, logs transaction in ledger.
    
    Input:
        date (int): the date of the transaction (nb of days since day 0)
        stock (int): the stock we want to sell
        stock_prices (ndarray): the stock price data
        fees (float): transaction fees (fixed amount per transaction)
        portfolio (list): our current portfolio
        ledger_file (str): path to the ledger file
    
    Output: None

    Example:
        To sell all our shares of stock 1 on day 8, with fees 20:
            >>> sell(8, 1, sim_data, 20, portfolio)
    '''
    # if stock price is NaN we have no stock to sell
    if np.isnan(stock_prices[date, stock]) == False:
        
        # first we log the transaction in the ledger
        log_transaction('sell', date, stock, portfolio[stock], stock_prices[date, stock], fees, ledger_file)

        # now we change the portfolio according to what stock we want to sell, selling all of this stock
        portfolio[stock] = 0
    
    # if price is NaN, set number of shares of this stock to 0
    else: 
        portfolio[stock] = 0
    

def create_portfolio(available_amounts, stock_prices, fees, ledger_file):
    '''
    Create a portfolio by buying a given number of shares of each stock.
    
    Input:
        available_amounts (list): how much money we allocate to the initial
            purchase for each stock (this should cover fees)
        stock_prices (ndarray): the stock price data
        fees (float): transaction fees (fixed amount per transaction)
    
    Output:
        portfolio (list): our initial portfolio

    Example:
        Spend 1000 for each stock (including 40 fees for each purchase):
        >>> N = sim_data.shape[1]
        >>> portfolio = create_portfolio([1000] * N, sim_data, 40)
    '''
    
    # convert available_amounts to array
    available_amounts = np.array(available_amounts)
    
    # how many stocks in our portfolio
    N = stock_prices.shape[1]
    
    # we create this portfolio on day 0
    start_date = 0
    
    # initialize portfolio
    portfolio = np.zeros(N)
    
    # loop through each stock to buy
    for stock in range(N):
        
        # buy stock using the buy function
        buy(start_date, stock, available_amounts[stock], stock_prices, fees, portfolio, ledger_file)
    
    # return the initial portfolio with integer values 
    return list(map(int, portfolio))
    
    

