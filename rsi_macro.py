import rsi_creator as RSI
import sys

def read_data(symbols_file, csv_path, number_of_days):
    file = open(symbols_file)
    for item in file:
        if item.strip() != 'Symbol':
            print(csv_path + '/' + item.strip() + '.csv')
            try:
                RSI.main(number_of_days, csv_path + '/' + item.strip() + '.csv')
            except SystemExit:
                print('Could not create RSI for ' + csv_path + '/' + item.strip() + '.csv')

def main_non_macro():
    symbol_file = input('Symbol list?\n')
    csv_path = input('Folder with all the csv\n')
    day_number = input('How many days for RSI\n')
    read_data(symbol_file, csv_path, day_number)

def main():
    symbol_file = sys.argv[1]
    csv_path = sys.argv[2]
    day_number = sys.argv[3]
    read_data(symbol_file, csv_path, day_number)

main()
