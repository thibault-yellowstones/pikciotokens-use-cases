"""The test shows all the attributes that can be deduced from simply defining
rules and transferring a particular amount to a shareholder.

This is not a unit test.
"""

# We need to override the context sender to mimic a call from a particular
# account.
from pikciotok import context

import shares


def test_shares():
    # Let's create a new market share.
    context.sender = "Pikcio SA"
    shares.init(
        supply=13000000,
        name_="Pikciotronics Ltd",
        symbol_="PKT"
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
    print("\nChanging vote policy to 'One person one vote'\n")
    shares.set_vote_mode(shares._VOTE_POLICY_OPOV)

    # And see how tables turn
    print("John's shares: " + str(shares.get_shares("John Doe")))
    print("John's votes: " + str(shares.get_votes("John Doe")))
    print("John's weight: " + str(shares.get_weight("John Doe")))
    print("John's rights:\n- " + '\n- '.join(shares.get_rights("John Doe")))
    print("Is John majority ?: " + str(shares.is_majority("John Doe")))


if __name__ == '__main__':
    test_shares()
