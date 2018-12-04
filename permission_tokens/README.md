# Permission Token

## Type 
**Utility token (SEC) / Utility token (FINMA)**

> Provides access to the goods & services that a project offers.

https://medium.com

## Description
The permission token enables to provide and then verify access to a
resource. There is one token per accessed resource. Users can require, exchange
and later use tokens representing access to the resource.

This token can be configured to give 3 different types of permissions:
- unrestricted access to an unlimited resource:
  Reusable permission, like a door pass, an admin right, etc...
- restricted access to an unlimited resource:
  Make 3 wishes, use 100 times an API for free, etc...
- restricted access to a limited resource:
  Eat 2 cookies, Get 4 seats at a concert, etc...

The type influences the side effect at the moment the token is used only.

## Characteristics

This token has following properties.

### Decimals

A permission is atomic and cannot be split. Thus, it has no decimals.

### Roles
The token creator is called the **authority**. The authority is meant to 
represent the entity granting or revoking the permission.

The authority is entitled with all the units when the token is created. 
Throughout time, the authority will dispatch tokens to give permissions and
collect them back when those permissions are used or to revoke a previously
granted right. 

Each other account is a normal one and does not any hold special permission.

### Supply management

Token supply really depends on the use case and the type of token:
- *Limited resource*: it represents the quantity of resources available. 
Like the cookies in the jar eaten by voracious children.
- *Unlimited resource*: it represents the maximum number of concurrent permissions
that can be given at a time. For example, toilets for 15 people. People buy a 
token when they get in and spend it when they get out. When there are too many
people in, no more token can be given away.

In both case, the authority usually creates or destroys tokens 
when the represented resource supply changes.

### Transfer conditions
Depends on the case as well.
Some permissions could be traded or sold, like a concert ticket. Some other
should not, like a driving license for example.

This version of the token assumes the tokens can be exchanged but updating it
would be easy.

### Allowances conditions
No specific restrictions on allowances.

One might decide to forbid allowances though, depending
on the use case.

### Others

All permissions can be frozen using the `is_frozen` switch, providing a
simple way to suspend the entire system while something is off.


