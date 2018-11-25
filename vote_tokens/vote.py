"""The vote token allows to create poll on people or topics.

Before starting the vote, the vote place (token creator) defines a list of
candidates.

Once the vote is started, everyone except the candidate and the vote place
receives one and only one token.

Afterwards, people send their token to the candidate they like the most.
The vote is stopped when everyone has voted or when the vote place decides to
interrupt the vote.

Once the vote is stopped, everyone can see results, like the winner and the
participation.
"""
from datetime import datetime
from typing import List

from pikciotok import base, context, events


_TOKEN_VERSION = "T1.0"

name = ''
"""The friendly name of the token"""
symbol = ''
"""The symbol of the token currency. Should be 3 or 4 characters long."""
_decimals = 0  # A ballot cannot be split.
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


# Constants

_VOTE_STOP_NOT_YET = 0
"""The vote has not already been stopped."""

_VOTE_STOP_INTERRUPTED = 1
"""The vote has been stopped manually."""

_VOTE_STOP_COMPLETED = 2
"""The vote has been stopped because all voters made their mind."""


# Special attributes

base.missing_balance_means_zero = False
"""People must be chosen to enter a vote. More specifically, once a vote has
started. People can't join the vote anymore. In addition, once they have 
voted, voter must remain in the register. So there is a strict difference 
between having no balance and not being a voter."""

vote_place = ''
"""The referee of the vote. Dispatches ballots when the vote begins."""

candidates = []
# type: List[str]
"""The addresses of the candidates in the vote. This set must be defined when 
a vote starts."""

vote_beginning = 0
"""Timestamp of the beginning of the current vote, if any."""
vote_end = 0
"""Timestamp of the end of the current vote, if any."""
vote_stop_reason = 0

# Events
started = events.register("started", "voters_count", "candidates")
"""Fired when a vote starts."""
interrupted = events.register("interrupted", "winner", "duration")
"""Fired when a vote is manually stopped."""
completed = events.register("completed", "winner", "duration")
"""Fired when a all voters made their mind."""
voted = events.register("voted", "participation", "remaining_votes")
"""Fired when a ballot is put into a poll."""


# Initializer

def init(supply: int, name_: str, symbol_: str):
    """Initialise this token with a new name, symbol and supply."""
    global total_supply, name, symbol, vote_place

    name, symbol = name_, symbol_
    balance_of[context.sender] = total_supply = (supply * 10 ** _decimals)

    vote_place = context.sender  # The token creator becomes the referee.
    balance_of[vote_place] = total_supply


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
    _assert_no_vote_started()
    _assert_is_vote_place(context.sender)

    total_supply = base.mint(balance_of, total_supply, context.sender, amount)
    return total_supply


def burn(amount: int) -> int:
    """Destroy tokens. Tokens are withdrawn from sender's account.
    Returns new total supply.
    """
    global total_supply
    _assert_no_vote_started()
    _assert_is_vote_place(context.sender)

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


# Global accessors

def get_voters_count() -> int:
    """Gives the current number of voters in the poll."""
    return len(balance_of) - len(candidates) - 1  # Remove the vote place.


def get_candidates() -> List[str]:
    """Obtains the addresses of the current poll candidates."""
    return candidates


def get_candidates_count() -> int:
    """Obtains the current number of candidates."""
    return len(candidates)


def is_vote_in_progress() -> bool:
    """Indicates if a vote is currently in progress."""
    return vote_beginning > 0


def current_vote_beginning() -> float:
    """Returns the timestamp of the beginning of the current vote, if any."""
    return vote_beginning


def current_vote_end() -> float:
    """Returns the timestamp of the end of the current vote, if any."""
    return vote_end


def get_vote_stop_reason() -> int:
    """Tells why the current vote has been stopped, if it has been stopped."""
    return vote_stop_reason


# Poll management

def _assert_electoral_list_is_not_full():
    """Raises an exception if the current supply of tokens does not allow to
    add a new voter."""
    if get_voters_count() >= total_supply:
        raise RuntimeError('Electoral list is full')


def _assert_vote_started():
    """Raises an exception is no vote is currently in progress."""
    if vote_beginning == 0:
        raise RuntimeError("No vote currently in progress")


def _assert_no_vote_started():
    """Raises an exception is a vote is currently in progress."""
    if vote_beginning > 0:
        raise RuntimeError("A vote has already started")


def _assert_vote_not_stopped():
    """Raises an exception if a vote has already been stopped."""
    if vote_stop_reason > 0:
        raise RuntimeError('Current vote has already been stopped')


def _assert_vote_stopped():
    """Raises an exception if a vote has not already been stopped."""
    if vote_stop_reason == 0:
        raise RuntimeError('Current vote has not been stopped yet')


def _assert_is_candidate(address: str):
    """Raises an exception if provided address does not belong to a
    candidate."""
    if address not in candidates:
        raise ValueError("'{}' is not a candidate".format(address))


def _assert_is_vote_place(address: str):
    """Raises an exception if provided address is not the vote place"""
    if address != vote_place or not vote_place:
        raise ValueError("'{} is not the vote place".format(address))


def register_voter(address: str) -> int:
    """Registers provided voter so that they can take part in next vote.

    :returns: The new count of voters.
    """
    _assert_no_vote_started()
    _assert_electoral_list_is_not_full()
    balance_of[address] = 0
    return get_voters_count()


def strike_off_voter(address: str) -> int:
    """Removes a voter from the voting list.

    :returns: The new count of voters.
    """
    _assert_no_vote_started()
    if address in balance_of:
        del balance_of[address]
    return get_voters_count()


def add_candidate(address: str) -> int:
    """Adds a candidate to the next vote.

    :returns: The new count of candidates.
    """
    _assert_no_vote_started()

    _assert_electoral_list_is_not_full()
    balance_of[address] = 0
    candidates.append(address)
    return get_candidates_count()


def remove_candidate(address: str) -> int:
    """Removes a candidate from the next vote.

    :returns: The new count of candidates.
    """
    _assert_no_vote_started()
    _assert_is_candidate(address)
    _assert_electoral_list_is_not_full()
    del balance_of[address]
    candidates.remove(address)
    return get_candidates_count()


def start() -> bool:
    """Starts a new vote. Voters pool and candidates set are frozen."""
    global vote_beginning

    _assert_no_vote_started()
    vote_beginning = datetime.utcnow().timestamp()

    # Transfer one vote token to each voter.
    for address in balance_of:
        if address not in candidates and address != vote_place:
            base.transfer(balance_of, vote_place, address, 1)

    started(voters_count=get_voters_count(), candidates=candidates)
    return True


def interrupt() -> str:
    """Manually stops the current vote. Vote can't be resumed afterwards.

    :returns: The address of the winner.
    """
    global vote_stop_reason, vote_end
    _assert_vote_started()
    _assert_vote_not_stopped()
    _assert_is_vote_place(context.sender)

    vote_stop_reason = _VOTE_STOP_INTERRUPTED
    vote_end = datetime.utcnow().timestamp()
    interrupted(winner=get_winner(), duration=get_vote_duration())

    return get_winner()


def clear() -> bool:
    """Clears the current vote state.

    Timestamps are reset. candidate list is emptied. All tokens are transferred
    back to the vote place.
    """
    global vote_stop_reason, vote_end, vote_beginning, candidates

    vote_beginning = 0
    vote_end = 0
    vote_stop_reason = _VOTE_STOP_NOT_YET
    candidates = []

    for address in balance_of:
        balance_of[address] = 0
    balance_of[vote_place] = total_supply

    return True


def vote(address: str) -> bool:
    """Puts a ballot in provided candidate urn."""
    global vote_stop_reason, vote_end

    _assert_vote_started()
    _assert_vote_not_stopped()
    _assert_is_candidate(address)

    if not base.transfer(balance_of, context.sender, address, 1):
        return False

    voted(participation=get_participation(),
          remaining_votes=get_remaining_votes())

    # Check for vote termination
    if get_remaining_votes() == 0:
        vote_stop_reason = _VOTE_STOP_COMPLETED
        vote_end = datetime.utcnow().timestamp()
        completed(winner=get_winner(), duration=get_vote_duration())
    return True


# Poll info

def has_voted(address: str) -> bool:
    """Tells if voter has already made his mind."""
    return get_balance(address) > 0


def get_remaining_votes() -> int:
    """Obtains the number of voters who haven't made their mind yet."""
    _assert_vote_started()
    return get_voters_count() - sum(balance_of[c] for c in candidates)


def get_participation() -> float:
    """Obtains the participation score for the current vote."""
    return 1 - (get_remaining_votes() / get_voters_count())


def get_vote_duration() -> float:
    """Obtains the duration of the vote until now. The duration keeps
    increasing until the vote is stopped somehow.
    """
    _assert_vote_started()
    end = vote_end or datetime.utcnow().timestamp()
    return end - vote_beginning


def get_score(candidate: str) -> float:
    """Obtains the vote percentage for the provided candidate. Such result can
    only be queried once the vote has stopped.
    """
    _assert_vote_stopped()
    _assert_is_candidate(candidate)
    return balance_of[candidate] / get_voters_count()


def get_ranking() -> List[str]:
    """Obtains the complete ranking of all the candidates, by decreasing score
    order. Such result can only be queried once the vote has stopped.
    """
    _assert_vote_stopped()
    return list(sorted(candidates, reverse=True, key=lambda c: get_score(c)))


def get_winner() -> str:
    """Obtains the address of the winning candidate."""
    ranking = get_ranking()
    return ranking[0] if ranking else ''
