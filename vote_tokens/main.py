from random import Random

from pikciotok import context

import vote


def test_vote():
    # Let's create a new vote...
    voters_count = 10000
    context.sender = 'vote place'
    vote.init(
        name_="What is the best way to eat strawberries?",
        symbol_="STBY",
        total_supply_=voters_count
    )
    print("Today's question is: {}".format(vote.name))

    # Add a few options...
    candidates = (
        "With a friend at Pikcio.",
        "With Yogurt and sugar.",
        "In a tart, with a scoop of ice cream.",
        "As jam on a toast."
    )
    for candidate in candidates:
        vote.add_candidate(candidate)
    print("Candidates are:\n{}\n".format('\n'.join(candidates)))

    # And loads of voters.
    for i in range(voters_count):
        vote.register_voter(str(i))
    print("There are {} voters.".format(vote.get_voters_count()))

    # Start the vote.
    vote.start()
    rand = Random()

    # Each voter may now hav an opinion.
    for i in range(voters_count):
        # About 70% of the population cares to answer.
        if rand.randint(0, 9) > 2:
            context.sender = str(i)
            vote.vote(rand.choice(candidates))

    # Time to stop the poll and collect results.
    context.sender = 'vote place'
    vote.interrupt()

    print('Duration was: ' + str(vote.get_vote_duration()))
    print('Participation was: {:.2f}%'.format(vote.get_participation() * 100))
    print('Winner was: ' + vote.get_winner())


if __name__ == '__main__':
    test_vote()
