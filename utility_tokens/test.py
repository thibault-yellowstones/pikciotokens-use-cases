"""The test shows how one can create a gift catalog, dispatch points and then
let customers use their point to get those gifts.

This is not a unit test.
"""
from pikciotok import context

import loyalty_card


def test_loyalty_card():
    # Let's create a loyalty card...
    loyalty_card.init(
        supply=0,  # Created on the fly. There is no supply of points.
        name_="Pikzeria",
        symbol_="PIKZ"
    )

    # And add a few gifts to the catalog.
    loyalty_card.add_update_catalog({
        'Free Drink': 200,
        'Free Dessert': 300,
        'Free Pizza': 400,
    })

    # Say Mr Doe bought a 3 course meal. He won some points.
    loyalty_card.grant('john.doe@mymail.com', 350)

    # Mrs Bourgon get some points because of a current promotion in the menu.
    loyalty_card.grant('alice.bourgon@mymail.com', 220)

    print("Total points ever granted: {}.".format(loyalty_card.total_supply))

    # If Mr Doe tries to get the free pizza, it won't work.
    try:
        context.sender = 'john.doe@mymail.com'
        loyalty_card.purchase('Free Pizza')
    except ValueError as e:
        print('John Failed to purchase the free pizza: ' + str(e))

    # However he can have the dessert
    # This should fire an JSON event in the console.
    loyalty_card.purchase('Free Dessert')

    # Obviously, Mr Doe balance has been decreased.
    new_balance = loyalty_card.get_balance('john.doe@mymail.com')
    print("Doe's balance: " + str(new_balance))

    # Alice can have the free drink.
    context.sender = 'alice.bourgon@mymail.com'
    loyalty_card.purchase('Free Drink')

    # We can track how many points have been spent.
    print('Total spent by everyone: {}'.format(loyalty_card.get_total_spent()))


if __name__ == '__main__':
    test_loyalty_card()
