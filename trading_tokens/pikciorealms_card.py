"""In the PikcioRealms world, each token describes a card that is part of a
trading card game.

Characteristics are set once for all just after the token creation. Each card
then has its own supply and characteristic embedded in the token.

The cards can be exchanged in order to create powerful combinations, depending
on the actual rules of this fictive trading card game.

This kind of token is particular, as it represents only a part of a greater
system involving several tokens.
"""

from pikciotok import base, context

_TOKEN_VERSION = "T1.0"

name = ''
"""The friendly name of the token"""
symbol = ''
"""The symbol of the token currency. Should be 3 or 4 characters long."""
_decimals = 0  # A card cannot be split.
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

craftsman = ''
"""Address of the craftsman of the card, emitting this token."""

# Card characteristics
# In the magical world of PikcioRealms, characters have
# A race, like Human or Ork,
race = ''
# An element, that gives them special powers, like Earth, Wind or Fire
element = ''
# A general level, to state how strong they are.
level = 0
# The effect of the card.
effect = ''
# Game characteristics
attack = 0
defense = 0
stamina = 0
magic = 0


# Initializer
# The initializer is partial here. init_card needs to be called afterwards.

def init(supply: int, name_: str, symbol_: str):
    """Initialise this token with a new name, symbol and supply."""
    global total_supply, name, symbol, craftsman

    name, symbol = name_, symbol_
    balance_of[context.sender] = total_supply = (supply * 10 ** _decimals)
    craftsman = context.sender


def _assert_is_craftsman(address: str):
    """Raises an exception if provided address is not the bank."""
    if address != craftsman:
        raise ValueError("'{} is not the craftsman".format(address))


def _assert_characteristics_set():
    """Raises an exception if the card details have not been set yet."""
    if not race:
        raise RuntimeError("Token characteristics have not been set yet.")


def _assert_characteristics_not_set():
    """Raises an exception if the card details have already been set."""
    if race:
        raise RuntimeError("Token characteristics have already been set yet.")


def init_card(race_: str, element_: str, level_: int, effect_: str,
              attack_: int, defense_: int, stamina_: 0, magic_: 0):
    """Puts a meaning on the tokens emitted.

    All characteristics of the card are set. Please note that this method can
    only be called once. Afterwards the card details are set forever.
    """
    _assert_is_craftsman(context.sender)
    _assert_characteristics_not_set()

    global race, element, level, effect, attack, defense, stamina, magic

    race = race_
    element = element_
    level = level_
    effect = effect_
    attack = attack_
    defense = defense_
    stamina = stamina_
    magic = magic_


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


def get_race() -> str:
    """Gets the card race."""
    return race


def get_element() -> str:
    """Gets the card element."""
    return element


def get_level() -> int:
    """Gets the card level."""
    return level


def get_effect() -> str:
    """Gets the card effect."""
    return effect


def get_attack() -> int:
    """Gets the card attack."""
    return attack


def get_defense() -> int:
    """Gets the card defense."""
    return defense


def get_stamina() -> int:
    """Gets the card stamina."""
    return stamina


def get_magic() -> int:
    """Gets the card magic."""
    return magic


def get_rarity() -> str:
    """Rarity is an indicator driven by total supply of the card"""
    return (
        "common" if total_supply > 20000 else
        "uncommon" if total_supply > 10000 else
        "rare" if total_supply > 5000 else
        "legendary"
    )


def get_characteristics() -> dict:
    """Returns a dictionary describing this card."""
    return {
        attribute: globals()["get_" + attribute]()
        for attribute in ("name", "race", "element", "level", "effect",
                          "attack", "defense", "stamina", "magic", "rarity")
    }

# Actions


def transfer(to_address: str, amount: int) -> bool:
    """Execute a transfer from the sender to the specified address."""
    return base.transfer(balance_of, context.sender, to_address, amount)


def mint(amount: int) -> int:
    """Request tokens creation and add created amount to sender balance.
    Returns new total supply.
    """
    global total_supply
    _assert_is_craftsman(context.sender)
    total_supply = base.mint(balance_of, total_supply, context.sender, amount)
    return total_supply


def burn(amount: int) -> int:
    """Destroy tokens. Tokens are withdrawn from sender's account.
    Returns new total supply.
    """
    global total_supply
    # A player might decide to destroy a card, if he possesses it, so no:
    # _assert_is_craftsman(context.sender)
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
