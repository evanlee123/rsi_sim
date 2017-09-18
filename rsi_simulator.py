import datetime as dt
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import csv
import sys


style.use('ggplot')

def read_data(some_file):
    price = pd.read_csv(some_file, parse_dates = True, index_col =0)
    return price

def plot_intersect(x_list, y_list, inter_list, axis, color):
    for item in inter_list:
        axis.plot(x_list[item],y_list[item],color, linewidth = 0.6)
    
def main(stock_data, rsi_data, buy_rsi, sell_rsi,  *args, **kwargs):
    #start_date and end_date should be in YYYY-MM-DD format
    start_date = kwargs.get('start', None)
    stop_date = kwargs.get('stop', None)
    buy_amt = kwargs.get('amt', 1)
    #first buy either on a up or down trend
    buy_on_down = kwargs.get('first_down', False)
    buy_on_up = kwargs.get('first_up', False)
    #buy/sell at a up or down trend
    buy_always_up = kwargs.get('buy_always_up', False)
    buy_always_down = kwargs.get('buy_always_down', False)
    sell_always_up = kwargs.get('sell_always_up', False)
    sell_always_down = kwargs.get('sell_always_down', False)
    show_trans = kwargs.get('show_trans', False)
    #buys and sell at next day's Adj. open prices
    buy_open = kwargs.get('buy_open', False)
    sell_open = kwargs.get('sell_open', False)
    #writes to a csv file in a directory at write_trans 
    write_trans = kwargs.get('write_trans', None)
    #adds the option for an additional buy/sell line
    sell_option = kwargs.get('sell_opt', None)
    buy_option = kwargs.get('buy_opt', None)
    #Boolean of whether to sell at current price IF RSI has not hit the sell line
    sell_at_end = kwargs.get('sell_now', False)
    #show graph
    show_graph = kwargs.get('show_graph', True)
    #show profit
    show_profit = kwargs.get('show_profit', True)
    #return profit
    return_profit = kwargs.get('return_profit', False)

    
    #gather data
    prices = []
    rsi = []
    try:
        prices = read_data(stock_data)
        rsi = read_data(rsi_data)
    except FileNotFoundError:
        print('file not found')
        sys.exit()
    if buy_open == True or sell_open == True:
        try:
            prices['Adj Open'] = prices['Open'] * prices['Adj Close'] / prices['Close']
        except TypeError:
            print('Error with Calculating Adj Open')
            sys.exit()
    #sets range
    beg_date =dt.date(1,1,1)
    end_date = dt.date(1,1,2)
    try:
        if start_date != None and stop_date != None:
            beg_date =  dt.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = dt.datetime.strptime(stop_date, '%Y-%m-%d')
        elif ((start_date != None and stop_date == None) or
              (start_date == None and stop_date != None)):
            if start_date == None:
                beg_date = rsi.index[0]
                end_date = dt.datetime.strptime(stop_date, '%Y-%m-%d')

            else:
                beg_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = rsi.index[-1]   
        elif start_date == None and stop_date == None:
            beg_date = rsi.index[0]
            end_date = rsi.index[-1]
    except IndexError:
        print('One of the files is not filled')
        sys.exit()
    
    while prices.index[0] < beg_date:
        prices.drop(prices.index[0], inplace = True)
    while rsi.index[0] < beg_date:
        rsi.drop(rsi.index[0], inplace = True)
    while prices.index[-1] > end_date:
        prices.drop(prices.index[-1], inplace = True)
    while rsi.index[-1] > end_date:
        rsi.drop(rsi.index[-1], inplace = True)

    
    #sets graph size
    ax1 = plt.subplot2grid((6,1),(0,0),rowspan=5, colspan =1)
    ax2 = plt.subplot2grid((6,1),(5,0),rowspan=1, colspan =1, sharex = ax1)

    #removes offset of dates
    while prices.index[0] < rsi.index[0]:
        prices.drop(prices.index[0], inplace = True)         

    #graphs data
    try:
        buy_line = [buy_rsi for date in rsi.index]
        sell_line = [sell_rsi for date in rsi.index]
        if buy_open == True or sell_open == True:
            ax1.plot(prices.index, prices['Adj Open'], 'blue', linewidth = 0.75)
        if (buy_open == False or sell_open == False):
            ax1.plot(prices.index, prices['Adj Close'], 'black', linewidth = 0.75)
        ax2.plot(rsi.index,rsi['RSI'], 'black', linewidth = 0.75)
        ax2.plot(rsi.index,buy_line,'g',
                 rsi.index,sell_line,'r')
    except ValueError:
        print('Data Error')
        sys.exit()

    #calculates intersects
    buy_inter0 = np.argwhere(np.diff(np.sign(buy_line - rsi['RSI'])) != 0).reshape(-1) + 0
    sell_inter0 = np.argwhere(np.diff(np.sign(sell_line - rsi['RSI'])) != 0).reshape(-1) + 0

    buy_line1 = []
    sell_line1 = []
    buy_rsi1 = buy_option
    sell_rsi1 = sell_option
    sell_inter1 = 'dummy'
    buy_inter1 = 'dummy'
    if buy_option != None:
        buy_line1 = [buy_option for date in rsi.index]
        ax2.plot(rsi.index,buy_line1, 'g')
        buy_inter1 = np.argwhere(np.diff(np.sign(buy_line1 - rsi['RSI'])) != 0).reshape(-1) + 0
        buy_inter = np.append(buy_inter0, buy_inter1 )
        buy_inter.sort()
    else:
        buy_inter = buy_inter0
    if sell_option != None:
        sell_line1 = [sell_option for date in rsi.index]
        ax2.plot(rsi.index, sell_line1, 'r')
        sell_inter1 = np.argwhere(np.diff(np.sign(sell_line1 - rsi['RSI'])) != 0).reshape(-1) + 0
        sell_inter = np.append(sell_inter0, sell_inter1)
        sell_inter.sort()
    else:
        sell_inter = sell_inter0
    
    #money simulator
    if len(buy_inter) == 0 or len(sell_inter) == 0:
        sys.exit()
    have_money = False
    new_buy = [buy_inter[0]]
    new_sell = []
    curr_index = new_buy[0]
    if buy_on_up == True:
        for item in buy_inter:
            if ((rsi['RSI'][item - 1] < buy_rsi and item in buy_inter0)
                or (buy_rsi1 != None and rsi['RSI'][item-1] < buy_rsi1 and item in buy_inter1)
                or (rsi['RSI'][item ] <= buy_rsi and rsi['RSI'][item+1] >= buy_rsi and item in buy_inter0)
                or (buy_rsi1 != None and rsi['RSI'][item ] <= buy_rsi1 and rsi['RSI'][item+1] >= buy_rsi1 and item in buy_inter1)):
                new_buy = [item]
                curr_index = item
                break
    elif buy_on_down == True:
        for item in buy_inter:
            if ((rsi['RSI'][item - 1] > buy_rsi and item in buy_inter0)
                or (sell_rsi1 != None and rsi['RSI'][item-1] > buy_rsi1 and item in buy_inter1)
                or (rsi['RSI'][item ] >= buy_rsi and rsi['RSI'][item+1] <= buy_rsi and item in buy_inter0)
                or (buy_rsi1 != None and rsi['RSI'][item ] >= buy_rsi1 and rsi['RSI'][item+1] <= buy_rsi1 and item in buy_inter1)):
                new_buy = [item]
                curr_index = item
                break

    
        
    while curr_index <= len(rsi.index) and curr_index <= buy_inter[-1] and curr_index <= sell_inter[-1]:
        has_changed = False
        if have_money == True:
            for item in buy_inter:
                if item > curr_index:
                    if buy_always_up == True:
                        if ((rsi['RSI'][item - 1] <= buy_rsi and item in buy_inter0)
                            or (buy_rsi1 != None and rsi['RSI'][item-1] <= buy_rsi1 and item in buy_inter1)
                            or (rsi['RSI'][item ] <= buy_rsi and rsi['RSI'][item+1] >= buy_rsi and item in buy_inter0)
                            or (buy_rsi1 != None and rsi['RSI'][item ] <= buy_rsi1 and rsi['RSI'][item+1] >= buy_rsi1 and item in buy_inter1)):  
                            new_buy.append(item)
                            curr_index = item
                            have_money = False
                            has_changed = True
                            break
                    elif buy_always_down == True:
                        if ((rsi['RSI'][item - 1] >= buy_rsi and item in buy_inter0)
                            or (buy_rsi1 != None and rsi['RSI'][item-1] >= buy_rsi1 and item in buy_inter1)
                            or (rsi['RSI'][item ] >= buy_rsi and rsi['RSI'][item+1] <= buy_rsi and item in buy_inter0)
                            or (buy_rsi1 != None and rsi['RSI'][item ] >= buy_rsi1 and rsi['RSI'][item+1] <= buy_rsi1 and item in buy_inter1)):
                            new_buy.append(item)
                            curr_index = item
                            have_money = False
                            has_changed = True
                            break
                    else:
                        new_buy.append(item)
                        curr_index = item
                        have_money = False
                        has_changed = True
                        break
        elif have_money == False:
            for item in sell_inter:
                if item > curr_index:
                    if sell_always_up == True:
                        if ((rsi['RSI'][item - 1] <= sell_rsi and item in sell_inter0)
                            or (sell_rsi1 != None and rsi['RSI'][item-1] <= sell_rsi1 and item in sell_inter1)
                            or (rsi['RSI'][item ] <= sell_rsi and rsi['RSI'][item+1] >= sell_rsi and item in sell_inter0)
                            or (sell_rsi1 != None and rsi['RSI'][item ] <= sell_rsi1 and rsi['RSI'][item+1] >= sell_rsi1 and item in sell_inter1)):
                            new_sell.append(item)
                            curr_index = item
                            have_money = True
                            has_changed = True
                            break
                    elif sell_always_down == True:
                        if ((rsi['RSI'][item - 1] >= sell_rsi and item in sell_inter0)
                            or (sell_rsi1 != None and rsi['RSI'][item-1] >= sell_rsi1 and item in sell_inter1)
                            or (rsi['RSI'][item ] >= sell_rsi and rsi['RSI'][item+1] <= sell_rsi and item in sell_inter0)
                            or (sell_rsi1 != None and rsi['RSI'][item ] >= sell_rsi1 and rsi['RSI'][item+1] <= sell_rsi1 and item in sell_inter1)):
                            new_sell.append(item)
                            curr_index = item
                            have_money = True
                            has_changed = True
                            break
                    else:
                        new_sell.append(item)
                        curr_index = item
                        has_changed = True
                        have_money = True
                        break
        if has_changed == False:
            break

    #Option as to sell at end or remove last buy
    if len(new_buy) > len(new_sell):
        if sell_at_end == True:
            new_sell.append(len(rsi.index)-1)
        else:
            new_buy.remove(new_buy[-1])    
    if buy_open == True:
        for item in range(len(new_buy)):
            new_buy[item] = new_buy[item] +1
    if sell_open == True:
        for item in range(len(new_sell)):
            new_sell[item] = new_sell[item] +1
    #at this point len(new_buy) = len(new_sell)
    #Profit calculator
    trans = []
    profit = 0
    trans_length = dt.timedelta(0)
    for number in range(len(new_buy)):
        bought = buy_amt * prices['Adj Close'][new_buy[number]]
        sell = buy_amt * prices['Adj Close'][new_sell[number]]
        if buy_open == True:
            bought = buy_amt * prices['Adj Open'][new_buy[number]]
        if sell_open == True:
            sell = buy_amt * prices['Adj Open'][new_sell[number]]
        time = rsi.index[new_sell[number]] - rsi.index[new_buy[number]]
        trans_length += time
        change = 0
        try:
            change = sell - bought
        except TypeError:
            print('data is not number')
            sys.exit()
        profit += change
        gain = (sell-bought)/bought * 100
        if show_trans == True:
            print('Bought:', bought, 'Sell:', sell , 'Change:', change, 'Gain%:', gain)
            print('Bought date:', rsi.index[new_buy[number]].strftime('%y-%m-%d'),
                  'Sell date:', rsi.index[new_sell[number]].strftime('%y-%m-%d'),
                  'Days spent:', time.days)
            print()
            
        if write_trans != None:
            trans.append([ bought,rsi.index[new_buy[number]].strftime('%y-%m-%d'),
                           sell , rsi.index[new_sell[number]].strftime('%y-%m-%d'),
                           change, gain, time.days, gain/time.days])
    if write_trans != None:
        string = write_trans + '.csv'
        with open(string, 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            fieldnames = ['Bought', 'Bought date','Sell','Sell date','Change','Gain%','Days spent', 'Gain%/day']
            writer.writerow(fieldnames)
            for line in trans:
                writer.writerow(line)
            writer.writerow(['Profit:', profit, 'Number of Transactions:', len(new_buy),
                             'Avg gain', profit/len(new_buy), 'Avg time for transaction:', trans_length.days/len(new_buy)])
        csvfile.close()
    if show_profit == True:
        print('Profit:', profit, 'Number of Transactions:', len(new_buy), 'Avg gain', profit/len(new_buy), 'Avg time for transaction:', trans_length.days/len(new_buy)) 
    #time_elapsed = rsi.index[-1] - rsi.index[0]
    #print(time_elapsed)
    #profit_year = profit/(time_elapsed.days/365)
    #profit_perc = profit_year/(prices['Adj Close'][0] * buy_amt) * 100
    #print('Rate of return%:', profit_perc)    
    new_buy1 = []
    new_sell1 = []
    if buy_option != None:
        for item in new_buy:
            if (item - 1) in buy_inter1:
                new_buy1.append(item)
        plot_intersect(rsi.index,buy_line1, new_buy1, ax2, 'go')
        if buy_open == True:
            plot_intersect(rsi.index, prices['Adj Open'],new_buy1, ax1, 'gd')
        else:
            plot_intersect(rsi.index,prices['Adj Close'], new_buy1, ax1, 'gd')
        
        for item in new_buy1:
                new_buy.remove(item)
    
    if sell_option != None:
        for item in new_sell:
            if (item - 1) in sell_inter1:
                new_sell1.append(item)
                
        plot_intersect(rsi.index,sell_line1, new_sell1, ax2, 'ro')
        if sell_open == True:
            plot_intersect(rsi.index, prices['Adj Open'],new_sell1, ax1, 'rd')
        else:
            plot_intersect(rsi.index,prices['Adj Close'], new_sell1, ax1, 'rd')
        for item in new_sell1:
                new_sell.remove(item)

    
    
    # ALL BUY SELL POINTS
    #plot_intersect(rsi.index,buy_line, buy_inter, ax2, 'go')
    #plot_intersect(rsi.index,sell_line, sell_inter, ax2, 'bo')
    #plot_intersect(rsi.index,prices['Adj Close'], buy_inter, ax1, 'go')
    #plot_intersect(rsi.index,prices['Adj Close'], sell_inter, ax1, 'bo')
    if len(new_buy) == 0:
        sys.exit()
        

    #New_buy and New_sell points
    if show_graph == True:
        plot_intersect(rsi.index,buy_line, new_buy, ax2, 'go')
        plot_intersect(rsi.index,sell_line, new_sell, ax2, 'ro')
        if buy_open == True:
            plot_intersect(rsi.index,prices['Adj Open'], new_buy, ax1, 'gd')
        else:
            plot_intersect(rsi.index,prices['Adj Close'], new_buy, ax1, 'gd')
        if sell_open == True:
            plot_intersect(rsi.index,prices['Adj Open'], new_sell, ax1, 'rd')
        else:
            plot_intersect(rsi.index,prices['Adj Close'], new_sell, ax1, 'rd')
    ##ax2.plot(rsi.index[item for item in list1], buy_line[item for item in list1], 'ro')
    #ax2.plot(rsi.index[buy_inter], buy_line[buy_inter], 'ro')
    #ax2.plot(rsi.index[sell_inter], sell_line[sell_inter], 'ro')
    if show_graph == True:
        plt.show()
    if return_profit == True:
        #print(profit, 'RSI')
        list1 = [profit, len(new_buy), profit/len(new_buy), trans_length.days/len(new_buy)]
        return list1
