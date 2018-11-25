"""The permission token enables to provide and then verify access to a
resource. There is one token per accessed resource. Users can require, exchange
and later use tokens representing access to the resource.

This token can be configured to give 3 different types of permissions:
- unrestricted access to an unlimited resource:
  Reusable permission, like a door pass, an admin right, etc...
- restricted access to an unlimited resource:
  Make 3 wishes, use 100 times an API for free, etc...
- restricted access to a limited resource:
  Eat 2 cookies, Get 4 seats at a concert, etc...

The type influences the side effect at the moment the token is used only.
"""

from pikciotok import base, context, events

_TOKEN_VERSION = "T1.0"

name = ''
"""The friendly name of the token"""
symbol = ''
"""The symbol of the token currency. Should be 3 or 4 characters long."""
_decimals = 0  # A permission cannot be split.
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
revoked = events.register("revoked", "user", "amount")
"""Fired when the authority transfers back some token from an user."""
access_granted = events.register("access_granted", "user")
"""Fired when the authority reckons that an user is allowed access."""
access_denied = events.register("access_denied", "user", "why")
"""Fired when the authority states that an user can't access"""


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

def transfer(to_address: str, amount: int) -> bool:
    """Execute a transfer from the sender to the specified address."""
    return base.transfer(balance_of, context.sender, to_address, amount)


def mint(amount: int) -> int:
    """Request tokens creation and add created amount to sender balance.
    Returns new total supply.
    """
    global total_supply
    _assert_is_authority(context.sender)
    total_supply = base.mint(balance_of, total_supply, context.sender, amount)
    return total_supply


def burn(amount: int) -> int:
    """Destroy tokens. Tokens are withdrawn from sender's account.
    Returns new total supply.
    """
    global total_supply
    _assert_is_authority(context.sender)
    total_supply = base.burn(balance_of, total_supply, context.sender, amount)
    return total_supply


def approve(to_address: str, amount: int) -> bool:
    """Allow specified address to spend/use some tokens from sender account.

    The approval is set to specified amount.
    """
    return base.approve(allowances, context.sender, to_address, amount)


def update_approve(to_address: str, delta_amount: int) -> int:
    """Updates the amount specified address is allowed to spend/use from
    sender account.

    The approval is incremented of the specified amount. Negative amounts
    decrease the approval.
    """
    return base.update_approve(allowances, context.sender, to_address,
                               delta_amount)


def transfer_from(from_address: str, to_address: str, amount: int) -> bool:
    """Executes a transfer on behalf of another address to specified recipient.

    Operation is only allowed if sender has sufficient allowance on the source
    account.
    """
    return base.transfer_from(balance_of, allowances, context.sender,
                              from_address, to_address, amount)


def init(supply: int, name_: str, symbol_: str):
    """Initialise this token with a new name, symbol and supply."""
    global total_supply, name, symbol, authority

    name, symbol = name_, symbol_
    balance_of[context.sender] = total_supply = (supply * 10 ** _decimals)
    authority = context.sender  # Creator becomes the authority.


def _assert_is_authority(address: str):
    """Raises an exception if provided address is not the authority"""
    if address != authority or not authority:
        raise ValueError("'{} is not the authority".format(address))


def _assert_is_not_frozen():
    """Raises an exception if permission tokens are currently frozen."""
    if is_frozen:
        raise ValueError("All tokens are currently frozen.")


# Global accessors

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


# Permission operations

def revoke(address: str, amount: int) -> int:
    """Removes specified amount (at max) of tokens from provided address.

    Tokens go back to the authority.

    :return: The final balance of the address.
    """
    _assert_is_authority(context.sender)
    amount = min(amount, get_balance(address))
    base.Balances(balance_of).transfer(context.sender, address, amount)
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
    success = True
    if permission_type == _PERM_TYPE_RETURNED:
        success = transfer(authority, 1)
    elif permission_type == _PERM_TYPE_CONSUMED:
        total_supply = burn(1)

    # Finally, raise appropriate event
    if success:
        access_granted(user=context.sender)
    else:
        access_denied(user=context.sender, why="Unknown error")

    return success
