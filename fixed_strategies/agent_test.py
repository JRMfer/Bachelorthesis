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

    def __init__(self, id, type, valuations):
        """
        Every agent is intiialized as buyer/seller
        with id, redemption/cost price and
        corresponding quantity and also a variable
        to keep track of individual transasction price.
        """

        self.id = id
        self.type = type
        self.valuations = valuations
        self.budget = self.set_budget(valuations)
        self.quantity = self.set_quantity(valuations)
        self.price = None
        self.active = True
        self.index = 0
        self.profits = {}
        self.transactions = {}
        self.time = {}

    def __str__(self):
        """
        Prints type, id, value and quantity of agent
        """

        return f"ID: {self.id} \nAgent: {self.name} \nType: {self.type} \n Price: {self.price}"

    def set_budget(self, valuations):
        """
        Set budget buyer to the sum of their redemptions
        and set budget seller to 0
        """

        if self.type == "buyer":
            return sum(valuations)
        elif self.type == "seller":
            return 0

    def set_quantity(self, valuations):
        """
        Set right quantity for buyer or seller
        """

        if self.type == "buyer":
            return 0
        elif self.type == "seller":
            return len(valuations)

    def offer_price(self, best_bid, best_ask):
        """
        Random offer strategy of ZI-U trader
        with possibility for NYSE rule
        """

        if not best_bid:
            best_bid = 1

        if not best_ask:
            best_ask = 400

        if self.type == "buyer":
            bid = randint(best_bid, 200)
            self.price = bid
            return bid

        elif self.type == "seller":
            bid = randint(1, best_ask)
            self.price = bid
            return bid

    def add_info_transaction(self, period, time_step, price, profit):
        """
        Keep track of individual transactions, surplus, with corresponding
        period and time step
        """

        if period in self.transactions:
            self.transactions[period].append(price)
            self.profits[period].append(profit)
            self.time[period].append(time_step)

        else:
            self.transactions[period] = []
            self.profits[period] = []
            self.time[period] = []
            self.transactions[period].append(price)
            self.profits[period].append(profit)
            self.time[period].append(time_step)



class Agent_C(Agent):
    """
    Representation of a ZI-C agent
    """

    name = "ZI-C"

    def offer_price(self, best_bid, best_ask):
        """
        Random offer strategy for a ZI-C agent
        """

        if not best_bid:
            best_bid = 1

        if not best_ask:
            best_ask = 400

        if self.type == "buyer" and best_bid <= self.valuations[self.index]:
            bid = randint(best_bid, self.valuations[self.index])
            self.price = bid
            return bid
        elif self.type == "seller" and best_ask >= self.valuations[self.index]:
            ask = randint(self.valuations[self.index], best_ask)
            self.price = ask
            return ask


    def check_activity(self, best_bid, best_ask):

        if self.type == "buyer":
            if not best_bid:
                return True
            return best_bid < self.valuations[self.index]
        elif self.type == "seller":
            if not best_ask:
                return True
            return best_ask > self.valuations[self.index]


class Agent_K(Agent):
    """
    Reprensentation of a Kaplan agent
    """

    name = "Kaplan"

    def __init__(self, id, type, valuations, time_frac, spread_ratio, profit_perc):
        super().__init__(id, type, valuations)
        self.time_frac = time_frac
        self.spread_ratio = spread_ratio
        self.profit_perc = profit_perc

    def offer_price(self, best_bid, best_ask):
        """
        Bidding strategie is pretty straightforward:
        it will shout the best ask/bid
        """

        # if best_ask == None:
        #     best_ask = best_bid + 1
        #
        # if best_bid == None:
        #     best_bid =


        if self.type == "buyer":
            self.price = best_ask
            return best_ask
        elif self.type == "seller":
            self.price = best_bid
            return best_bid

    def check_valuation(self, max_bid, min_ask):
        """
        Checks if outstanding ask/bid is
        lower/higher or equal than own redemption/cost
        """

        if self.type == "buyer":
            return self.valuations[self.index] >= min_ask

        elif self.type == "seller":
            return self.valuations[self.index] <= max_bid


    def check_time(self, time_step, total_time_steps):
        return ((total_time_steps - time_step) / total_time_steps) < self.time_frac

    def check_best_trade(self, best_bid, best_ask, previous_min_trade, previous_max_trade):
        """
        Checks if best ask/bid is
        less/greater than min/max
        trade price previous period
        (depends on market side of trader)
        """
        #
        # if previous_min_trade == -inf and self.type == "buyer":
        #     return True
        # elif previous_max_trade == inf and self.type == "seller":
        #     return True

        if self.type == "buyer" and best_ask:
            return best_ask < previous_min_trade
        elif self.type == "seller" and best_bid:
            return best_bid > previous_max_trade

        return False

    def check_worst_trade(self, best_bid, best_ask, previous_min_trade, previous_max_trade):

        if self.type == "buyer" and best_ask:
            return best_ask < previous_max_trade
        elif self.type == "seller" and best_bid:
            return best_bid > previous_min_trade

        return False

    def check_spread(self, best_bid, best_ask):

        if self.type == "buyer" and best_ask and best_bid:
            return ((best_ask - best_bid) / best_ask) < self.spread_ratio
        elif self.type == "seller" and best_ask and best_bid:
            return ((best_ask - best_bid) / best_bid) < self.spread_ratio

        return False

    def check_exp_profit(self, best_bid, best_ask):
        """
        Calculates expected profit Kaplan agent
        given best bid/ask depending on buyer/seller
        """

        # ratio best profit/loss on cost/redemotion must be greater than perc
        if self.type == "buyer" and best_ask:
            return (((self.valuations[self.index] - best_ask) /
                    self.valuations[self.index]) > self.profit_perc)
        elif self.type == "seller" and best_bid:
            return (((best_bid - self.valuations[self.index]) /
                    self.valuations[self.index]) > self.profit_perc)

        return False

    def check_spread_profit(self, best_bid, best_ask, previous_min_trade,
                                previous_max_trade):
        """
        Checks if the bid-ask spread is small enough
        and if the expected profit is juicy enough
        """

        return (self.check_worst_trade(best_bid, best_ask, previous_min_trade, previous_max_trade) and
                self.check_spread(best_bid, best_ask) and
                self.check_exp_profit(best_bid, best_ask))

    def check_activity(self, time_step, total_time_steps, best_bid,
            best_ask, previous_min_trade, previous_max_trade):


        if self.type == "buyer" and not best_ask:
            return False
        elif self.type == "seller" and not best_bid:
            return False

        return ((self.check_time(time_step, total_time_steps)
                or self.check_best_trade(best_bid, best_ask, previous_min_trade,
                                            previous_max_trade)
                or self.check_spread_profit(best_bid, best_ask, previous_min_trade,
                                            previous_max_trade))
                and self.check_valuation(best_bid, best_ask))

if __name__ == "__main__":

    kaplan = Agent_K(1, "buyer", [260, 250], 0.1, 0.1, 0.02)
