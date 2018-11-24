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
allowances = {}
# type: Dict[str,Dict[str,int]]
"""Gives for each customer a map to the amount delegates are allowed to spend 
on their behalf."""

base.missing_balance_means_zero = True
"""Someone who has no token has no permission. Thus having no account is 
equivalent.
"""

# Constants

_PERM_TYPE_REUSABLE = 0
"""Once a token is given to a user, it can be used without restriction (until 
revoked).

This type of token works well with persistent permissions, as a door pass for
example. 
"""

_PERM_TYPE_RETURNED = 1
"""Permission tokens return to authority once used.

This is great for enabling temporary access to a resource.
"""

_PERM_TYPE_CONSUMED = 2
"""Permission token is burnt once used.

This fits cases where the number of resources is limited and can only be 
accessed once. For example, a ticket to a concert cannot be transferred to 
anyone else once the customer has entered the concert room. (limited seats,
unique usage).
"""

# Special attributes
authority = ''
"""The primary account which dispatches tokens."""

permission_type = _PERM_TYPE_REUSABLE
"""Defines the behaviour of the token once used."""

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
burnt = events.register("burn", "sender", "amount", "new_supply")
"""Fired when the authority destroyed some tokens."""
minted = events.register("mint", "sender", "amount", "new_supply")
"""Fired when the authority created some tokens."""


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
    """Gives the total number of permission tokens in circulation."""
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


def get_permission_type() -> int:
    """Returns a value indicating how a token behaves when used."""
    return permission_type


def freeze_permission(state: bool) -> bool:
    """Defines the token frozen state and returns the previous value."""
    _assert_is_authority(context.sender)
    global is_frozen
    state, is_frozen = is_frozen, state
    return state


def set_permission_type(typ: int) -> int:
    """Defines the token type and returns the previous value."""
    _assert_is_authority(context.sender)
    global permission_type
    typ, permission_type = permission_type, typ
    return typ


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


def mint(amount: int) -> int:
    """Request token creation and add created amount to sender balance.
    Returns new total supply.
    """
    global total_supply

    _assert_is_authority(context.sender)
    new_supply = base.mint(balance_of, total_supply, context.sender, amount)
    if new_supply != total_supply:
        minted(sender=context.sender, amount=amount, new_supply=new_supply)

    total_supply = new_supply
    return total_supply


def burn(amount: int) -> int:
    """Destroy tokens. tokens are withdrawn from sender's account.
    Returns new total supply.
    """
    global total_supply

    _assert_is_authority(context.sender)
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

# Permission operations

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


def use_token() -> bool:
    """Grants or deny access to the sender, depending on the tokens owned."""
    global total_supply

    try:
        # First check base permission requirements
        _assert_is_not_frozen()
        base.Balances(balance_of).require(context.sender, 1)
    except ValueError as e:
        access_denied(user=context.sender, why=str(e))
        return False

    # then handle consequences regarding token type.
    if permission_type == _PERM_TYPE_RETURNED:
        success = transfer(authority, 1)
    elif permission_type == _PERM_TYPE_CONSUMED:
        total_supply = base.burn(balance_of, total_supply, context.sender, 1)
        success = True
    else:
        success = True

    # Finally, raise appropriate event
    if success:
        access_granted(user=context.sender)
    else:
        access_denied(user=context.sender, why="Unknown error")

    return success
