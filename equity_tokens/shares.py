import itertools
from typing import List, Tuple

from pikciotok import base, context

# T1 Protocol

_TOKEN_VERSION = "T1.0"


name = ''
"""The friendly name of the token"""
symbol = ''
"""The symbol of the token currency. Should be 3 or 4 characters long."""
_decimals = base.MAX_TOKEN_DECIMALS
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


# Internal constants

# Shareholders weight during vote can follow several different policies, like
_VOTE_POLICY_ODOV = 1
"""One dollar one vote. Each shareholder weighs as much as its share of the
total assets."""
_VOTE_POLICY_OPOV = 2
"""One person one vote. Each shareholder weighs the same."""

# Following gives the rights of minority shareholders depending on their
# weight.
_SHAREHOLDERS_RIGHTS = {
    0.05: [
        "apply to court to prevent the conversion of a public company into a "
        "private company",
        "call a general meeting",
        "require the circulation of a written resolution to shareholders "
        "(in private companies)",
        "require the passing of a resolution at an annual general meeting "
        "(AGM) of a public company.",
    ],
    0.1: [
        "call for a poll vote on a resolution",
        "right to prevent a meeting being held on short notice "
        "(in private companies)."
    ],
    0.15: [
        "apply to the court to cancel a variation of class rights, provided "
        "such shareholders did not consent to, or vote in favour of, "
        "the variation.",
    ],
    0.25: [
        "prevent the passing of a special resolution"
    ]
}

base.missing_balance_means_zero = True
"""Once you give up your shares, you are no longer a shareholder (and are not
entitled to receive delegation, to vote, etc...) That means that we want to
automatically remove any empty account."""

# Special attributes

dividend = 0.0
"""percentage of retribution to the shareholders."""

vote_mode = _VOTE_POLICY_ODOV
"""Specifies how a shareholder weighs in an assembly vote."""


# Initializer

def init(supply: int, name_: str, symbol_: str):
    """Initialise this token with a new name, symbol and supply."""
    global total_supply, name, symbol

    name, symbol = name_, symbol_
    balance_of[context.sender] = total_supply = (supply * 10 ** _decimals)


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


# Actions

def transfer(to_address: str, amount: int) -> bool:
    """Execute a transfer from the sender to the specified address."""
    return base.transfer(balance_of, context.sender, to_address, amount)


def mint(amount: int) -> int:
    """Request tokens creation and add created amount to sender balance.
    Returns new total supply.
    """
    global total_supply
    total_supply = base.mint(balance_of, total_supply, context.sender, amount)
    return total_supply


def burn(amount: int) -> int:
    """Destroy tokens. Tokens are withdrawn from sender's account.
    Returns new total supply.
    """
    global total_supply
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


def get_balance(address: str) -> int:
    """Gives the current balance of the specified account."""
    return base.Balances(balance_of).get(address)


def get_allowance(allowed_address: str, on_address: str) -> int:
    """Gives the current allowance of allowed_address on on_address account."""
    return base.Allowances(allowances).get_one(on_address, allowed_address)


# Global accessors

def set_vote_mode(mode: int) -> int:
    """Changes the way shareholders weigh in a vote. See _VOTE_POLICY consts.

    :param mode: The new vote mode.
    :return: The old mode.
    """
    global vote_mode
    vote_mode, mode = mode, vote_mode
    return mode


def get_vote_mode() -> int:
    """Tells how shareholders weigh in a vote. See _VOTE_POLICY consts."""
    return vote_mode


def set_dividend(dividend_: float) -> float:
    """Updates the current dividend rate. Returns the old one."""
    global dividend
    dividend, dividend_ = dividend_, dividend
    return dividend_


def get_dividend() -> float:
    """Tells what is the current dividend rate."""
    return dividend


# Shares related info

def get_total_shareholders() -> int:
    """Gives the total number of shareholders."""
    return len(balance_of)


def is_shareholder(address: str = None) -> bool:
    """Returns true if the provided address is a shareholder.

    :param address: The address of the shareholder to get delegation. If none
        provided, uses the sender's delegate address.
    :return: True if the provided address is a shareholder.
    """
    address = address or context.sender
    return address in balance_of


def _assert_is_shareholder(address: str):
    """Checks that provided address is a shareholder. Raises an Exception
    otherwise.

    :param address: The address to check.
    """
    if not is_shareholder(address):
        raise ValueError("Address {} does not stand for a shareholder.".format(
            address
        ))


def is_delegating(address: str = None) -> bool:
    """Returns true if the provided address has entitled someone else with its
    share power.

    :param address: The address of the shareholder to check delegation for.
        If none provided, uses the sender's delegate address.
    :return: True if the address is currently delegating its share power.
    """
    _assert_is_shareholder(address)
    return base.Allowances(allowances).has_allowances(address)


def get_delegators(address: str = None) -> Tuple:
    """Returns a tuple of all the shareholders who delegate their power to
    provided address.

    :param address: The address of the shareholder to collect delegations for.
        If none provided, uses the sender's delegate address.
    :return: A tuple of all the addresses giving their power to the provided
        address.
    """
    _assert_is_shareholder(address)
    allowances_ex = base.Allowances(allowances)
    return tuple(
        account for account in balance_of
        if allowances_ex.is_allowed(account, address)
    )


def get_organic_shares(address: str = None) -> int:
    """Gives the number of shares of the specified shareholder. This does not
    include delegation.

    :param address: The address of the shareholder to get delegation. If none
        provided, uses the sender's delegate address.
    """
    _assert_is_shareholder(address)
    return base.Balances(balance_of).get(address)


def get_delegated_shares(address: str = None) -> int:
    """Gives the amount of shares delegated to the specified address.

    :param address: The address of the shareholder to get delegated amount.
        If none provided, uses the sender's delegate address.
    """
    return sum(get_organic_shares(addr) for addr in get_delegators(address))


def get_shares(address: str = None) -> int:
    """Gives the number of "effective" shares of the specified shareholder.
    This includes all delegations.

    :param address: The address of the shareholder to get effective shares for.
        If none provided, uses the sender's delegate address.
    """
    _assert_is_shareholder(address)
    return (
        get_delegated_shares(address)
        + get_organic_shares(address) if not is_delegating(address) else 0
    )


# Vote related info

def get_total_votes() -> int:
    """Obtains the total number of votes during an assembly. Depends on the
    current mode.
    """
    return total_supply if vote_mode == _VOTE_POLICY_ODOV else len(balance_of)


def get_organic_votes(address: str = None) -> int:
    """Obtains the number of votes a shareholder is entitled with. This does
    not include delegation.

    :param address: The address of the shareholder to get effective shares for.
        If none provided, uses the sender's delegate address.
    """
    return get_shares(address) if vote_mode == _VOTE_POLICY_ODOV else 1


def get_delegated_votes(address: str = None) -> int:
    """Gives the amount of votes delegated to the specified address.

    :param address: The address of the shareholder to get delegated amount.
        If none provided, uses the sender's delegate address.
    """
    return sum(get_organic_votes(addr) for addr in get_delegators(address))


def get_votes(address: str = None) -> int:
    """Gives the number of "effective" votes of the specified shareholder.
    This includes all delegations.

    :param address: The address of the shareholder to get effective votes for.
        If none provided, uses the sender's delegate address.
    """
    return (
        get_delegated_votes(address)
        + get_organic_votes(address) if not is_delegating(address) else 0
    )


# Weight related info

def get_organic_weight(address: str = None) -> float:
    """Obtains the share weight a shareholder is entitled with. This does
    not include delegation.

    :param address: The address of the shareholder to get effective weight for.
        If none provided, uses the sender's delegate address.
    """
    return get_organic_votes(address) / get_total_votes()


def get_delegated_weight(address: str = None) -> float:
    """Gives the share weight delegated to the specified address.

    :param address: The address of the shareholder to get delegated weight.
        If none provided, uses the sender's delegate address.
    """
    return get_delegated_votes(address) / get_total_votes()


def get_weight(address: str = None) -> float:
    """Gives the "effective" weight of the specified shareholder.
    This includes all delegations.

    :param address: The address of the shareholder to get effective weight for.
        If none provided, uses the sender's delegate address.
    """
    return get_votes(address) / get_total_votes()


def is_organic_majority(address: str = None) -> bool:
    """Tells if a shareholder is majority considering its organic weight.

    :param address: The address of the shareholder to check majority for.
        If none provided, uses the sender's delegate address.
    """
    return get_organic_weight(address) > 0.5


def is_majority(address: str = None) -> bool:
    """Tells if a shareholder is majority considering its total weight.

    :param address: The address of the shareholder to check majority for.
        If none provided, uses the sender's delegate address.
    """
    return get_weight(address) > 0.5


def _get_rights(percentage: float) -> List[str]:
    """Gives the list of rights of a shareholder with provided weight."""
    return list(itertools.chain.from_iterable(
        rights
        for min_weight, rights in _SHAREHOLDERS_RIGHTS.items()
        if percentage >= min_weight
    ))


def get_organic_rights(address: str = None) -> List[str]:
    """Collects and return the list of rights of the provided shareholder,
    considering its organic share weight.

    :param address: The address of the shareholder to check rights for.
        If none provided, uses the sender's delegate address.
    :return:
    """
    return _get_rights(get_organic_weight(address))


def get_rights(address: str = None) -> List[str]:
    """Collects and return the list of rights of the provided shareholder,
    considering its share weight (delegation included then).

    :param address: The address of the shareholder to check rights for.
        If none provided, uses the sender's delegate address.
    :return:
    """
    return _get_rights(get_weight(address))
