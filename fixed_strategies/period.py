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

    def __init__(self, agents, total_time_steps, min_shout, max_shout):
        """
        Initializes a transaction period with attributes to keep track
        of agents in/out auction, active/inactive agents, max bid
        and min ask, max/min trade previous period, the gained surplus and
        corresponding quantities and all transactions made.
        """

        self.agents_in_auction = agents
        self.steps = total_time_steps
        self.min_shout = min_shout
        self.max_shout = max_shout
        self.data_transactions = []
        self.data_surplus = []
        self.active_agents = []
        self.inactive_agents = []
        self.agents_out_auction = []
        self.period = 0
        self.max_bid = None
        self.min_ask = None
        self.max_trade = inf
        self.min_trade = -inf

    def __str__(self):
        """
        Print current gained surplus and corresponding quantity
        and all transactions
        """

        return f"Transactions: {self.transactions} "

    def set_activity_traders(self, step):
        """
        Checks which traders are willing to shout bids/asks (active)
        and seperate the active agents from the inactive agents
        """

        self.active_agents = []
        self.inactive_agents = []

        for agent in self.agents_in_auction:

            if agent.name == "Kaplan":

                if agent.check_activity(step, self.steps, self.max_bid,
                                        self.min_ask, self.min_trade,
                                        self.max_trade):

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
                offer = agent.offer_price(self.max_bid, self.min_ask,
                                          self.min_shout, self.max_shout)
                self.max_bid = offer

            elif agent.type == "seller":
                offer = agent.offer_price(self.max_bid, self.min_ask,
                                          self.min_shout, self.max_shout)
                self.min_ask = offer

        elif agent.name == "Kaplan":
            if agent.type == "buyer":
                offer = agent.offer_price(self.max_bid, self.min_ask)
                self.max_bid = offer

            elif agent.type == "seller":
                offer = agent.offer_price(self.max_bid, self.min_ask)
                self.min_ask = offer

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
            data = self.data_transactions[period]

        except IndexError:
            data = None

        # calculates surplus
        surplus = redemption - cost

        if data:
            transaction = {"price": price, "time": time_step}
            self.data_transactions[period].append(transaction)
            self.data_surplus[period][0]["surplus"] += surplus
            self.data_surplus[period][0]["quantity"] += 1

        else:
            transaction = {"time": time_step, "price": price, }
            self.data_transactions.append([transaction])
            data_surplus = {"surplus": surplus, "quantity": 1}
            self.data_surplus.append([data_surplus])

    def reset_agents(self):
        """
        Reset private outstanding bid or ask of all traders
        and activity
        """

        for agent in self.agents_in_auction:
            agent.price = None

    def procces_transaction(self, buyer, seller, price, period, time_step):
        """
        Adjust for seller and buyer quantity, index of valuations, surplus,
        budget and keep track of prive information (price, profit). Also keep
        track of information per period.
        Finally reset outstanding offers in period and made by agents
        """

        # add info transaction for buyer and seller
        profit_buyer = buyer.valuations[buyer.index] - price
        buyer.add_info_transaction(period, time_step, price, profit_buyer)

        profit_seller = price - seller.valuations[seller.index]
        seller.add_info_transaction(period, time_step, price, profit_seller)

        # add info transactions for curren period
        self.add_info_transaction(buyer.valuations[buyer.index],
                                  seller.valuations[seller.index], price,
                                  period, time_step)

        # adjust quantity, budget, index buyer and seller
        buyer.quantity += 1
        seller.quantity -= 1
        buyer.budget -= price
        seller.budget += price
        buyer.index += 1
        seller.index += 1

        # reset
        self.reset_agents()
        self.max_bid = None
        self.min_ask = None

    def check_competing_agents(self, buyer, seller, buyer_val, costs_val):
        """
        Checks if buyer and seller
        can still participate in auction
        """

        if buyer.budget <= 0 or buyer.index >= (len(buyer_val) - 1):
            self.agents_out_auction.append(buyer)
            self.agents_in_auction.remove(buyer)
            buyer.active == False

        if seller.quantity == 0 or seller.index >= (len(costs_val) - 1):
            self.agents_out_auction.append(seller)
            self.agents_in_auction.remove(seller)
            seller.active == False

    def check_trade_agents(self, buyer, seller):
        """
        Checks if the two agents can trade with each other.
        (no trade can happen between two Kaplan agents)
        """

        return (seller.type == "seller" and buyer.budget
                >= seller.valuations[seller.index]
            and buyer.valuations[buyer.index]
                >= seller.valuations[seller.index] and not
                (buyer.name == "Kaplan" and seller.name == "Kaplan"))

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

                    if self.check_trade_agents(agent, other_agent):

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
        prices = [transaction["price"]
                  for transaction in self.data_transactions[period]]
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

        # reset max bid ans min ask as well
        self.max_bid = None
        self.min_ask = None

        for agent in self.agents_in_auction:
            if agent.type == "buyer":
                agent.budget = sum(redemptions)
                agent.quantity = 0
                agent.price = None
                agent.index = 0

            else:
                agent.budget = 0
                agent.quantity = len(costs)
                agent.price = None
                agent.index = 0
