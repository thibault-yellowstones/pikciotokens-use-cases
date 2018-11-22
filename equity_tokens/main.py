from pikciotok import context

import shares


def test_shares():
    # Let's create a new market share.
    context.sender = "Pikcio SA"
    shares.init(
        name_="Pikciotronics Ltd",
        symbol_="PKT",
        total_supply_=13000000
    )

    # Add another shareholder
    shares.transfer("John Doe", 1200000 * 10 ** shares.decimals)

    # Let's collect info now.
    print("John's shares: " + str(shares.get_shares("John Doe")))
    print("John's votes: " + str(shares.get_votes("John Doe")))
    print("John's weight: " + str(shares.get_weight("John Doe")))
    print("John's rights:\n- " + '\n- '.join(shares.get_rights("John Doe")))
    print("Is John majority ?: " + str(shares.is_majority("John Doe")))

    # Now let's change how vote works
    print()
    print("Changing vote policy to 'One person one vote'")
    print()
    shares.set_vote_mode(shares._VOTE_POLICY_OPOV)

    # And see how tables turn
    print("John's shares: " + str(shares.get_shares("John Doe")))
    print("John's votes: " + str(shares.get_votes("John Doe")))
    print("John's weight: " + str(shares.get_weight("John Doe")))
    print("John's rights:\n- " + '\n- '.join(shares.get_rights("John Doe")))
    print("Is John majority ?: " + str(shares.is_majority("John Doe")))


if __name__ == '__main__':
    test_shares()
