from typing import Dict

from pikciotok import base, context, events

_TOKEN_VERSION = "T1.0"

# Standard attributes

name = ''
symbol = ''
decimals = 0  # No decimals. Permissions cannot be divided.
total_supply = 0
balance_of = {}
# type: Dict[str,int]

base.missing_balance_means_zero = True
"""Someone who has no token has no permission. Thus having no account is 
equivalent.
"""

# Special attributes
authority = ''
"""The primary account which dispatches tokens."""

is_ephemeral = False
"""A consumable permission token returns to the authority when it is used"""

is_frozen = False
"""If True, all permissions are frozen and no one can access."""

# Events
allowed = events.register("allowed", "user", "amount")
"""Fired when the authority transfers tokens to an user."""
revoked = events.register("revoked", "user", "amount")
"""Fired when the authority transfers back some token from an user."""
access_granted = events.register("access_granted", "user")
"""Fired when the authority reckons that an user is allowed access."""
access_denied = events.register("access_denied", "user", "why")
"""Fired when the authority states that an user can't access"""
transferred = events.register("transferred", "sender", "recipient", "amount")
"""Fired when an user transfers tokens to another user."""


def init(name_: str, symbol_: str, total_supply_):
    """Initialise this token with a new name, symbol and supply."""
    global name, symbol, total_supply, authority
    name = name_
    symbol = symbol_
    total_supply = total_supply_ * 10 ** decimals

    authority = context.sender  # Creator becomes the authority.
    balance_of[authority] = total_supply


def _assert_is_authority(address: str):
    """Raises an exception if provided address is not the authority"""
    if address != authority or not authority:
        raise ValueError("'{} is not the authority".format(address))


def _assert_is_not_frozen():
    """Raises an exception if permission tokens are currently frozen."""
    if is_frozen:
        raise ValueError("All tokens are currently frozen.")


# Global accessors

def get_total_supply() -> int:
    """Gives the total number of permission tokens emitted."""
    return total_supply


def allowed_users_count() -> int:
    """Gives the current number of users with at least one token."""
    return len(balance_of) - 1  # Minus the authority.


def allowed_tokens_count() -> int:
    """Gives the total number of tokens given to users at the moment."""
    return total_supply - get_balance(authority)


def is_permission_frozen() -> bool:
    """Tells if all allowed tokens are currently frozen and can't be used."""
    return is_frozen


def is_token_ephemeral() -> bool:
    """Tells if tokens get consumed when used."""
    return is_ephemeral


def freeze_permission(state: bool) -> bool:
    """Defines the token frozen state and returns the previous value."""
    _assert_is_authority(context.sender)
    global is_frozen
    state, is_frozen = is_frozen, state
    return state


def set_token_ephemeral(state: bool) -> bool:
    """Defines the token ephemeral attribute and returns the previous value."""
    _assert_is_authority(context.sender)
    global is_ephemeral
    state, is_ephemeral = is_ephemeral, state
    return state


# Tokens management

def get_balance(address: str) -> int:
    """Gives the current balance of the specified user"""
    return base.Balances(balance_of).get(address)


def transfer(to_address: str, amount: int) -> bool:
    """Execute a transfer of tokens from the sender to another user."""
    sender = context.sender
    if base.transfer(balance_of, sender, to_address, amount):
        if sender == authority:
            allowed(user=to_address, amount=amount)
        else:
            transferred(sender=sender, recipient=total_supply, amount=amount)
        return True
    return False


def revoke(address: str, amount: int) -> int:
    """Removes specified amount (at max) of tokens from provided address.

    Tokens go back to the authority.

    :return: The final balance of the address.
    """
    _assert_is_authority(context.sender)

    amount = min(amount, get_balance(address))
    if base.transfer(balance_of, address, authority, amount):
        revoked(user=address, amount=amount)
    return base.Balances(balance_of).get(address)


def require_access() -> bool:
    """Grants or deny access to the sender, depending on the tokens owned."""
    try:
        _assert_is_not_frozen()
        base.Balances(balance_of).require(context.sender, 1)
    except ValueError as e:
        access_denied(user=context.sender, why=str(e))
        return False

    if not is_ephemeral or transfer(authority, 1):
        access_granted(user=context.sender)
        return True

    access_denied(user=context.sender, why="Unknown error")
    return False
