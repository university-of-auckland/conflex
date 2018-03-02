# Information Fix for Views in MySQL 5.7

Views that include joins for the Architecture Overview require a `GROUP BY` clause in their SQL.
Whilst this works fine in MySQL versions below 5.7 (due to the `ONLY_FULL_GROUP_BY` being set automatically) this does
not always work out in version 5.7.

To fix this, every field in the `SELECT` statement should be contained by the `ANY_VALUE()` function (this should not
include the `AS` keyword).