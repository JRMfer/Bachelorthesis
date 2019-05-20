# Round
# Julien Fer (10649441)
# University of Amsterdam
#
# This script contains the functionality
# to represent a transaction period
# for a continuous double auction


from random import choice
from math import inf
from agent_test import Agent, Agent_C, Agent_K


class Period(object):
    """
    Reprensentation of the structure of
    transaction period CDA
    """

    def __init__(self, agents, total_time_steps):
        """
        Initializes a transaction period
        """

        self.agents_in_auction = agents
        self.steps = total_time_steps
        self.surplus = {}
        self.quantity = {}
        self.data = []
        self.data_surplus = []
        self.active_agents = []
        self.inactive_agents = []
        self.agents_out_auction = []
        self.max_bid = None
        self.min_ask = None
        self.max_trade = inf
        self.min_trade = -inf

    def __str__(self):
        return f"Surplus: {self.surplus} \nTransactions: {self.transactions} \nQuantity: {self.quantity}"


    def set_activity_traders(self, step):
        """
        Checks whihc traders are willing to shout bids/asks
        and seperate these in a seperate list
        """

        self.active_agents = []
        self.inactive_agents = []

        for agent in self.agents_in_auction:

            if agent.name == "Kaplan":

                if agent.check_activity(step, self.steps, self.max_bid, self.min_ask,
                                        self.min_trade, self.max_trade):
                    self.active_agents.append(agent)
                else:
                    self.inactive_agents.append(agent)

            elif agent.name == "ZI-C":

                if agent.check_activity(self.max_bid, self.min_ask):
                    self.active_agents.append(agent)
                else:
                    self.inactive_agents.append(agent)


    def shout_offer(self):
        """
        Randomly selects an agent from the active agents
        to shout a bid or ask and returns the chosen agent
        """

        agent = choice(self.active_agents)

        if agent.name == "ZI-C":
            if agent.type == "buyer":
                offer = agent.offer_price(self.max_bid, self.min_ask)
                self.max_bid = offer
                # return offer

            elif agent.type == "seller":
                offer = agent.offer_price(self.max_bid, self.min_ask)
                self.min_ask = offer
                # return offer

        elif agent.name == "Kaplan":
            if agent.type == "buyer":
                offer = agent.offer_price(self.max_bid, self.min_ask)
                self.max_bid = offer
                # return offer

            elif agent.type == "seller":
                offer = agent.offer_price(self.max_bid, self.min_ask)
                self.min_ask = offer
                # return offer

        return agent

    def check_transaction(self):
        """
        Checks if transaction is possible
        returns True or False
        """

        if not self.min_ask or not self.max_bid:
            return False

        return self.min_ask <= self.max_bid

    def pick_agents_transactions(self, agent):
        """
        Randomly selects buyer or seller depending on type agent
        that already can make a transaction from the set of
        active agents for transaction
        """

        if agent.type == "buyer":
            possible_sellers = []

            for active_agent in self.agents_in_auction:
                if active_agent.price:
                    if active_agent.type == "seller" and agent.price >= active_agent.price:
                        possible_sellers.append(active_agent)

            return choice(possible_sellers)

        else:
            possible_buyers = []

            for active_agent in self.agents_in_auction:
                if active_agent.price:
                    if active_agent.type == "buyer" and agent.price <= active_agent.price:
                        possible_buyers.append(active_agent)

            return choice(possible_buyers)

    def check_buyer(self, buyer, price):
        """
        Checks if buyer has enough budget
        to purchase the commodity
        """

        return buyer.budget - price >= 0

    def add_info_transaction(self, redemption, cost, price, period, time_step):
        """
        Keep track of total suprlus per period and of the transactions per
        time step in every period.
        """

        data = None

        try:
            data =self.data[period]
        except IndexError:
             data = None

        # calculates surplus
        surplus = redemption - cost

        if data:
            self.quantity[period] += 1
            self.surplus[period] += surplus
            transaction = {"price": price, "time": time_step}
            self.data[period].append(transaction)
            self.data_surplus[period][0]["surplus"] += surplus
            self.data_surplus[period][0]["quantity"] += 1
            pass
        else:
            self.quantity[period] = 1
            self.surplus[period] = surplus
            transaction = {"price": price, "time": time_step}
            self.data.append([transaction])
            data_surplus = {"surplus": surplus, "quantity": 1}
            self.data_surplus.append([data_surplus])


    def reset_agents(self):
        """
        Reset private outstanding bid or ask of all traders
        and activity
        """

        for agent in self.active_agents:
            agent.price == None
            # agent.active == False



    def procces_transaction(self, buyer, seller, price, period, time_step):
        """
        Adjust quantity seller/buyer, index of valuations, surplus
        budget and keep track individual transaction prices
        returns transaction price
        """

        # first update private information (profit, transasction price) of the
        # two traders.
        profit_buyer = buyer.valuations[buyer.index] - price
        buyer.add_info_transaction(period, time_step, price, profit_buyer)

        profit_seller = price - seller.valuations[seller.index]
        seller.add_info_transaction(period, time_step, price, profit_seller)

        # update information (surplus, transaction price, time step) time step
        # at the according period
        self.add_info_transaction(buyer.valuations[buyer.index],
                                    seller.valuations[seller.index], price,
                                    period, time_step)

        # adjust quantity, budget and the index of the valuations of both traders
        buyer.quantity += 1
        seller.quantity -= 1
        buyer.budget -= price
        seller.budget += price
        buyer.index += 1
        seller.index += 1

        # reset outstanding bids
        self.reset_agents()
        self.max_bid = None
        self.min_ask = None


    def check_competing_agents(self, buyer, seller, buyer_val, costs_val):
        """
        Checks if buyer/seller can still compete
        for the remainder of trading period,
        otherwise "save" in array for agents
        not competing in trading period
        """

        possible_trades_buyer = 0
        possible_trades_seller = 0

        if buyer.budget <= 0 or buyer.index >= (len(buyer_val) - 1):
            self.agents_out_auction.append(buyer)
            self.agents_in_auction.remove(buyer)
            buyer.active == False

        if seller.quantity == 0 or seller.index >= (len(costs_val) - 1):
            self.agents_out_auction.append(seller)
            self.agents_in_auction.remove(seller)
            seller.active == False


    def check_end_period(self):
        """
        Checks is agents still are possible
        to trade with each other, otherwise period has ended
        """

        if not self.agents_in_auction:
            return True

        possible_trades = False

        for agent in self.agents_in_auction:
            if agent.type == "buyer":
                for other_agent in self.agents_in_auction:
                    if (other_agent.type == "seller" and agent.budget
                        >= other_agent.valuations[other_agent.index]
                        and agent.valuations[agent.index] >=
                        other_agent.valuations[other_agent.index] and not
                        (agent.name == "Kaplan" and other_agent.name == "Kaplan")):
                        possible_trades = True
                        break

            if possible_trades:
                break

        return not possible_trades

    def update_min_max_trade(self, period):
        """
        Keep track of maximum and minimum
        transaction price of previous period
        """
        prices = [transaction['price'] for transaction in self.data[period]]
        self.min_trade = min(prices)
        self.max_trade = max(prices)


    def reset_agents_new_round(self, redemptions, costs):
        """
        Resets budget, quantity and index
        for all the agents when new round
        is about to start.
        """

        self.agents_in_auction += self.agents_out_auction
        self.agents_out_auction = []

        for agent in self.agents_in_auction:
            if agent.type == "buyer":
                agent.budget = sum(redemptions)
                agent.quantity = 0
                agent.index = 0

            else:
                agent.budget = 0
                agent.quantity = len(costs)
                agent.index = 0
