import matplotlib.pylab as plt
import os
import pandas as pd
from random import choice
from math import inf
from csv import DictWriter
from agent_test import Agent, Agent_C, Agent_K
from period import Period

REDEMPTIONS = [260, 250, 240, 230, 220, 210, 200, 190, 180, 170]
COSTS = [160, 170, 180, 190, 200, 210, 220, 230, 240, 250]
QUANTITY = len(REDEMPTIONS)
TRADERS = 20
PERIODS = 15
TIME_STEPS = 725
PROPORTIONS = 0.5
PROPORTIONS_BUY = 0.5
PROPORTIONS_SEL = 0.5

# spread ration of 15% seems to work better for the variation of max and min trade
INFO_TRADERS = {"redemptions": [260, 250, 240, 230, 220, 210, 200, 190, 180, 170],
                "costs": [160, 170, 180, 190, 200, 210, 220, 230, 240, 250],
                "traders": 20,
                "proportions": 0.5,
                "proportions_sel": 0.5,
                "proportions_buy": 0.5,
                "time_frac": 0.1,
                "spread_ratio": 0.15,
                "profit_perc": .02}

def main():
    """
    Test version of the simulation of an CDA
    with fixed strategies and switching strategies.
    """

    # sort valuations from highest to lowest, costs from lowest to highest
    REDEMPTIONS.sort(reverse=True)
    COSTS.sort()

    # calculates maximum surplus
    maximum_surplus = max_surplus(REDEMPTIONS, COSTS, TRADERS)
    print(f"The maximum surplus is: {maximum_surplus}")

    for sim in range(2):

        # divide the traders equally into buyers and sellers and the right proportions
        # of strategies among the market sides
        agents_in_auction = divide_traders(INFO_TRADERS)

        # creates transaction period object
        trans_period = Period(agents_in_auction, TIME_STEPS)

        # starts loop for the total amount of transaction periods
        # for period in range(PERIODS):
        for period in range(PERIODS):


            # loop for amount of time steps per period
            # for time_step in range(TIME_STEPS):
            for time_step in range(TIME_STEPS):
                # print(f"Period: {period}  Time: {time_step}")
                # print("--------------------------------------")

                # checks which traders are willing to shout a bid or ask
                trans_period.set_activity_traders(time_step)

                if trans_period.active_agents:

                    # random agent to shout bid or ask
                    trader = trans_period.shout_offer()
                    # print(trader)
                    # print("--------------------------------------")
                    # print(f"Max bid: {trans_period.max_bid}")
                    # print(f"Min ask: {trans_period.min_ask}")
                    # print(f"Shout price trader: {trader.price}")
                    # print("--------------------------------------")

                    # checks if transactions is possible
                    if trans_period.check_transaction():

                        # chooses radomly a traders from the opposite market side to exchange
                        second_trader = trans_period.pick_agents_transactions(trader)

                        # checks if traders that shouted is buyer
                        if trader.type == "buyer":

                            # check if buyer has enough budget
                            if trans_period.check_buyer(trader, second_trader.price):

                                # procces transactions between the two traders
                                trans_period.procces_transaction(trader, second_trader,
                                    second_trader.price, period, time_step)

                                # check if traders can still participate in auction, otherwise update
                                trans_period.check_competing_agents(trader, second_trader, REDEMPTIONS, COSTS)

                        # checks if trader that shouted is seller
                        else:

                            # checks if the buyer has enough budget
                            if trans_period.check_buyer(second_trader, second_trader.price):

                                # procces transaction between the two traders
                                trans_period.procces_transaction(second_trader, trader,
                                    second_trader.price, period, time_step)

                                # check if traders can still participate in auction, otherwise update
                                trans_period.check_competing_agents(second_trader, trader, REDEMPTIONS, COSTS)

                    # check if trades are still possible
                    if trans_period.check_end_period():
                        print("END")
                        break

            # for agent in trans_period.agents_in_auction:
            #     print(agent)

            # set all agents "reseted" in auction and keep track of min max trade price
            trans_period.update_min_max_trade(period)
            trans_period.reset_agents_new_round(REDEMPTIONS, COSTS)

            print("--------------------------------------")
            print(f"PERIOD: {period}  TIME: {time_step}")
            print(f"MAX TRADE: {trans_period.max_trade}  MIN TRADE: {trans_period.min_trade}")
            if trans_period.surplus.get(period):
                print(f"EFFICIENCY: {round((trans_period.surplus[period] / maximum_surplus) * 100, 2)}%")
                print("--------------------------------------")

        all_data_simulation(sim, trans_period.data_surplus, trans_period.data)

def max_surplus(redemptions, costs, traders):
    """
    Calculates the maximum possible surplus
    """

    surplus = 0
    transactions = 0.5 * traders

    for redemption, cost in zip(redemptions, costs):
        if redemption >= cost:
            surplus += ((redemption - cost) * transactions)

    return surplus

def divide_traders(info_traders):
    """
    Divide traders equally into buyers and sellers
    and set the right proportions of strategies '
    among the market sides
    """

    agents = []
    amount_side = info_traders["proportions"] * info_traders["traders"]
    flag = 1

    # divide the kaplan agents on the demand side
    for kaplan in range(int(info_traders["proportions_buy"] * amount_side)):
        agents.append(Agent_K(flag, "buyer", info_traders["redemptions"],
                                info_traders["time_frac"],
                                info_traders["spread_ratio"],
                                info_traders["profit_perc"]))
        flag += 1

    # divide ZI_C agents on the demand side
    for zi in range(int((1-info_traders["proportions_buy"]) * amount_side)):
        agents.append(Agent_C(flag, "buyer", info_traders["redemptions"]))
        flag += 1

    # divide Kaplan agents on the supply side
    for kaplan in range(int(info_traders["proportions_sel"] * amount_side)):
        agents.append(Agent_K(flag, "seller", info_traders["costs"],
                                info_traders["time_frac"],
                                info_traders["spread_ratio"],
                                info_traders["profit_perc"]))
        flag += 1

    # divide ZI_C agents on the supply side
    for zi in range(int((1 - info_traders["proportions_sel"]) * amount_side)):
        agents.append(Agent_C(flag, "seller", info_traders["costs"]))
        flag += 1

    return agents

def all_data_simulation(id, surplus_periods, prices_periods):
    """
    Writes all collected data to a csv file
    """

    os.mkdir(f"simulations/{id}")
    for period, data in enumerate(prices_periods):
        dataframe_prices = pd.DataFrame(data)
        dataframe_surplus = pd.DataFrame(surplus_periods[period])
        all_data = pd.concat([dataframe_prices, dataframe_surplus], axis=1)
        all_data.to_csv(f"simulations/{id}/data_period{period + 1}.csv", na_rep="")
    pass


if __name__ == "__main__":
    main()
