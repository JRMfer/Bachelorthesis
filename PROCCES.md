# Journal of Programming Procces
This document represents a day-by-day journal of every step of progress made
in the development of the CDA. I have decided to first implement agents with
fixed strategies (ZI-C and Kapland) in the CDA. After this, it will be a small
step towards agents that are capable to switch between these two strategies.
All the work is done in Python 3.7.

## Day 1
First implemented the different agents as Objects.

The ZI-U agent represents the Parent Object. It has as arguments a unique id,
the market side it will act on (buyer or seller) and a list of cost or
redemption values. Furthermore it will contain directly after initialization
attributes to keep track of their budget, quantity, price of shout, index for
valuations, profit, transactions, and according time steps.

This is the same for a ZI-C agent. the only difference is in
the way they shout an offer and in contrast to a ZI-U agent a ZI-C agent is not
always willing to shout a bid ot offer. So, the ZI-C agent also will have a
function to check if it is still active (willing to shout).

The Kaplan agents contained more work.
