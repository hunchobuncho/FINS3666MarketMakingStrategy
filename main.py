import math
import csv
import statistics
def get_prices(path):
    mid_prices = []
    with open(path) as csv_file:
        line_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in line_reader:
            print(f"Bid price is: {row[2]} Ask price is: {row[3]} ")
            line_count += 1
            if line_count == 15:
                break
        mid_prices.append((float(row[2]) + float(row[3])) / 2)
    return mid_prices

def indifference_price(s, q, t, standev):
    T = 1
    return s - q * standev ** 2 * (T - t)

def bid_ask_spread(y, standev, t, k):
    T = 1
    return y* standev ** 2 * (T - t) + (2/y)*math.log(1+y/k)

if __name__ == "__main__":
    # T = 1: the Terminal time, q starts at 0 , t is time, y = 0.1,
    aud_usd_prices = get_prices("data/AUDUSD.csv")
    for i in range(len(aud_usd_prices)):
        print(aud_usd_prices[i])
        break
    # Start with buying 10 units of the original price
    inventory = 10 * aud_usd_prices[0]
    current_time = 0
    standev = statistics.stdev(aud_usd_prices)
    y = 0.1




    # So let's say the strat is: we sell 10 units of AUDUSD over the ask price
    # We buy 10 units of AUDUSD when less than the bid price.
    # Inventories will be in total amount of asset (not whole units, it will be e.g. 10 * 0.91 = 9.1)
    #
