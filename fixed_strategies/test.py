import matplotlib.pylab as plt
from random import choice
from math import inf
from agent_test import Agent, Agent_C, Agent_K
from period import Period

REDEMPTIONS = [260, 250, 240, 230, 220, 210, 200, 190, 180, 170]
COSTS = [160, 170, 180, 190, 200, 210, 220, 230, 240, 250]
QUANTITY = len(REDEMPTIONS)
TRADERS = 20
PERIODS = 15
TIME_STEPS = 500
PROPORTIONS = 0.5

INFO_TRADERS = {"redemptions": [260, 250, 240, 230, 220, 210, 200, 190, 180, 170],
                "costs": [160, 170, 180, 190, 200, 210, 220, 230, 240, 250],
                "traders": 20,
                "proportions": 0.5,
                "time_frac": 0.1,
                "spread_ratio": 0.1,
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

    # divide the traders equally into buyers and sellers and the right proportions
    # of strategies among the market sides
    agents_in_auction = divide_traders(INFO_TRADERS)

    # creates transaction period object
    trans_period = Period(agents_in_auction, TIME_STEPS)


    trans_period.set_activity_traders(0)

    # starts loop for the total amount of transaction periods
    # for period in range(PERIODS):
    for period in range(1):

        # RESET TRACKING VARIABLES FOR EVERY BEGINNING OF NEW PERIOD

        # loop for amount of time steps per period
        # for time_step in range(TIME_STEPS):
        for time_step in range(100):

            trans_period.set_activity_traders(time_step)
            trader = trans_period.shout_offer()

            if trans_period.check_transaction():
                second_trader = trans_period.pick_agents_transactions(trader)

                if trader.type == "buyer":
                    if trans_period.check_buyer(trader, second_trader.price):
                        trans_period.procces_transaction(trader, second_trader,
                            second_trader.price, period, time_step)
                else:
                    if trans_period.check_buyer(second_trader, second_trader.price):
                        trans_period.procces_transaction(second_trader, trader,
                            second_trader.price, period, time_step)

                pass

            pass
    pass


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
    amount_side = 0.5 * info_traders["traders"]
    flag = 1

    # divide the kaplan agents on the demand side
    for kaplan in range(int(info_traders["proportions"] * amount_side)):
        agents.append(Agent_K(flag, "buyer", info_traders["redemptions"],
                                info_traders["time_frac"],
                                info_traders["spread_ratio"],
                                info_traders["profit_perc"]))
        flag += 1

    # divide ZI_C agents on the demand side
    for zi in range(int((1-info_traders["proportions"]) * amount_side)):
        agents.append(Agent_C(flag, "buyer", info_traders["redemptions"]))
        flag += 1

    # divide Kaplan agents on the supply side
    for kaplan in range(int(info_traders["proportions"] * amount_side)):
        agents.append(Agent_K(flag, "seller", info_traders["costs"],
                                info_traders["time_frac"],
                                info_traders["spread_ratio"],
                                info_traders["profit_perc"]))
        flag += 1

    # divide ZI_C agents on the supply side
    for zi in range(int((1 - info_traders["proportions"]) * amount_side)):
        agents.append(Agent_C(flag, "seller", info_traders["costs"]))
        flag += 1

    return agents


if __name__ == "__main__":
    main()
