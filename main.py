import math
import csv
import statistics


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


if __name__ == "__main__":
    # T = 1: the Terminal time, q starts at 0 , t is time, y = 0.1,
    aud_usd_prices = get_prices("data/AUDUSD.csv")
    # Start with buying 10 units of the original price
    mid_pices = [(x["bid"] + x["ask"])/2 for x in aud_usd_prices]
    inventory = 100 * (mid_pices[0])
    current_time = 0
    standev = statistics.stdev(mid_pices)
    y = 0.1

    # So let's say the strat is: we sell 100 units of AUDUSD over the ask price
    # We buy 100 units of AUDUSD when less than the bid price.
    # Inventories will be in total amount of asset (not whole units, it will be e.g. 10 * 0.91 = 9.1)

    for i in range(1, len(aud_usd_prices)):
        t = float(len(aud_usd_prices) - i) / len(aud_usd_prices)
        indiff_price = indifference_price(mid_pices[i], inventory, t, standev)
        spread = bid_ask_spread(y, standev, t, 1) # I'll let k = 1 as a parameter, not sure what it should be
        if indiff_price + spread >= aud_usd_prices[i]["ask"]:
            inventory -= 100 * (indiff_price + spread)
        elif indiff_price - spread <= aud_usd_prices[i]["bid"]:
            inventory += 100 * (indiff_price - spread)

    print(f"\nFINAL INVENTORY IS: {inventory/(10**6)} million")

