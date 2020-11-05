import numpy as np
import re
import matplotlib.pyplot as plt
import pandas as pd

# Evaluate performance.

def read_ledger(ledger_file, profit_plot = True, strategy = 'Random Strategy', stock_of_choice = False):
    '''
    Reads and reports useful information from ledger_file.
    
    Input:
        ledger_file (str): path to the ledger file
        profit_plot (boolean, default True): plots profit/loss made over time if True.
        strategy (str, default 'Random Strategy'): to be displayed on tle of plot if profit_plot is True.
        stock_of_choice (int, default False): if set to an integer, information of this stock will be returned.
        
    Output:
        State of initial and final portfolio, information on portfolio and information of chosen stock.
    '''
    # first open the file into a readable mode
    file = open(ledger_file, 'r')
    
    # now read it into a list
    contents = file.read()
    contents = re.split('[,\n\s]\s*', contents)
    
    # count how many trades were done 
    no_of_trades = contents.count('buy') + contents.count('sell')
    
    i = 0
    # clean and format the list
    while i < len(contents):
        
        # if there are white spaces in the list remove them
        if contents[i] == '':
            contents.remove(contents[i])
        # stay on same index        
        
        else: 
            
        # change 'buy' to 1 and 'sell' to -1
            if contents[i] == 'buy':
                contents[i] = 1
            elif contents[i] == 'sell':
                contents[i] = -1
            
            # move to next index
            i += 1
    
    # now turn the new list into an array
    ledger_data = np.array(contents, dtype = float).reshape(no_of_trades, 7)
    
    
    
    # we can now use this array to find the relevant information
                          
    # calculate how much money was spent and earned
    # use np.where to find which indices have ledger_data < 0 and > 0
    total_amount_spent = np.abs(np.sum(ledger_data[ledger_data[:, 6] < 0, 6]))
    total_amount_earned = np.sum(ledger_data[(ledger_data[:, 6] > 0), 6])
    
    # total profit/loss = amount earned - amount spent
    total_profit_loss = total_amount_earned - total_amount_spent
            
    # get state of portfolio before last day
    # do this by getting the state of the portfolio on each trading day
    # get initial portfolio
    trading_days = np.unique(ledger_data[:, 1])
    no_of_trading_days = len(trading_days)
    no_of_stock = np.count_nonzero(ledger_data[:, 1] == 0)
    portfolio = np.zeros((no_of_trading_days, no_of_stock))
    portfolio[0] = np.array(ledger_data[ledger_data[:, 1] == 0, 3])
    
    # rows where stocks were bought and sold
    bought_rows = ledger_data[ledger_data[:, 0] == 1]
    sold_rows = ledger_data[ledger_data[:, 0] == -1]
    
    i = 1
    
    # now loop over each trading day to update portfolio
    for day in trading_days[1:]:
        
        # get rows where stocks were bought and sold on the day
        bought_on_day_rows = bought_rows[bought_rows[:, 1] == day]
        sold_on_day_rows = sold_rows[sold_rows[:, 1] == day]       
        
        # get which stocks were bought and sold on the day
        if len(bought_on_day_rows) > 0 and len(sold_on_day_rows) > 0:
            stocks_bought_on_day = np.array(bought_on_day_rows[:, 2], dtype = int)
            stocks_sold_on_day = np.array(sold_on_day_rows[:, 2], dtype = int)
            
            #update portfolio
            portfolio[i, stocks_bought_on_day] = portfolio[i - 1, stocks_bought_on_day] + bought_on_day_rows[:, 3]           
            portfolio[i, stocks_sold_on_day] = portfolio[i - 1, stocks_sold_on_day] - sold_on_day_rows[:, 3] 
            
        elif len(bought_on_day_rows) > 0:
            stocks_bought_on_day = np.array(bought_on_day_rows[:, 2], dtype = int)
            
            #update portfolio
            portfolio[i] = portfolio[i - 1]
            portfolio[i, stocks_bought_on_day] += bought_on_day_rows[:, 3]  
             
        elif len(sold_on_day_rows) > 0:
            stocks_sold_on_day = np.array(sold_on_day_rows[:, 2], dtype = int)
            
            #update portfolio
            portfolio[i] = portfolio[i - 1]
            portfolio[i, stocks_sold_on_day] += - sold_on_day_rows[:, 3]  
        
        else:
            portfolio[i] = portfolio[i - 1]
            
        i = int(i + 1)

       
    # put initial final state of portfolio in table
    initial_portfolio = pd.DataFrame(map(int,portfolio[0]), columns = ['No. of Shares (Initial Portfolio)']).transpose()
    final_portfolio = pd.DataFrame(map(int, portfolio[-2]), columns = ['No. of Shares (Final Portfolio before selling)']).transpose()
    
    
    # now calculate profit over time
    profits = np.zeros(no_of_trading_days + 1)
    profits[0], profits[1] = 0, ledger_data[0, 6]
    profit_idx = 2
    
    for row in range(2, no_of_trades + 1):
               
        if ledger_data[row - 1, 1] == ledger_data[row - 2, 1]:
            profits[profit_idx - 1] += ledger_data[row - 1, 6]
        
        else:
            profits[profit_idx] = profits[profit_idx - 1] + ledger_data[row - 1, 6]
            profit_idx += 1
    
    
    
    # option to plot profits
    if profit_plot == True:
        plt.plot(np.append(-1, trading_days), profits)
        plt.hlines(0, -1, trading_days[-1], linestyle = '--', colors = 'r')
        plt.title(f'Profit/Loss Over Time using {strategy}, Total Profit/Loss = ${round(total_profit_loss, 2)}')
        plt.xlabel('Time (days)')
        plt.ylabel('Profit/Loss (+/-)')
        plt.show()
    
    # put information in a table
    information = pd.DataFrame(np.array([no_of_trading_days - 1, total_amount_spent, total_amount_earned, total_profit_loss]), index = ['No. of Trades (after portfolio creation)', 'Total Amount Spent ($)', 'Total Amount Earned ($)', 'Total Profit/Loss (+/-)'], columns = [''])  
    
    
    
    # get information on stock of choice
    if stock_of_choice != False and len(np.atleast_1d(stock_of_choice)) > 0:
        
        # get dates on which stock was bought and sold
        bought_dates = np.unique(bought_rows[np.where(bought_rows[:, 2] == stock_of_choice), 1])
        sold_dates = np.unique(sold_rows[np.where(sold_rows[:, 2] == stock_of_choice), 1])
                
        # get how much we earned from this stock
        earned_from_stock = np.sum(ledger_data[np.where(ledger_data[:, 2] == stock_of_choice), 6])
        
        return initial_portfolio, final_portfolio, information, list(map(int, bought_dates)), list(map(int, sold_dates)), earned_from_stock
    
    else:
        return initial_portfolio, final_portfolio, information, 
        
    
            
            
            
      
        
    
        