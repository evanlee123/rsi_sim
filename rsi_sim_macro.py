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
                #WHILE LOADING, SKIPS VALUES IN THE LIST UNTILL IT THE ITEM IN THE PROGRESS.CSV FILE MATCHES THE CURRENT ITEM IN FILE
                load = pd.read_csv(directory + '/progress.csv')
                value = list(load.columns.values)
                if str(value[0]) != str(item):
                    print('Skipping: ' + str(item))
                    continue
                if str(value[0]) == str(item):
                    print('Loaded at at: ' + str(item))
                    first_file = False

        #MAKES SURE THAT THE ITEM IN FILE IS AN ACTUALY TICKER SYMBOL
        if item.strip() != 'Symbol':
            string = directory + '/' + item.strip() + '-profit.csv'
            #Writes the data for current file if file is the one left off on progress.csv or if no loading
            if load_prog == False or first_file == False:
                fieldnames = ['Profit', 'Number of Transactions', 'Avg gain',
                              'Avg time for transaction', 'buy rsi', 'sell rsi']
                write_row(string, 'w', fieldnames)

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
                print('Trying All RSI in range: ' + str(beg) +", " + str(end))
                #THIS REPRESENT BUY VALUE CYCLING THROUGH
                for number in range(beg,end):
                    #makes sure that if loading, that it loads to the right buying rsi value
                    if load_prog== True and first_buy == True:
                        if str(number) != str(value[1]):
                            continue
                        if str(number) == str(value[1]):
                            first_buy = False
                    start_time = time.time()
                    buy_rsi = number
                    #THIS REPRESENTS SELL VALUE CYCLYING THROUGH
                    for integer in range(beg,end):
                        #makes sure it is on the right selling rsi value if loading
                        if load_prog == True and first_sell == True:
                            if str(integer) != str(value[2]):
                                continue
                            first_sell = False
                            print(value)
                        sell_rsi = integer
                        #Writes the rsi value data into a csv file
                        try:
                            temp = call_sim(price_file, rsi_file, buy_rsi, sell_rsi, **kwargs)
                            temp += [buy_rsi,sell_rsi]
                            write_row(string, 'a', temp)
                            #Saves current transaction to the progress csv is saving is enabled
                            if save_prog == True:
                                if sell_rsi == end - 1:
                                    progress = [item, buy_rsi +1, beg, profit]
                                else:
                                    progress = [item, buy_rsi, sell_rsi+1, profit]
                                write_row(str(directory + '/progress.csv'),'w', progress)
                                
                            if profit == []:
                                profit = temp
                            elif float(profit[0]) < float(temp[0]):
                                profit = temp
                                
                            #AT THIS POINT PROFIT SHOULD BE ONE OF THE TRANSACTIONS DONE
                        except TypeError:
                            print("Type Error")
                            print(type(profit))
                            
                        except SystemExit:
                            print("Something tried to make the program exit")
                            pass

                    print(time.time() - start_time)
                if max_profit == True:
                    write_row(string, 'a', profit)

            #THIS IS IF SPECIFIED TO ONLY RUN ONE SPECIFIC BUY SELL RSI VALUE
            else:
                buy_rsi = args[0]
                sell_rsi = args[1]
                try:
                    temp = call_sim(price_file, rsi_file,buy_rsi,sell_rsi, **kwargs)
                    temp += [buy_rsi,sell_rsi]
                    #print(temp)
                    write_row(string, 'a', temp)
                    if save_progress == True:
                        if sell_rsi == end - 1:
                            progress = [item]
                        else:
                            progress = [item]
                        write_row(str(directory + '/progress.csv'), 'a', progress)
                except SystemExit:
                    print('There is an error(1)')
                
def call_sim(stock_data, rsi_data, buy_rsi, sell_rsi ,*args, **kwargs):
    return sim.main(stock_data, rsi_data, buy_rsi, sell_rsi, *args, **kwargs)
    pass

#string is a string of the directory, write type is a string, field is a list
def write_row(string, write_type, field):
    with open(string, write_type, newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field)
        csvfile.close()  
