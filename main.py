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
    prices = get_prices("data/AUDUSD.csv")
    # Start with buying 10 units of the original price
    mid_pices = [(x["bid"] + x["ask"]) / 2 for x in prices]
    inventory = 100 * (mid_pices[0])
    current_time = 0
    y = 0.5*(10**6)
    pnl = 0

    # So let's say the strat is: we sell 100 units of AUDUSD over the ask price
    # We buy 100 units of AUDUSD when less than the bid price.
    # Inventories will be in total amount of asset (not whole units, it will be e.g. 10 * 0.91 = 9.1)

    for i in range(1, len(prices)):
        t = float(len(prices) - i) / len(prices)
        stdev = 0 if i == 1 else statistics.stdev(mid_pices[:i]) #standard deviation up to a point
        indiff_price = indifference_price(mid_pices[i], inventory, t, stdev) # TODO: do we calculate the indiff price on the current price? or the previous row?
        spread = bid_ask_spread(y, stdev, t, k=1.5)  # k is set as 1.5 as a parameter
        bid_price = prices[i]["bid"]
        ask_price = prices[i]["ask"]
        print(f"INDIFF_PRICE: {indiff_price}, SPREAD: {spread}, STANDARD DEVIATION: {stdev}")
        print(f" Upper limit: {format(indiff_price + spread / 2, '.5f')} : ask price: {ask_price} || lower limit: {format(indiff_price - spread / 2, '.5f')} : bid price : {bid_price} \n")

        # Actual market making strategy
        if prices[i]["ask"] >= indiff_price + (spread/2):
            inventory -= 100 * (indiff_price + spread / 2)
            pnl += 100 * (indiff_price + spread / 2)

        elif prices[i]["bid"] <= indiff_price - (spread/2):
            inventory += 100 * (indiff_price - spread / 2)
            pnl -= 100 * (indiff_price - spread / 2)


    print(f"\nFor AUD/USD using the market making strategy, the FINAL INVENTORY IS: {inventory}")
    print(f"FINAL PnL for AUD/USD IS: {format(pnl, '.5f')}")

    #TODO: run for crypto, and for all currency pairs