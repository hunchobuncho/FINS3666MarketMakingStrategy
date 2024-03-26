import math
import csv
import statistics
import os


def get_prices(path):
    mid_prices = []
    with open(path) as csv_file:
        line_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in line_reader:
            line_count += 1
            if line_count == 10000:
                break
            mid_prices.append({"bid": float(row[2]), "ask": float(row[3])})
    return mid_prices


def indifference_price(s, q, t, standev):
    T = 1
    return s - q * standev ** 2 * (T - t)


def bid_ask_spread(y, standev, t, k):
    T = 1
    return y * standev ** 2 * (T - t) + (2 / y) * math.log(1 + y / k)


def calculate_pnl(prices, mid_prices, inventory):
    pnl = 0
    num_buys = 0
    num_sells = 0
    stdev_cache = [0] * len(prices)

    for i in range(1, len(prices)):
        t = float(len(prices) - i) / len(prices)

        # Calculate standard deviation once and cache it
        if stdev_cache[i] == 0 and i > 4:
            stdev_cache[i] = statistics.stdev(mid_prices[:i - 3])
        stdev = stdev_cache[i]
        indiff_price = indifference_price(mid_prices[0], inventory, t,
                                          stdev) if (i <= 4) else indifference_price(mid_prices[i - 4], inventory, t,
                                                                                     stdev)  # get indiff prices from 3 rows ago
        spread = bid_ask_spread(y, stdev, t, k=1.5)  # k is set as 1.5 as a parameter
        bid_price = prices[i]["bid"]
        ask_price = prices[i]["ask"]

        # Actual market making strategy
        if ask_price >= indiff_price + (spread / 2):  # We want the indiff price to be from 3 rows ago
            inventory -= 100 * (indiff_price + spread / 2)
            pnl += 100 * (indiff_price + spread / 2)
            num_sells += 1

        elif bid_price <= indiff_price - (spread / 2):  # indiff price has to be from 3 rows ago
            inventory += 100 * (indiff_price - spread / 2)
            pnl -= 100 * (indiff_price - spread / 2)
            num_buys += 1
    return {'pnl': pnl, 'num_buys': num_buys, 'num_sells': num_sells, 'inventory': inventory}


if __name__ == "__main__":

    # Loops through all the currency pairs and stores them in a dict
    all_prices = {}
    all_mid_prices = {}
    for filepath in os.listdir(os.getcwd() + '/data'):
        if os.path.isfile(os.getcwd() + '/data/' + filepath):
            all_prices[str(filepath)] = get_prices('data/' + filepath)

        all_mid_prices[str(filepath)] = [(x["bid"] + x["ask"]) / 2 for x in all_prices[str(filepath)]]

    current_time = 0
    pnl = 0

    # y = 50000

    for y in range(10, 101, 10):
        # y = 200000 # TODO: SWITCH TO THIS AND UNINDENT (SHIFT-TAB) IF YOU ONLY WANT TO TEST ONE GAMMA
                    # TODO: ALSO, IF YOU ONLY WANT TO TEST ONE CSV FILE, DRAG IT OUT OF THE DATA FOLDER AND
                    # INTO THE MAIN FOLDER

        # So let's say the strat is: we sell 100 units of AUDUSD over the ask price
        # We buy 100 units of AUDUSD when less than the bid price.
        # Inventories will be in total amount of asset (not whole units, it will be e.g. 10 * 0.91 = 9.1)

        final_pnls = {}
        final_buys = {}
        final_sells = {}
        final_inventory = {}
        for i in all_prices:
            inventory = 100 * (all_mid_prices[i][0])
            results = calculate_pnl(all_prices[i], all_mid_prices[i], inventory)
            final_pnls[i] = results['pnl']
            final_buys[i] = results['num_buys']
            final_sells[i] = results['num_sells']
            final_inventory[i] = results['inventory']

        # final_pnl = calculate_pnl(prices, mid_prices, inventory)
        # print(f" THE ACTUAL ONE FOR EUR/AUD.csv IS: {final_pnl}")


        print(f"If gamma was {y}: ")
        for i in final_pnls:
            print(f"Profit and Loss for: {i} is: {final_pnls[i]} || Final Inventory : {final_inventory[i]} "
                  f"|| Number of Buys: {final_buys[i]} || Number of Sells: {final_sells[i]}")