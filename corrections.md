# Corrections and clarifications

Last updated Mon 2/11/2020.

This is a list of different corrections, clarifications, and additional information for the project. I will email the class to notify whenever this file is updated.

### Updates

- Fri 30/10/2020: Created the file
- Mon 2/11/2020:
    - Added general marking criteria and expectations in `marking.md`
    - Added corrections to the docstring examples of `get_data()`, where the volatility and initial values didn't match the data file.
    - Added clarifications on computing and testing the indicators
    - Added clarification and an example of a moving average

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
            Found data with initial prices [210, 100] and volatilities [1.2, 3.4].
        
        Returns an array with 1 column and displays a message:
            >>> get_data(volatility=[5.1])
            Found data with initial prices [380] and volatilities [5.2].
        
        If method is 'read' and both initial_price and volatility are specified,
        volatility will be ignored (a message is displayed to indicate this):
            >>> get_data(initial_price=[210, 58], volatility=[5, 7])
            Found data with initial prices [210, 100] and volatilities [1.2, 3.4].
            Input argument volatility ignored.
    
        No arguments specified, all default values, returns price data for all stocks in the file:
            >>> get_data()
    '''
```

This function should be defined in `data.py`.

**Note** the corrected example values (updated 2/11/2020).

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
    - how you handle days when you can't compute indicators (typically the first `n-1` days in the data, for an indicator with period `n`),
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

### Periods for indicators

Whenever an `n`-day period is indicated for the computation of an oscillator or a moving average, the `n` days should include today. You will need to **decide** what to do for the first `n-1` days in your data (and explain/justify that decision), when you don't have enough data yet to compute the indicator.

### Moving average example

A moving average with period `n` is basically just an average taken over a sliding window spanning the n days up to the current day. The value is different every day, since you update the previous average using today's data.

For example, if you have some data `[2, 4, 3, 3, 5, 1, 5, 4]` taken over 8 days, then today's value of the 3-day moving average is `(1+5+4)/3`, yesterday's value was `(5+1+5)/3`, the day before it was `(3+5+1)/3`, etc.

In practice, what this does is it *smoothes* your data, since any sudden changes from one day to another are lumped together with the average of the previous days.

The weighted moving average is the same idea, but you can give different weights to different days in the window (you then calculate the weighted average over that window, instead of the mean).

You also have to decide what to do, for example here, about the first 2 days -- the 3-day moving average won't be defined since you don't have enough data yet. Take a step back from the problem, and consider what's a sensible thing to do about this. (How to handle this wasn't explicitly specified in the task, so there are not really any right or wrong answers here -- as long as you clearly explain your reasoning for how you made that decision in the end.)

## General expectations for your indicator and strategy functions

It seems to be worth clarifying that the project is not a Coderunner quiz -- it will be assessed by human markers, who can understand nuances in implementation and design decisions a lot better than an automatic test! And to some extent, particularly for the last parts of Task 2, your ability to make **reasoned** design and implementation decisions is part of the assessment, as well as your ability to reflect on your code and results. So please don't worry too much about trying to match some exact expected output -- instead, take a step back when you test your functions and think critically about your results. Ask yourself if they make sense, try some simple/trivial inputs if something doesn't seem to work as expected.

The fairly strict specification of the utility functions was given not necessarily to be overly prescriptive, but to make sure that everyone was given enough detailed instructions to have a trading process running as a well-defined "standardised" procedure, and to avoid students getting stuck on figuring out exactly how to implement the process of e.g. "buying shares" in the first parts of the task, which would have completely prevented them from even attempting the simulation and analysis of the results.

I won't provide some expected output signals for the indicators -- you should spend time thinking critically about your results, not tweaking your code to make some numbers match exactly. For instance, here are some ideas to test your indicator functions:

- What should the `n`-day moving average look like for constant data? for periodic data with period `n`?
- What should it look like for `n = 1`?
- For the weighted moving average, what should it look like where all the weights are 0 except one?
- For some test stock price data, what should the moving average look like, qualitatively speaking, when you plot it next to the data? What should moving averages with different periods look like, relatively to each other?
- The oscillator values should be between 0 and 1. Looking at the formulas, qualitatively/intuitively, what do they each measure?
- In what situations should their value be close to 1? close to 0?
- What should the value be if the price is constantly increasing or decreasing? 
- What should the value be if today's price is the highest of the past `n` days? the lowest?

This doesn't mean that you should do all these tests or include them in your hand-in -- these are just some ideas you could try, to check if your code works as you intend it to.
