import math
import csv
import statistics
import os

# CONSTANTS
NUM_SIMULATIONS = 3000
K_PARAM = 3000
GAMMA = 1
TERMINAL_TIME = 1

'''
Gets all of the bid and ask prices given a path

Parameters
---------------
path: string 

Returns 
--------------
A list of all of the bid and ask prices (not mid prices)
'''
def get_prices(path):
    mid_prices = []
    with open(path) as csv_file:
        line_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in line_reader:
            line_count += 1
            if line_count == NUM_SIMULATIONS:
                break
            mid_prices.append({"bid": float(row[2]), "ask": float(row[3])})
    return mid_prices

'''
Calculate Indifference Price

Parameters
---------------
s: the mid price of the asset -> float 
q: total inventory of asset -> float
t: current time as a fraction of the terminal time -> float
standev: standard deviation of asset up to a particular time -> float
y: Gamma parameter -> float

Returns 
--------------
The indifference price, which is the mid-price adjusted for time approaching the terminal time 
and inventory -> float
'''
def indifference_price(s, q, t, standev, y):
    T = TERMINAL_TIME
    return s - y * q * standev ** 2 * (T - t)


'''
Calculates the bid ask spread

Parameters
---------------
y: Gamma parameter -> float
t: Current time as a fraction of the terminal time -> float
standev: Standard deviation of asset up to a particular time -> float
k: The K parameter -> float

Returns 
--------------
The final bid ask spread
'''
def bid_ask_spread(y, standev, t, k):
    T = TERMINAL_TIME
    return y * standev ** 2 * (T - t) + (2 / y) * math.log(1 + y / k)


def write_to_csv(file_name, fieldnames, data):
    with open(file_name, mode='w', newline='') as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in data:
            csv_writer.writerow(row)

def write_list_to_csv(csv_file_name, plot):
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(plot.keys())
        for row in zip(*plot.values()):
            writer.writerow(row)


def calculate_pnl(prices, mid_prices, inventory, y, is_symmetric_method=None):
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
        indiff_price = 0
        if (is_symmetric_method is None):
            indiff_price = indifference_price(mid_prices[0], inventory, t,
                                              stdev, GAMMA) if (i <= 4) else indifference_price(mid_prices[i - 4],
                                                                                                inventory,
                                                                                                t,
                                                                                                stdev,
                                                                                                GAMMA)  # get indiff prices from 3 rows ago
        else:
            indiff_price = mid_prices[0] if (i <= 4) else mid_prices[i - 4]

        spread = bid_ask_spread(y, stdev, t, k=K_PARAM)  # k is set as 1.5 as a parameter
        bid_price = prices[i]["bid"]
        ask_price = prices[i]["ask"]

        # Actual market making strategy: if price moves below or above our bounds, then buy or sell asset
        if ask_price >= indiff_price + (spread / 2):
            inventory -= 100 * (indiff_price + spread / 2)
            pnl += 100 * (indiff_price + spread / 2)
            num_sells += 1

        elif bid_price <= indiff_price - (spread / 2):
            inventory += 100 * (indiff_price - spread / 2)
            pnl -= 100 * (indiff_price - spread / 2)
            num_buys += 1
        pnl_list.append(pnl)
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

    # So let's say the strat is: we sell 100 units of AUDUSD over the ask price
    # We buy 100 units of AUDUSD when less than the bid price.
    # Inventories will be in total amount of asset (not whole units, it will be e.g. 10 * 0.91 = 9.1)
    print(f"=============GAMMA IS {GAMMA}, K IS {K_PARAM}=============")
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
        inventory_results = calculate_pnl(all_prices[i], all_mid_prices[i], starting_inv, GAMMA)
        symmetric_results = calculate_pnl(all_prices[i], all_mid_prices[i], starting_inv, GAMMA, True)

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

    # ================= SETUP CSV FILES =======================
    inventory_data = []
    for key in final_inv_strat_pnls:
        inventory_data.append({
            'Currency': key,
            'PnL': final_inv_strat_pnls[key],
            'Inventory': final_inv_strat_inventory[key],
            'Number of Buys': final_inv_strat_buys[key],
            'Number of Sells': final_inv_strat_sells[key],
        })

    symmetric_data = []
    for key in final_sym_strat_pnls:
        symmetric_data.append({
            'Currency': key,
            'PnL': final_sym_strat_pnls[key],
            'Inventory': final_sym_strat_inventory[key],
            'Number of Buys': final_sym_strat_buys[key],
            'Number of Sells': final_sym_strat_sells[key],
        })

    # Write to CSV Files
    inventory_fields = ['Currency', 'PnL', 'Inventory', 'Number of Buys', 'Number of Sells']
    write_to_csv('inventory_method.csv', inventory_fields, inventory_data)

    symmetric_fields = ['Currency', 'PnL', 'Inventory', 'Number of Buys', 'Number of Sells']
    write_to_csv('symmetric_method.csv', symmetric_fields, symmetric_data)

    csv_file_name = 'inventory_pnl_plot.csv'
    write_list_to_csv(csv_file_name, final_inv_strat_pnl_plot)

    csv_file_name = 'symmetric_pnl_plot.csv'
    write_list_to_csv(csv_file_name, final_sym_strat_pnl_plot)
