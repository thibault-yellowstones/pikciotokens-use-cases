from typing import List, Dict

from pikciotok import base, context, events

_TOKEN_VERSION = "T1.0"

# Standard attributes
name = ''
symbol = ''
decimals = 0        # No decimals. Points can't be divided.
initial_supply = 0  # No initial supply. Points are created on the fly.
total_supply = 0
balance_of = {}

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
purchased = events.register("purchased", "gift", "from", "price")
"""The only event we are interested in is the purchase of a gift."""


def init(_name: str, _symbol: str):
    """Initialise this token with a new name, and symbol."""
    global name, symbol, bank_account
    name = _name
    symbol = _symbol

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


# Accounts management

def get_balance(address: str) -> int:
    """Gives the current balance of the specified client's account"""
    return base.Balances(balance_of).get(address)


def get_total_spent_points() -> int:
    """Gives the total number of points spent by all customers."""
    return base.Balances(balance_of).get(bank_account)


def grant(to_address: str, amount: int) -> int:
    """Gives points to provided customer. Points are created."""
    global total_supply

    total_supply = base.mint(balance_of, total_supply, to_address, amount)
    return total_supply


def spend(amount: int) -> int:
    """Spends amount from the sender's account. Money goes to the bank."""


def mint(amount: int) -> int:
    """Request money creation and add created amount to sender balance.
    Returns new total supply.
    """
    global total_supply

    new_supply = base.mint(balance_of, total_supply, context.sender, amount)
    if new_supply != total_supply:
        minted(sender=context.sender, amount=amount, new_supply=new_supply)

    total_supply = new_supply
    return total_supply


def burn(amount: int) -> int:
    """Destroy money. Money is withdrawn from sender's account.
    Returns new total supply.
    """
    global total_supply

    new_supply = base.burn(balance_of, total_supply, context.sender, amount)
    if new_supply != total_supply:
        burnt(sender=context.sender, amount=amount, new_supply=new_supply)

    total_supply = new_supply
    return total_supply


def approve(to_address: str, amount: int) -> bool:
    """Allow specified address to spend provided amount from sender account.

    The approval is set to specified amount.
    """
    return base.approve(allowances, context.sender, to_address, amount)


def update_approve(to_address: str, delta_amount: int) -> int:
    """Allow specified address to spend more or less from sender account.

    The approval is incremented of the specified amount. Negative amounts
    decrease the approval.
    """
    return base.update_approve(allowances, context.sender, to_address,
                               delta_amount)


def transfer_from(from_address: str, to_address: str, amount: int) -> bool:
    """Require Transfer from another address to specified recipient. Operation
    is only allowed if sender has sufficient allowance on the source account.
    """
    if base.transfer_from(balance_of, allowances, context.sender, from_address,
                          to_address, amount):
        transferred(sender=from_address, recipient=total_supply, amount=amount)
        return True

    return False


def burn_from(from_address: str, amount: int) -> int:
    """Require Burn from another account. Operation is only allowed if sender
    has sufficient allowance on the source account.
    """
    global total_supply
    new_supply = base.burn_from(balance_of, allowances, total_supply,
                                context.sender, from_address, amount)
    if new_supply != total_supply:
        burnt(sender=context.sender, amount=amount, new_supply=new_supply)

    total_supply = new_supply
    return total_supply
