import rsi_simulator as sim
import csv
import time
import pandas as pd
import ast



def main(symbol_list,directory, *args, **kwargs):
    try_all_rsi = kwargs.get('try_all_rsi', False)
    max_profit = kwargs.get('max_profit', False)
    beg = kwargs.get('beg', 20)
    end = kwargs.get('end', 20)
    kwargs['show_profit'] = False
    kwargs['show_graph'] = False
    kwargs['return_profit'] = True
    if directory[-1] == '/':
        directory = directory[:-1]
    print(kwargs)
    macro(symbol_list, directory, *args, **kwargs)
    

def macro(symbol_list, directory, *args, **kwargs):
    print(args)
    print(kwargs)
    try_all_rsi = kwargs.get('try_all_rsi', False)
    max_profit = kwargs.get('max_profit', False)
    save_prog = kwargs.get('save_prog',False)
    load_prog = kwargs.get('load_prog', False)
    beg = kwargs.get('beg', 20)
    end = kwargs.get('end', 40)
    #parameters is a list
    file = open(symbol_list)
    #stuff for progress
    progress = []
    first_file = True
    first_buy = True
    first_sell = True
    value = []
    for item in file:
        if load_prog == True:
            if first_file == True:
                load = pd.read_csv(directory + '/progress.csv')
                value = list(load.columns.values)
                if str(value[0]) != str(item):
                    print(item)
                    print(value[0])
                    print('AA')
                    continue
                if str(value[0]) == str(item):
                    first_file = False                     
        if item.strip() != 'Symbol':
            string = directory + '/' + item.strip() + '-profit.csv'
            if load_prog == False or first_file == False:
                with open(string, 'w', newline = '') as csvfile:
                    writer = csv.writer(csvfile)
                    fieldnames = ['Profit', 'Number of Transactions', 'Avg gain',
                                  'Avg time for transaction', 'buy rsi', 'sell rsi']
                    writer.writerow(fieldnames)
                    csvfile.close()           
            buy_rsi = 0
            sell_rsi= 0
            price_file = directory + '/' + item.strip() + '.csv'
            rsi_file = price_file[:price_file.index('.')] + '-RSI.csv'
            print(price_file)
            print(rsi_file)
            profit = []
            if load_prog == True:
                profit = ast.literal_eval(value[3])
            if try_all_rsi == True:
                print('AAAA')
                for number in range(beg,end):
                    if load_prog== True and first_buy == True:
                        if str(number) != str(value[1]):
                            continue
                        if str(number) == str(value[1]):
                            first_buy = False
                    start_time = time.time()
                    #if number % 10 == 0:
                    
                    buy_rsi = number
                    for integer in range(beg,end):
                        
                        if load_prog == True and first_sell == True:
                            if str(integer) != str(value[2]):
                                continue
                            first_sell = False
                            print(value)
                        sell_rsi = integer
                        try:
                            temp = call_sim(price_file, rsi_file, buy_rsi, sell_rsi, **kwargs)
                            temp += [buy_rsi,sell_rsi]
                            #print(temp)
                            fd = open(string, 'a', newline = '')
                            writer = csv.writer(fd)
                            writer.writerow(temp)
                            fd.close()
                            if save_prog == True:
                                if sell_rsi == end - 1:
                                    progress = [item, buy_rsi +1, beg, profit]
                                else:
                                    progress = [item, buy_rsi, sell_rsi+1, profit]
                                path = directory + '/progress.csv'
                                fd = open(path, 'w', newline = '')
                                writer = csv.writer(fd)
                                writer.writerow(progress)
                                fd.close()
                            if profit == []:
                                profit = temp
                            elif float(profit[0]) < float(temp[0]):
                                profit = temp
                        except TypeError:
                            print(type(profit))
                            #try:
                            #    print('Type Error', temp, type(temp))
                            #except UnboundLocalError:
                            #    print('could not call the call_sim method')
                            
                            
                        except SystemExit:
                            pass

                    print(time.time() - start_time)
                if max_profit == True:
                    fd = open(string, 'w', newline = '')
                    writer = csv.writer(fd)
                    writer.writerow(profit)
                    fd.close
                            #print('There is an error(0)', 'buy: ', buy_rsi, ', sell: ', sell_rsi)
            else:
                buy_rsi = args[0]
                sell_rsi = args[1]
                try:
                    temp = call_sim(price_file, rsi_file,buy_rsi,sell_rsi, **kwargs)
                    temp += [buy_rsi,sell_rsi]
                    #print(temp)
                    fd = open(string, 'a')
                    writer = csv.writer(fd)
                    writer.writerow(temp)
                    fd.close()
                    if save_progress == True:
                        if sell_rsi == end - 1:
                            progress = [item]
                        else:
                            progress = [item]
                        path = directory + '/progress.csv'
                        fd = open(path, 'a', newline = '')
                        writer = csv.writer(fd)
                        writer.writerow(progress)
                        fd.close()
                except SystemExit:
                    print('There is an error(1)')
            
            #print(profit)
            
                        
    
    
    pass

def call_sim(stock_data, rsi_data, buy_rsi, sell_rsi ,*args, **kwargs):
    return sim.main(stock_data, rsi_data, buy_rsi, sell_rsi, *args, **kwargs)
    pass
