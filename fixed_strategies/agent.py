# AGENT
# Julien Fer
# University of Amsterdam
#
# This script contains the functionality to computationally visualize either a
# ZI-U, ZI-C or Kaplan agent.

from random import randint

class Agent(object):
    """
    This is a representation of
    a financial agent (buyer/seller).
    """
    name = "ZI-U"

    def __init__(self, id, type, valuation, quantity, max):
        """
        Every agent is intiialized as buyer/seller
        with id, redemption/cost price and
        corresponding quantity and also a variable
        to keep track of individual transasction price.
        """

        self.id = id
        self.type = type
        self.valuation = valuation
        self.quantity = quantity
        self.bid = max
        self.profits = []

    def __str__(self):
        """
        Prints type, id, value and quantity of agent
        """
        return f"This agent is of the type {self.type} with id: {self.id} and " \
                f"has preferences price: {self.value} and quantity: {self.quantity}"

    def offer_price(self, price):
        """
        Random offer strategy of ZI-U trader
        """
        if self.type == "buyer":
            bid = randint(price, 200)
            self.bid = bid
            return bid

        elif self.type == "seller":
            bid = randint(1, price)
            self.bid = bid
            return bid
        else:
            return 0

class Agent_C(Agent):
    """
    Representation of a ZI-C agent
    """

    name = "ZI-C"

    def offer_price(self, bid):
        """
        Random offer strategy for a ZI-C agent
        """

        if self.type == "buyer" and bid <= self.valuation:
            bid =  randint(bid, self.valuation)
            self.bid = bid
            return bid
        elif self.type == "seller" and bid >= self.valuation:
            bid = randint(self.valuation, bid)
            self.bid = bid
            return bid

        return 0
