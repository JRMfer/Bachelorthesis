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
        for time_step in range(675):
            print(time_step)
            print("--------------")

            # checks which traders are willing to shout a bid or ask
            trans_period.set_activity_traders(time_step)

            if trans_period.active_agents:

                # random agent to shout bid or ask
                trader = trans_period.shout_offer()
                print(trader)
                print("--------------")
                print(f"Max bid: {trans_period.max_bid}")
                print(f"Min ask: {trans_period.min_ask}")
                print(f"Shout price trader: {trader.price}")
                print("--------------")

                # checks if transactions is possible
                if trans_period.check_transaction():

                    print("DEAL")

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
                            trans_period.check_competing_agents(trader, second_trader, REDEMPTIONS)

                    # checks if trader that shouted is seller
                    else:

                        # checks if the buyer has enough budget
                        if trans_period.check_buyer(second_trader, second_trader.price):

                            # procces transaction between the two traders
                            trans_period.procces_transaction(second_trader, trader,
                                second_trader.price, period, time_step)

                            # check if traders can still participate in auction, otherwise update
                            trans_period.check_competing_agents(second_trader, trader, REDEMPTIONS)

                if time_step > 500:
                    print(f"Length competing agents: {len(trans_period.agents_in_auction)}")

                # AAN HET EINDE VAN EEN PERIODE MOET DE MAX EN MIN TRADE TRACK VARIABLE
                # OP EEN BEPAALDE MANIER WEER GERESET WORDEN!!!!!!!
                if trans_period.check_end_period():
                    print("END")
                    break

        print(trans_period)
        if trans_period.surplus.get(period):
            print(f"Allocative efficiency {period}: {round((trans_period.surplus[period] / maximum_surplus) * 100, 2)}%")
        # for agent in trans_period.agents_in_auction:
        #     print(f"ID: {agent.id} \nName: {agent.name} \nType: {agent.type} \nValuation agent: {agent.valuations[agent.index]}")

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
