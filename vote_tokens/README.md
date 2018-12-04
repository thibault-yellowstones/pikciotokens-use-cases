# Vote token

## Type 
**Utility token (SEC) / Utility token (FINMA)**

> Provides access to the goods & services that a project offers.

https://medium.com

## Description
The vote token allows to create poll on people or topics.

Before starting the vote, the vote place (token creator) defines a list of
candidates.

Once the vote is started, everyone except the candidate and the vote place
receives one and only one token.

Afterwards, people send their token to the candidate they like the most.
The vote is stopped when everyone has voted or when the vote place decides to
interrupt the vote.

Once the vote is stopped, everyone can see results, like the winner and the
participation.

## Characteristics

This token has following properties.

### Decimals 
A ballot cannot be split. Thus, it has no decimals.

### Roles
There are 3 roles in this token:
- **The vote place** is the emitter of the token. It is the one who starts and
stops polls and sets up the candidates
- **The candidates** are special accounts that can't take part to the vote but only 
act as recipients of regular voters
- **The voters** are the remaining accounts. They transfer their token to candidates
to express themselves on a poll. 

### Supply management
The total supply limits the maximum number of concurrent voters. It can be changed
by the vote place and only before a poll has started or after it has ended.

Because the number of voters is known and frozen when a poll starts, the 
implementation could also be adapted to mint/burn difference between the number
of vote tokens required and the current total supply. 

### Transfer conditions
Trading votes is not really ethic... Thus bare transfers are forbidden.
One has to use **vote** endpoint or **vote_from** to transfer its vote(s).

### Allowances conditions
No specific restrictions on allowances.

This will let voters vote by proxy to their friends and family.

### Others

The vote system implemented is simple: 1 ballot per voter, winner is the one 
with most voices.

It could be extended to add more complicated mechanisms, like several ballots 
per voter or a different rule to determine the winner.
