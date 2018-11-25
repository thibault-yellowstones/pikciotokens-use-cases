"""The test shows examples of the two uncommon cases of permissions described
in the token:
- restricted access to an unlimited resource (consumable permission)
- restricted access to a limited resource (returned permission)

The most common case of permanent access to an unlimited resource is easier
to understand (think of a door pass) and would not bring more light on how
to use the token.

This is not a unit test.
"""
from pikciotok import context

import permission


def test_consumable_permission():
    # Let's create a new permission:
    # Resource: Cookies in a jar
    # Access: Take a cookie
    # The resource is limited as the cookies won't return to the jar once eaten
    # by the kids.
    # The access is restricted as we only want kids to take that many cookies
    # at max.
    context.sender = "Pikciocolate"
    permission.init(
        supply=10,
        name_="Take a cookie in the jar",
        symbol_="CKE"
    )
    permission.set_permission_type(permission._PERM_TYPE_CONSUMED)

    # Kids love cookies.
    permission.transfer("Marie", 2)
    permission.transfer("Rebecca", 5)

    # Marie shows some gluttony sometimes
    context.sender = "Marie"
    permission.use_token()
    permission.use_token()
    permission.use_token()

    # Obviously there is less cookies left.
    print("Remaining in the jar: {}".format(permission.get_total_supply()))

    # Rebecca is nice. She shares one cookie with Marie
    context.sender = "Rebecca"
    permission.transfer("Marie", 1)

    context.sender = "Marie"
    permission.use_token()

    # Can't give more cookies than hat is left in the jar.
    context.sender = "Pikciocolate"
    try:
        permission.transfer("Antonio", 4)  # This will raise an exception.
    except ValueError as e:
        print(str(e))


def test_returned_permission():
    # Let's create a new permission:
    # Resource: Songs on a jukebox
    # Access: Play a song
    # The resource is unlimited as a song is still available on the jukebox
    # after it has been played.
    # The access is restricted as we only want customers to play songs if they
    # pay for them.
    # The supply is of importance even if the resource is unlimited, as
    # "the bar" has a limited amount of tokens to sell to customers and only
    # get tokens back when customers put them into the machine.
    context.sender = "Pikciomusic"
    permission.init(
        supply=10,
        name_="Put a song on the jukebox",
        symbol_="JUK"
    )
    permission.set_permission_type(permission._PERM_TYPE_RETURNED)

    # Marie buys a token to play a song and Rebecca two.
    permission.transfer("Marie", 1)
    permission.transfer("Rebecca", 2)

    # They play them
    context.sender = "Marie"
    permission.use_token()

    # The total supply is still the same
    print("Tokens available at the bar: {}".format(
        permission.get_balance('Pikciomusic'))
    )
    print("Remaining tokens: {}".format(permission.get_total_supply()))


if __name__ == '__main__':
    test_consumable_permission()
    test_returned_permission()
