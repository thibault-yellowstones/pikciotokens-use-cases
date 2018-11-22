from typing import List, Dict

from pikciotok import base, context, events

_TOKEN_VERSION = "T1.0"

# Standard attributes

name = ''
symbol = ''
decimals = 0  # No decimals. Points can't be divided.
total_supply = 0
balance_of = {}

base.missing_balance_means_zero = False
"""We do not want to delete accounts of customers who have spent all of their 
points. So let's prevent that auto-removal by clearly stating that an empty 
account is not equal to a missing one."""

# Special attributes

bank_account = ''
"""The 'bank' account, getting the points when a client spends them.
This is an easy to check how many points have been spent.
"""
gift_catalog = {}
# type: Dict[str, int]
"""Contains a mapping of all the gifts that can be purchased using the loyalty 
points. Each name is mapped to a price. The case is simplified as we assume 
there is no limit on the quantity per gift.
"""

# Events
purchased = events.register("purchased", "gift", "by", "price")
"""The only event we are interested in is the purchase of a gift."""


def init(name_: str, symbol_: str, total_supply_: int):
    """Initialise this token with a new name, supply and symbol."""
    global name, symbol, bank_account, total_supply
    name = name_
    symbol = symbol_
    total_supply = total_supply_ * 10 ** decimals

    # It is assumed that the token initiator is "the bank".
    bank_account = context.sender


# Catalog management

def get_catalog_size() -> int:
    """Gets the current size of the catalog."""
    return len(gift_catalog)


def add_update_catalog(gifts: Dict[str, int]) -> int:
    """Adds or updates items in the catalog.

    :param gifts: Must be a dictionary mapping gift names to their price.
    :return: The new size of the catalog.
    """
    global gift_catalog
    gift_catalog.update(gifts)
    return get_catalog_size()


def remove_from_catalog(gift_names: List[str]) -> int:
    """Removes items from the catalog. If an item is already missing, its
    removal has no effect.

    :param gift_names: List of names to remove from the catalog.
    :return: The new size of the catalog.
    """
    global gift_catalog
    for gift_name in gift_names:
        if gift_name in gift_names:
            del gift_catalog[gift_name]
    return get_catalog_size()


# Global accessors

def get_total_spent() -> int:
    """Gives the total number of points spent by all customers."""
    return base.Balances(balance_of).get(bank_account)


def get_total_supply() -> int:
    """Gives the total number of points ever given to all customers. Some of
    those points might already be spent already.
    """
    return total_supply


# Accounts management

def get_balance(address: str) -> int:
    """Gives the current balance of the specified client's account"""
    return base.Balances(balance_of).get(address)


def grant(to_address: str, amount: int) -> int:
    """Gives points to provided customer. Points are created."""
    global total_supply

    total_supply = base.mint(balance_of, total_supply, to_address, amount)
    return total_supply


def purchase(gift_name: str) -> int:
    """Request a purchase on specified gift from sender.
    A purchase event is fired if the purchase is successful.

    :param gift_name: Name of the gift to buy.
    :return: The new balance of the customer.
    """
    if gift_name not in gift_catalog:
        raise KeyError("No such gift: '{}'".format(gift_name))
    price = gift_catalog[gift_name]
    if base.transfer(balance_of, context.sender, bank_account, price):
        purchased(gift=gift_name, by=context.sender, price=price)
    return get_balance(context.sender)
