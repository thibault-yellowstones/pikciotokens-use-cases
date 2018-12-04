# Loyalty Card Token

## Type 
**Utility token (SEC) / Utility token (FINMA)**

> Provides access to the goods & services that a project offers.

https://medium.com

## Description
The loyalty card lets customers collect points on an account.

Customers can use their points to get items from a catalog defined by the owner
of the token.

## Characteristics

This token has following properties.

### Decimals
A point is atomic and cannot be split. Thus, it has no decimals.

### Roles
The token creator is called the **bank**.

The bank is the only one that can mint/burn points. It is also the only
one allowed to update the gift catalog from which customers can buy items.

Each other account is a normal one and does not any hold special permission.

### Supply management
Points are completely virtual. They do not represent any real world resource 
and are virtually unlimited. The supply is thus not an issue.

This token uses a trick to keep track of points spent: when points are granted
to a customer, the bank always mint the required amount before transferring it.
When a customer buys a gift, points return to the bank.

This means that the balance of the bank is the total of points spent by all the 
customers, assuming the initial total supply was 0 or a carry forward.

### Transfer conditions
No specific restrictions on transfer in this implementation.

Although in some cases points transfers might be forbidden between customers to
prevent points traffic.

### Allowances conditions
Allowances are forbidden. They do not make sense in the implementation as
the purchase endpoint can only be called by the true owner of the account.

### Others

The catalog implementation is very simple: a mapping of names to prices.
It might take advantage of a deeper thinking to also carry a supply per item.