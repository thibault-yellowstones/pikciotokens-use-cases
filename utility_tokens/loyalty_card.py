"""The loyalty card lets customers collect points on an account.

Customers can use their points to get items from a catalog defined by the owner
of the token.
"""

from typing import List, Dict

from pikciotok import base, context, events

_TOKEN_VERSION = "T1.0"

name = ''
"""The friendly name of the token"""
symbol = ''
"""The symbol of the token currency. Should be 3 or 4 characters long."""
_decimals = 0  # A point cannot be split.
"""Maximum number of decimals to express any amount of that token."""
total_supply = 0
"""The current amount of the token on the market, in case some has been minted 
or burnt."""
balance_of = {}
# type: dict
"""Maps customers addresses to their current balance."""
allowances = {}
# type: dict
"""Gives for each customer a map to the amount delegates are allowed to spend 
on their behalf."""

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
purchased = events.register("purchased", "gift", "by")
"""The only event we are interested in is the purchase of a gift."""


# Initializer

def init(supply: int, name_: str, symbol_: str):
    """Initialise this token with a new name, symbol and supply."""
    global total_supply, name, symbol, bank_account

    name, symbol = name_, symbol_
    balance_of[context.sender] = total_supply = (supply * 10 ** _decimals)

    # It is assumed that the token initiator is "the bank".
    bank_account = context.sender


# Properties

def get_name() -> str:
    """Gets token name."""
    return name


def get_symbol() -> str:
    """Gets token symbol."""
    return symbol


def get_decimals() -> int:
    """Gets the number of decimals of the token."""
    return _decimals


def get_total_supply() -> int:
    """Returns the current total supply for the token"""
    return total_supply


def get_balance(address: str) -> int:
    """Gives the current balance of the specified account."""
    return base.Balances(balance_of).get(address)


def get_allowance(allowed_address: str, on_address: str) -> int:
    """Gives the current allowance of allowed_address on on_address account."""
    return base.Allowances(allowances).get_one(on_address, allowed_address)


# Actions

def _assert_is_bank(address: str):
    """Raises an exception if provided address is not the bank."""
    if address != bank_account:
        raise ValueError("'{} is not the bank".format(address))


def transfer(to_address: str, amount: int) -> bool:
    """Execute a transfer from the sender to the specified address."""
    return base.transfer(balance_of, context.sender, to_address, amount)


def mint(amount: int) -> int:
    """Request tokens creation and add created amount to sender balance.
    Returns new total supply.
    """
    global total_supply

    _assert_is_bank(context.sender)
    total_supply = base.mint(balance_of, total_supply, context.sender, amount)
    return total_supply


def burn(amount: int) -> int:
    """Destroy tokens. Tokens are withdrawn from sender's account.
    Returns new total supply.
    """
    global total_supply

    _assert_is_bank(context.sender)
    total_supply = base.burn(balance_of, total_supply, context.sender, amount)
    return total_supply


def approve(to_address: str, amount: int) -> bool:
    """Allow specified address to spend/use some tokens from sender account.

    The approval is set to specified amount.
    """
    raise NotImplementedError()


def update_approve(to_address: str, delta_amount: int) -> int:
    """Updates the amount specified address is allowed to spend/use from
    sender account.

    The approval is incremented of the specified amount. Negative amounts
    decrease the approval.
    """
    raise NotImplementedError()


def transfer_from(from_address: str, to_address: str, amount: int) -> bool:
    """Executes a transfer on behalf of another address to specified recipient.

    Operation is only allowed if sender has sufficient allowance on the source
    account.
    """
    raise NotImplementedError()


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
    _assert_is_bank(context.sender)

    gift_catalog.update(gifts)
    return get_catalog_size()


def remove_from_catalog(gift_names: List[str]) -> int:
    """Removes items from the catalog. If an item is already missing, its
    removal has no effect.

    :param gift_names: List of names to remove from the catalog.
    :return: The new size of the catalog.
    """
    global gift_catalog
    _assert_is_bank(context.sender)

    for gift_name in gift_names:
        if gift_name in gift_names:
            del gift_catalog[gift_name]
    return get_catalog_size()


# Global accessors

def get_total_spent() -> int:
    """Gives the total number of points spent by all customers."""
    return base.Balances(balance_of).get(bank_account)


# Accounts management

def grant(to_address: str, amount: int) -> int:
    """Gives points to provided customer. Points are always created."""
    _assert_is_bank(context.sender)

    mint(amount)
    transfer(to_address, amount)
    return total_supply


def purchase(gift_name: str) -> int:
    """Request a purchase on specified gift from sender.
    A purchase event is fired if the purchase is successful.

    :param gift_name: Name of the gift to buy.
    :return: The new balance of the customer.
    """
    if gift_name not in gift_catalog:
        raise KeyError("No such gift: '{}'".format(gift_name))

    if transfer(bank_account, gift_catalog[gift_name]):
        purchased(gift=gift_name, by=context.sender)
    return get_balance(context.sender)
