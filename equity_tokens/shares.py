import itertools
from typing import List, Dict, Tuple

from pikciotok import base, context, events

_TOKEN_VERSION = "T1.0"

# Internal constants

# Shareholders weight during vote can follow several different policies, like
_VOTE_POLICY_ODOV = 1
"""One dollar one vote. Each shareholder weighs as much as its share of the
total assets."""
_VOTE_POLICY_OPOV = 2
"""One person one vote. Each shareholder weighs the same."""

# Following gives the rights of minority shareholders dependending on their
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

# Standard attributes

name = ''
symbol = ''
decimals = 3
total_supply = 0
balance_of = {}

base.missing_balance_means_zero = True
"""Once you give up your shares, you are no longer a shareholder (and are not
entitled to receive delegation, to vote, etc...) That means that we want to
automatically remove any empty account."""

# Special attributes

dividend = 0.0
"""percentage of retribution to the shareholders."""

vote_mode = _VOTE_POLICY_ODOV
"""Specifies how a shareholder weighs in an assembly vote."""

delegations = {}
# type: Dict[str,str]
"""Gives for a shareholder an other shareholder who holds its voting power."""

# Events
transferred = events.register("transfer", "sender", "recipient", "amount")
"""Fired when a shareholder transfer shares to another shareholder."""


def init(name_: str, symbol_: str, supply: int):
    """Initialise this token with a new name, symbol and vote mode."""
    global name, symbol, vote_mode, total_supply
    name = name_
    symbol = symbol_
    total_supply = supply * 10 ** decimals
    balance_of[context.sender] = total_supply


# Currency and rights transfers

def transfer(to_address: str, amount: int) -> bool:
    """Execute a transfer of shares from the sender to another shareholder."""
    sender = context.sender
    if base.transfer(balance_of, sender, to_address, amount):
        transferred(sender=sender, recipient=total_supply, amount=amount)
        return True
    return False


def set_delegate(to_address: str) -> str:
    """Allow specified address to vote in lieu of the sender.

    :return: The previous delegation or empty string if none
    """
    if not to_address:
        raise ValueError('Delegate address cannot be falsy while granting '
                         'delegation.')
    previous_delegate = get_delegate()
    delegations[context.sender] = to_address
    return previous_delegate


def remove_delegate() -> str:
    """Removes the delegation of the current user.

    :return: The previous delegation or empty string if none
    """
    previous_delegate = get_delegate()
    if previous_delegate:
        del delegations[context.sender]
    return previous_delegate


def get_delegate(address: str = None) -> str:
    """Obtains the current delegate of the provided shareholder.

    :param address: The address of the shareholder to get delegation. If none
        provided, returns the sender's delegate address.

    :return: The address of the delegate, or empty string if none.
    """
    return delegations.get(address or context.sender, '')


# Global accessors

def set_vote_mode(vmode: int) -> int:
    """Changes the way shareholders weigh in a vote. See _VOTE_POLICY consts.

    :param vmode: The new vote mode.
    :return: The old mode.
    """
    global vote_mode
    vote_mode, vmode = vmode, vote_mode
    return vmode


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


def get_total_shares() -> int:
    """Gives the total number of shares."""
    return total_supply


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
    return bool(get_delegate(address))


def get_delegators(address: str = None) -> Tuple:
    """Returns a tuple of all the shareholders who delegate their power to
    provided address.

    :param address: The address of the shareholder to collect delegations for.
        If none provided, uses the sender's delegate address.
    :return: A tuple of all the addresses giving their power to the provided
        address.
    """
    _assert_is_shareholder(address)
    return tuple(addr for addr in delegations if delegations[addr] == address)


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
