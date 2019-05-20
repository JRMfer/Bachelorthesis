import matplotlib.pylab as plt
import os
import pandas as pd
from random import choice
from math import inf
from agent_test import Agent, Agent_C, Agent_K
from period import Period


def simulation(redemptions, costs, info_traders, simulations, periods, time_steps):

    # sort valuations from highest to lowest, costs from lowest to highest
    redemptions.sort(reverse=True)
    costs.sort()

    # calculates maximum surplus
    maximum_surplus = max_surplus(redemptions, costs, info_traders["traders"])

    # run certain amount of simulations
    for sim in range(simulations):

        # divide the number of agents participating in auction
        agents_in_auction = divide_traders(info_traders)

        # creates transaction period object
        trans_period = Period(agents_in_auction, time_steps, info_traders["min_price"],
                              info_traders["max_price"])

        # starts loop for the total amount of transaction periods
        for period in range(periods):

            trans_period.period = period

            # loop for amount of time steps per period
            for time_step in range(time_steps):

                # set activity agents
                trans_period.set_activity_traders(time_step)

                # checks if agents that are willing to shout are found
                if trans_period.active_agents:

                    # random agent to shout bid or ask
                    trader = trans_period.shout_offer()

                    # checks if transactions is possible
                    if trans_period.check_transaction():

                        # chooses radomly a traders from the opposite market side to exchange
                        second_trader = trans_period.pick_agents_transactions(
                            trader)

                        # checks if traders that shouted is buyer
                        if trader.type == "buyer":

                            # check if buyer has enough budget
                            if trans_period.check_buyer(trader, second_trader.price):

                                # procces transactions between the two traders
                                trans_period.procces_transaction(trader, second_trader,
                                                                 second_trader.price,
                                                                 period, time_step)

                                # check if traders can still participate in auction,
                                trans_period.check_competing_agents(trader,
                                                                    second_trader,
                                                                    redemptions,
                                                                    costs)

                        # checks if trader that shouted is seller
                        else:

                            # checks if the buyer has enough budget
                            if trans_period.check_buyer(second_trader,
                                                        second_trader.price):

                                # procces transaction between the two traders
                                trans_period.procces_transaction(second_trader, trader,
                                                                 second_trader.price,
                                                                 period, time_step)

                                # check if traders can still participate in auction
                                trans_period.check_competing_agents(second_trader,
                                                                    trader,
                                                                    redemptions,
                                                                    costs)

                    # check if trades are still possible
                    if trans_period.check_end_period():
                        break

            # set all agents "reseted" in auction and keep track of min max trade price
            trans_period.update_min_max_trade(period)
            trans_period.reset_agents_new_round(redemptions, costs)

        all_data_simulation(sim, trans_period.data_surplus,
                            trans_period.data_transactions,
                            trans_period.agents_in_auction)


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
    for zi in range(int((1 - info_traders["proportions_buy"]) * amount_side)):
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


def all_data_simulation(id, surplus_periods, prices_periods, agents):
    """
    Writes all collected data to a csv file
    """

    # makes folder for simulations, if it does not yet exist
    if not os.path.exists(f"simulations/{id + 1}"):
        os.mkdir(f"simulations/{id + 1}")

    # loop for all the data collectied in transaction periods
    for period, data in enumerate(prices_periods):

        # makes folder for every period, if it does not yet exist
        if not os.path.exists(f"simulations/{id + 1}/period{period + 1}"):
            os.mkdir(f"simulations/{id + 1}/period{period + 1}")

        # makes data frame from transaction prices, surplus and quantity
        dataframe_prices = pd.DataFrame(data)
        dataframe_surplus = pd.DataFrame(surplus_periods[period])
        all_data = pd.concat([dataframe_prices, dataframe_surplus], axis=1)

        # writes the data frame to a csv file
        all_data.to_csv(
            f"simulations/{id + 1}/period{period + 1}/data_period{period + 1}.csv",
            index=False, na_rep="")

        # track variables for data agents in the same period
        data_period_all_agents = []
        info_agents = []

        # loop over all agents
        for agent in agents:

            # makes data frame of data agent for the given period
            data_agent = pd.DataFrame(agent.data[period])

            # appen dataframe and corresponding info to a list
            data_period_all_agents.append(data_agent)
            info_agents.append(f"{agent.name} {agent.type} {agent.id}")

        # concat all dataframes together, index is the agent's strategy,
        # market side and id
        data_agents = pd.concat(data_period_all_agents, keys=info_agents)

        # write dataframe to csv file
        data_agents.to_csv(
            f"simulations/{id + 1}/period{period + 1}/data_agents{period + 1}.csv")


if __name__ == "__main__":

    # reads the valuations from csv
    # and stores redemptions and costs in seperate list
    valuations = pd.read_csv("../data/valuations.csv")
    redemptions = valuations["redemptions"].tolist()
    costs = valuations["costs"].tolist()

    # ensures proper value for minimum shout price
    min_price = ""
    while not min_price.isdigit() or int(min_price) >= min(costs) or int(min_price) < 0:
        min_price = input("Enter the minimum price that a trader can shout: ")

    min_price = int(min_price)

    # ensures proper value for maximum shout price
    max_price = ""
    while not max_price.isdigit() or int(max_price) <= max(redemptions):
        max_price = input("Enter the maximum price that a trader can shout: ")

    max_price = int(max_price)

    # ensures proper value for amount of simulations
    simulations = ""
    while not simulations.isdigit() or int(simulations) <= 0:
        simulations = input("Enter the amount of simulations: ")

    simulations = int(simulations)

    # ensures propor value for amount of periods
    periods = ""
    while not periods.isdigit() or int(periods) <= 0:
        periods = input("Enter the amount of transaction periods: ")

    periods = int(periods)

    # ensures propor value for amount of time steps
    time_steps = ""
    while not time_steps.isdigit() or int(time_steps) <= 0:
        time_steps = input(
            "Enter the amount of time steps for each transaction period: ")

    time_steps = int(time_steps)

    # ensures proper value for time fraction Kaplan agents
    time_frac = ""
    while ("." not in time_frac or round(float(time_frac), 2) <= 0
           or round(float(time_frac), 2) > 1):

        time_frac = input("Enter time fraction Kaplan agents: ")

    time_frac = round(float(time_frac), 2)

    # ensures proper value for spread_ratio Kaplan agents
    spread_ratio = ""
    while ("." not in spread_ratio or round(float(spread_ratio), 2) <= 0
           or round(float(spread_ratio), 2) > 1):

        spread_ratio = input("Enter spread ratio Kaplan agents: ")

    spread_ratio = round(float(spread_ratio), 2)

    # ensures proper value for profit_perc Kaplan agents
    profit_perc = ""
    while ("." not in profit_perc or round(float(profit_perc), 2) <= 0
           or round(float(profit_perc), 2) > 1):

        profit_perc = input("Enter profit percentage Kaplan agents: ")

    profit_perc = round(float(profit_perc), 2)

    prop_buy = ""
    while ("." not in prop_buy or round(float(prop_buy), 1) < 0.5
           or round(float(prop_buy), 1) > 0.7):

        prop_buy = input(
            "Enter the proportion of Kaplan agents on the demand side: ")

    prop_buy = round(float(prop_buy), 1)

    prop_sel = ""
    while ("." not in prop_sel or round(float(prop_sel), 1) < 0.5
           or round(float(prop_sel), 1) > 0.7):

        prop_sel = input(
            "Enter the proportion of Kaplan agents on the supply side: ")

    prop_sel = round(float(prop_sel))

    traders = ""

    while (not traders.isdigit() or int(traders) <= 0 or int(traders) % 2 > 0
    or (int(traders) / 2) % 2 > 0 or isinstance((int(traders) / 2) * prop_buy, int)
            or isinstance((int(traders) / 2) * prop_sel, int)):

        traders = input("Enter the total amount of traders: ")

    traders = int(traders)

    # collect all input (time_frac: 0.2, spread_ratio: 0.15 and profit_perc: 0.02)
    # doet het tot nu toe goed.
    info_traders = {"redemptions": redemptions,
                    "costs": costs,
                    "max_price": max_price,
                    "min_price": min_price,
                    "traders": traders,
                    "proportions": 0.5,
                    "proportions_sel": prop_sel,
                    "proportions_buy": prop_buy,
                    "time_frac": time_frac,
                    "spread_ratio": spread_ratio,
                    "profit_perc": profit_perc}

    simulation(redemptions, costs, info_traders,
               simulations, periods, time_steps)
