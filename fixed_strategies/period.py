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
        self.suprlus = {}
        self.transactions = {}
        self.active_agents = []
        self.inactive_agents = []
        self.agents_out_auction = []
        self.max_bid = None
        self.min_ask = None
        self.max_trade = inf
        self.min_trade = -inf


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

            for active_agent in self.active_agents:
                if active_agent.price:
                    if active_agent.type == "seller" and agent.price >= active_agent.price:
                        possible_sellers.append(active_agent)

            return choice(possible_sellers)

        else:
            possible_buyers = []

            for active_agent in self.active_agents:
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


    def procces_transaction(self, buyer, seller, price, period, time_step):
        """
        Adjust quantity seller/buyer, index of valuations, surplus
        budget and keep track individual transaction prices
        returns transaction price
        """

        buyer.quantity += 1
        seller.quantity -= 1
        self.surplus += buyer.valuations[buyer.index] - seller.valuations[seller.index]
        buyer.index += 1
        seller.index += 1

        ## VANAF HIER DINGEN VERANDEREN ZIE FUNCTIE ERONDER
        self.transactions.append(price)
        buyer.profits.append(buyer.valuations[buyer.index] - price)
        seller.profits.append(buyer.bid - seller.valuation)
        buyer.bid = 1
        seller.bid = 200
        self.agents = [agent for agent in self.agents if agent not in (buyer, seller)]

    def add_info_transaction(self, price, surplus, period, time_step):
        """
        Keeps track of info of transactions per period
        (surplus, transaction prices)
        """
        pass
