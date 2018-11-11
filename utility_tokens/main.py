from pikciotok import context

import loyalty_card


def main():
    # Let's create Luigi's loyalty card...
    loyalty_card.init(
        _name="Luigi's Pizzeria",
        _symbol="PIZZ"
    )

    # And add a few gifts to the catalog.
    loyalty_card.add_update_catalog({
        'Free Drink': 200,
        'Free Dessert': 300,
        'Free Pizza': 400,
    })

    # Say Mr Doe bought a 3 course meal. He won some points.
    loyalty_card.grant('john.doe@mymail.com', 300)

    # Mrs Bourgon get some points because of a current promotion in the menu.
    loyalty_card.grant('alice.Bourgon@mymail.com', 200)

    print("Total points ever granted: {}.".format(loyalty_card.total_supply))

    # If Mr Doe tries to get the free pizza, it won't work.
    try:
        context.sender = 'john.doe@mymail.com'
        loyalty_card.purchase('Free Pizza')
    except ValueError:
        print('John Failed to purchase the free pizza')

    # However he can have the dessert
    # This should fire an JSON event in the console.
    loyalty_card.purchase('Free Dessert')

    # Obviously, Mr Doe balance has been decreased.
    print("Remaining: " + str(loyalty_card.get_balance('john.doe@mymail.com')))


if __name__ == '__main__':
    main()
