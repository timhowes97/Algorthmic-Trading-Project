# Corrections and clarifications

Last updated Friday 30th October 2020.

This is a list of different corrections, clarifications, and additional information for the project. I will email the class to notify whenever this file is updated.

## Docstring for `get_data()`

I seem to have forgotten to provide the docstring for the `get_data()` function -- my apologies! Here it is:

```python
def get_data(method='read', initial_price=None, volatility=None):
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
```

This function should be defined in `data.py`.

## Input arguments for `create_portfolio()`

You will need the path of the ledger file as an input argument for your function `create_portfolio()`. Here is the corrected docstring:

```python
def create_portfolio(available_amounts, stock_prices, fees, ledger_file):
    '''
    Create a portfolio by buying a given number of shares of each stock.
    
    Input:
        available_amounts (list): how much money we allocate to the initial
            purchase for each stock (this should cover fees)
        stock_prices (ndarray): the stock price data
        fees (float): transaction fees (fixed amount per transaction)
        ledger_file (str): path to the ledger file
    
    Output:
        portfolio (list): our initial portfolio

    Example:
        Spend 1000 for each stock (including 40 fees for each purchase):
        >>> N = sim_data.shape[1]
        >>> portfolio = create_portfolio([1000] * N, sim_data, 40, 'ledger.txt')
    '''
```

## Clarifications

### `NaN` values

Your functions need to handle `NaN` in the data appropriately (when a share price goes below zero, meaning that the company has failed). In particular, if this happens and you still have shares with the company, you need to decide what happens with your portfolio, and how your strategy function should handle it.

### Strategy functions

- Each of your strategy functions should perform the actual trading (buying, selling, logging) over the 5 years of data, using different indicators as specified in the questions. The exact way to use the indicators is for you to decide -- for example, you will need to choose:
    - the periods of the slow and fast moving averages,
    - whether there is a cool-off period after buying or selling,
    - whether you want to buy every day that an oscillator is below the low threshold, or just the first day it happens, or only if it's stayed below the threshold for a number of consecutive days (or some other criterion),
    - whether you want to do any smoothing to the oscillators (e.g. using your moving average function),
    - etc.

- The output (as specified in the docstring for `random()`) is `None` for these functions (as all output will be written in the ledger file).

- You are allowed to write smaller functions to handle sub-tasks required for your strategies, if you find it convenient.

### Calculating RSI

Sometimes, you may find that there have been no price decreases over the past n days, which means that the average negative price difference is 0. In that case, you won't be able to calculate RS explicitly, but you can **still** calculate RSI.

### Momentum trading with oscillators

The wording which explains how to use the threshold for the oscillators is ambiguous. Here are some clarifications:

- The price is considered overvalued when the oscillator is above a threshold <img src="https://render.githubusercontent.com/render/math?math=T_{\text{over}}">. Different people choose different values for <img src="https://render.githubusercontent.com/render/math?math=T_{\text{over}}">, but usually, the value is taken to be somewhere between 0.7 and 0.8. Values of 0.7, 0.75, or 0.8 are common.
- The price is considered undervalued when the oscillator is below a threshold <img src="https://render.githubusercontent.com/render/math?math=T_{\text{under}}">. Different people choose different values for <img src="https://render.githubusercontent.com/render/math?math=T_{\text{under}}">, but usually, the value is taken to be somewhere between 0.2 and 0.3. Values of 0.2, 0.25, or 0.3 are common.
- Typically, we have <img src="https://render.githubusercontent.com/render/math?math=T_{\text{over}} %2B T_{\text{under}} = 1">. This is to say that, for example, if you choose <img src="https://render.githubusercontent.com/render/math?math=T_{\text{over}} = 0.7">, then you would choose <img src="https://render.githubusercontent.com/render/math?math=T_{\text{under}} = 0.3">.
