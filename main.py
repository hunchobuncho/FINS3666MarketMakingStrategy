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
            if line_count == 20000:
                break
            mid_prices.append({"bid": float(row[2]), "ask": float(row[3])})
    return mid_prices


def indifference_price(s, q, t, standev):
    T = 1
    return s - y * q * standev ** 2 * (T - t)


def bid_ask_spread(y, standev, t, k):
    T = 1
    return y * standev ** 2 * (T - t) + (2 / y) * math.log(1 + y / k)

def pnl_symmetric_strat(prices, mid_prices, inventory, y):
    pnl = 0
    num_buys = 0
    num_sells = 0
    stdev_cache = [0] * len(prices)
    pnl_list = []

    for i in range(1, len(prices)):
        t = i / len(prices)

        # Calculate standard deviation once and cache it
        if stdev_cache[i] == 0 and i > 4:
            stdev_cache[i] = statistics.stdev(mid_prices[:i - 3])
        stdev = stdev_cache[i]
        spread = bid_ask_spread(y, stdev, t, k=3000)  # k is set as 1.5 as a parameter
        bid_price = prices[i]["bid"]
        ask_price = prices[i]["ask"]

        mid_price = mid_prices[0] if (i <= 4) else mid_prices[i-4]

        # Actual market making strategy
        if ask_price >= mid_price + (spread / 2):  # We want the indiff price to be from 3 rows ago
            inventory -= 100 * (mid_price + spread / 2)
            pnl += 100 * (mid_price + spread / 2)
            num_sells += 1

        elif bid_price <= mid_price - (spread / 2):  # indiff price has to be from 3 rows ago
            inventory += 100 * (mid_price - spread / 2)
            pnl -= 100 * (mid_price - spread / 2)
            num_buys += 1
        pnl_list.append(pnl)
    return {'pnl': pnl, 'num_buys': num_buys, 'num_sells': num_sells, 'inventory': inventory, 'pnl_list': pnl_list}

def write_to_csv(file_name, fieldnames, data):
    with open(file_name, mode='w', newline='') as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in data:
                csv_writer.writerow(row)

def pnl_inventory_strat(prices, mid_prices, inventory, y):
    pnl = 0
    num_buys = 0
    num_sells = 0
    stdev_cache = [0] * len(prices)
    pnl_list = []

    for i in range(1, len(prices)):
        t = i / len(prices)

        # Calculate standard deviation once and cache it
        if stdev_cache[i] == 0 and i > 4:
            stdev_cache[i] = statistics.stdev(mid_prices[:i - 3])
        stdev = stdev_cache[i]
        indiff_price = indifference_price(mid_prices[0], inventory, t,
                                          stdev) if (i <= 4) else indifference_price(mid_prices[i - 4], inventory, t,
                                                                                     stdev)  # get indiff prices from 3 rows ago
        spread = bid_ask_spread(y, stdev, t, k=3000)  # k is set as 1.5 as a parameter
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
        pnl_list.append(pnl)
        # print(f"Bid ask spread{spread}, indiff price {indiff_price}")
    return {'pnl': pnl, 'num_buys': num_buys, 'num_sells': num_sells, 'inventory': inventory, 'pnl_list': pnl_list}


if __name__ == "__main__":

    # Loops through all the currency pairs and stores them in a dict
    all_prices = {}
    all_mid_prices = {}
    for filepath in os.listdir(os.getcwd() + '/data'):
        if os.path.isfile(os.getcwd() + '/data/' + filepath):
            all_prices[str(filepath)] = get_prices('data/' + filepath)
        # Get mid_prices
        all_mid_prices[str(filepath)] = [(x["bid"] + x["ask"]) / 2 for x in all_prices[str(filepath)]]

    current_time = 0
    pnl = 0

    for y in [1]:

        # So let's say the strat is: we sell 100 units of AUDUSD over the ask price
        # We buy 100 units of AUDUSD when less than the bid price.
        # Inventories will be in total amount of asset (not whole units, it will be e.g. 10 * 0.91 = 9.1)
        print(f"=============GAMMA IS {y}=============")
        final_inv_strat_pnls = {}
        final_inv_strat_buys = {}
        final_inv_strat_sells = {}
        final_inv_strat_inventory = {}
        final_inv_strat_pnl_plot = {}

        final_sym_strat_pnls = {}
        final_sym_strat_buys = {}
        final_sym_strat_sells = {}
        final_sym_strat_inventory = {}
        final_sym_strat_pnl_plot = {}
        for i in all_prices:
            starting_inv = 100 * (all_mid_prices[i][0])
            inventory_results = pnl_inventory_strat(all_prices[i], all_mid_prices[i], starting_inv, y)
            symmetric_results = pnl_symmetric_strat(all_prices[i], all_mid_prices[i], starting_inv, y)
            
            final_inv_strat_pnls[i] = inventory_results['pnl']
            final_inv_strat_buys[i] = inventory_results['num_buys']
            final_inv_strat_sells[i] = inventory_results['num_sells']
            final_inv_strat_inventory[i] = inventory_results['inventory']
            final_inv_strat_pnl_plot[i] = inventory_results['pnl_list']

            final_sym_strat_pnls[i] = symmetric_results['pnl']
            final_sym_strat_buys[i] = symmetric_results['num_buys']
            final_sym_strat_sells[i] = symmetric_results['num_sells']
            final_sym_strat_inventory[i] = symmetric_results['inventory']
            final_sym_strat_pnl_plot[i] = symmetric_results['pnl_list']

        print("=============Inventory Strategy ==================")
        for i in final_inv_strat_pnls:
            print(f"Profit and Loss for: {i} is: {final_inv_strat_pnls[i]} || Inventory : {final_inv_strat_inventory[i]} "
                  f"|| Number of Buys: {final_inv_strat_buys[i]} || Number of Sells: {final_inv_strat_sells[i]}")

        print("=============Symmetric Strategy ==================")

        for i in final_sym_strat_pnls:
            print(f"Profit and Loss for: {i} is: {final_sym_strat_pnls[i]} || Inventory : {final_sym_strat_inventory[i]} "
                  f"|| Number of Buys: {final_sym_strat_buys[i]} || Number of Sells: {final_sym_strat_sells[i]}")

        inventory_data = []
        for key in final_inv_strat_pnls:
            inventory_data.append({
                'Currency': key,
                'PnL': final_inv_strat_pnls[key],
                'Inventory': final_inv_strat_inventory[key],
                'Number of Buys': final_inv_strat_buys[key],
                'Number of Sells': final_inv_strat_sells[key],
                'PnL Plot': final_inv_strat_pnl_plot[key],
            })

        symmetric_data = []
        for key in final_sym_strat_pnls:
            symmetric_data.append({
                'Currency': key,
                'PnL': final_sym_strat_pnls[key],
                'Inventory': final_sym_strat_inventory[key],
                'Number of Buys': final_sym_strat_buys[key],
                'Number of Sells': final_sym_strat_sells[key],
                'PnL Plot': final_sym_strat_pnl_plot[key],
            })

        # Writing to CSV files
        inventory_fields = ['Currency', 'PnL', 'Inventory', 'Number of Buys', 'Number of Sells', 'PnL Plot']
        write_to_csv('inventory_method.csv', inventory_fields, inventory_data)

        symmetric_fields = ['Currency', 'PnL', 'Inventory', 'Number of Buys', 'Number of Sells', 'PnL Plot']
        write_to_csv('symmetric_method.csv', symmetric_fields, symmetric_data)

        # TODO: plot pnl for both
        # TODO: plot inventory

        csv_file_name = 'inventory_pnl_plot.csv'
        with open(csv_file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(final_inv_strat_pnl_plot.keys())
            for row in zip(*final_inv_strat_pnl_plot.values()):
                writer.writerow(row)

        csv_file_name = 'symmetric_pnl_plot.csv'
        with open(csv_file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(final_sym_strat_pnl_plot.keys())
            for row in zip(*final_sym_strat_pnl_plot.values()):
                writer.writerow(row)




