"""Unfortunately there is not much to test with the trading card. Because each
token is a card, there is no point in trading one with the same one.

That kind of token needs the help of another piece of code to handle the
trading of cards.

This is not a unit test.
"""

from pikciotok import context

import pikciorealms_card


def test_pikciorealms_card():
    # Let's create a new card. This card could then be bought/exchanged by
    # users in exchange of another card.
    context.sender = "PikcioRealms"
    pikciorealms_card.init(
        supply=4500,
        name_="The Mighty PikPik",
        symbol_="PKR-0001"
    )
    pikciorealms_card.init_card(
        race_='Bird',
        element_='Fire',
        level_=75,
        effect_="When it attacks, discard one card from your opponent's hand.",
        attack_=250,
        defense_=100,
        stamina_=800,
        magic_=750
    )

    # Check card details
    print(pikciorealms_card.get_characteristics())


if __name__ == '__main__':
    test_pikciorealms_card()
