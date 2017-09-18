""" Assuming that the data file being read in is
consisting of 7 columns with headers of
Date, Open, High, Low, Close, Adj Close, Volume
"""
import csv
import statistics
import math
import sys
class Date:
    def __init__(self, string):
        assert len(string) == 10
        self.year = int(string[:4])
        self.month = int(string[5:7])
        self.day = int(string[8:])
        
    def __eq__(self, other):
        return (self.year == other.year and self.month == other.month
                and self.day == other.day)
    def __lt__(self, other):
        if (self.year < other.year):
            return True
        elif (self.year == other.year and self.month < other.month):
            return True
        elif (self.year == other.year and self.month == other.month
              and self.day < other.day):
            return True
        return False
    def __str__(self):
        return str(self.year) + "/" + str(self.month) + "/" + str(self.day)

    def __repr__(self):
        return self.__str__()
    

        

def read_data(file):
    #convert to list of lists
    try:
        raw_data = open(file, encoding='utf-8-sig')
    except FileNotFoundError:
        print(file + 'was not found')
        sys.exit()
    data = []
    for line in raw_data:
        if line[0] is 'D':
            continue
        if len(line.split(',')) != 7:
            continue
        new_list = line.split(',')
        for item in new_list:
            item = item.strip()
        try:
            numbers = [Date(new_list[0])]+[float(x) for x in new_list if x is not new_list[0]]
        except ValueError:
            print('Problem with data at: '+ str(Date(new_list[0])))
            continue
        data.append(numbers)
    raw_data.close()  
    return data


def date_sort(data):
    is_sorted = True
    for number in range(len(data)):
        if (number +1 < len(data) and data[number][0] > data[number + 1][0]):
            is_sorted = False
            temp_data = data[number+1]
            data[number + 1] = data[number]
            data[number] = temp_data
    if is_sorted is True:
        return data
    return date_sort(data)
    pass

def compute_rsi(number_days, data):
    result = []
    change_list = [[data[day][0] , data[day][5] - data[day-1][5]] for day in range(len(data)) if day-1 >=0]
    
    first_time = True
    current_date = []
    selection = change_list[0:number_days]
    gain = []
    loss = []
    for index in range(len(selection)):
        if selection[index][1]>0:
            gain.append(selection[index][1])
        elif selection[index][1]<0:
            loss.append(selection[index][1])
    if math.fsum(loss)!= float(0) and math.fsum(gain)!= float(0):
        RS = float((math.fsum(gain)/number_days)/(abs(math.fsum(loss))/number_days))
    elif math.fsum(gain)== float(0) and math.fsum(loss)!= float(0):
        RS = 0
    elif math.fsum(loss)== float(0) and math.fsum(gain)!= float(0):
        RS = 100
    else:
        RS = 3.1415927
    RSI = float(100 - 100/(1+ RS))
    try:
        result.append([change_list[number_days-1][0],RSI, math.fsum(gain)/number_days, abs(math.fsum(loss))/number_days])
    except IndexError:
        print('There is not enough stock information to calculate RSI')
        sys.exit()
    for value in range(number_days,len(change_list)):
        curr_gain = 0
        curr_loss = 0
        if change_list[value][1]>0:
            curr_gain = change_list[value][1]
        else:
            curr_loss = abs(change_list[value][1])
        avg_gain = float((float(result[-1][2]*(number_days-1)) + float(curr_gain))/number_days)
        avg_loss = float((float(result[-1][3]*(number_days-1)) + float(curr_loss))/number_days)
        if avg_loss!= float(0) and avg_gain!= float(0):
            RS = float(avg_gain/abs(avg_loss))
        elif avg_gain== float(0) and avg_loss!= float(0):
            RS = 0
        elif avg_loss== float(0) and avg_gain!= float(0):
            RS = 100
        else:
            RS = 3.1415927
        RSI = float(100 - 100/(1+ RS))
        result.append([change_list[value][0],RSI, avg_gain, avg_loss])
    return result        
    
def main(number_of_days, path):
    number_of_days = int(number_of_days)
    csv_path = path[:path.index('.')]+'-RSI.csv'
    print(csv_path)
    output_file= open(csv_path, 'w', newline='')
    output_writer = csv.writer(output_file)
    output_writer.writerow(['Date','RSI'])
    to_be_written= compute_rsi(number_of_days,date_sort(read_data(path)))
    for data in to_be_written:
        output_writer.writerow(data[:2])
    output_file.close()
    

#read_data('C:\Users\Ryan\Downloads\data\A.csv')

