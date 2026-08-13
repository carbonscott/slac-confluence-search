<!-- archived from https://developer.atlassian.com/server/confluence/cql-function-reference/ -->

# CQL function reference

The instructions on this page describe how to use functions in CQL to define structured search
queries to [search for content in Confluence](/server/confluence/advanced-searching-using-cql).

## Functions Reference

A function in CQL appears as a word followed by parentheses, which may contain one or more explicit values.
In a clause, a function is preceded by an [operator](/server/confluence/advanced-searching-using-cql#operator-reference) that
in turn is preceded by a [field](/server/confluence/advanced-searching-using-cql#field-reference).
A function performs a calculation on either specific Confluence data or the function content in parentheses,
such that only true results are retrieved by the function and then again by the clause in which the function is used.

## List of Functions

This list provides explanations and examples for the following functions:

* currentUser()
* endOfDay()
* endOfMonth()
* endOfWeek()
* endOfYear()
* startOfDay()
* startOfMonth()
* startOfWeek()
* startOfYear()
* favouriteSpaces()
* recentlyViewedContent()
* recentlyViewedSpaces()

#### Current user

Perform searches based on the currently logged-in user.

Note that this function can only be used by logged-in users. Anonymous users cannot use this function.

###### Syntax

```
```
1
2
```

```
currentUser()
```
```

###### Supported Fields

* [creator](/server/confluence/advanced-searching-using-cql/#creator)
* [contributor](/server/confluence/advanced-searching-using-cql/#contributor)
* [mention](/server/confluence/advanced-searching-using-cql/#mention)
* [watcher](/server/confluence/advanced-searching-using-cql/#watcher)
* [favourite](/server/confluence/advanced-searching-using-cql/#favourite-favorite)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Examples

* Find content that was created by me.

  ```
  ```
  1
  2
  ```

  ```
  creator = currentUser()
  ```
  ```
* Find content that mentions me but wasn't created by me.

  ```
  ```
  1
  2
  ```

  ```
  mention = currentUser() and creator != currentUser()
  ```
  ```

#### End of day

Perform searches based on the end of the current day.

###### Syntax

```
```
1
2
```

```
endOfDay()
```
```

or

```
```
1
2
```

```
endOfDay("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created since the end of yesterday.

  ```
  ```
  1
  2
  ```

  ```
  created > endOfDay("-1d")
  ```
  ```

#### End of month

Perform searches based on the end of the current month.

###### Syntax

```
```
1
2
```

```
endOfMonth()
```
```

or

```
```
1
2
```

```
endOfMonth("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content modified before the end of the month.

  ```
  ```
  1
  2
  ```

  ```
  lastmodified < endOfMonth()
  ```
  ```

#### End of week

Perform searches based on the end of the current week.

###### Syntax

```
```
1
2
```

```
endOfWeek()
```
```

or

```
```
1
2
```

```
endOfWeek("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created after the end of last week.

  ```
  ```
  1
  2
  ```

  ```
  created > endOfWeek("-1w")
  ```
  ```

#### End of year

Perform searches based on the end of the current year.

###### Syntax

```
```
1
2
```

```
endOfYear()
```
```

or

```
```
1
2
```

```
endOfYear("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created by the end of this year.

  ```
  ```
  1
  2
  ```

  ```
  created < endOfYear()
  ```
  ```

#### Start of day

Perform searches based on the start of the current day.

###### Syntax

```
```
1
2
```

```
startOfDay()
```
```

or

```
```
1
2
```

```
startOfDay("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created since the start of today.

  ```
  ```
  1
  2
  ```

  ```
  created > startOfDay()
  ```
  ```
* Find content created in the last 7 days.

  ```
  ```
  1
  2
  ```

  ```
  created > startOfDay("-7d")
  ```
  ```

#### Start of month

Perform searches based on the start of the current month.

###### Syntax

```
```
1
2
```

```
startOfMonth()
```
```

or

```
```
1
2
```

```
startOfMonth("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created since the start of the month.

  ```
  ```
  1
  2
  ```

  ```
  created >= startOfMonth()
  ```
  ```

#### Start of week

Perform searches based on the start of the current week.

###### Syntax

```
```
1
2
```

```
startOfWeek()
```
```

or

```
```
1
2
```

```
startOfWeek("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created since the start of the week.

  ```
  ```
  1
  2
  ```

  ```
  created >= startOfWeek()
  ```
  ```

#### Start of year

Perform searches based on the start of the current year.

```
```
1
2
```

```
startOfYear()
```
```

or

```
```
1
2
```

```
startOfYear("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created this year.

  ```
  ```
  1
  2
  ```

  ```
  created >= startOfYear()
  ```
  ```

#### Now

Perform searches based on current time.

###### Syntax

```
```
1
2
```

```
now()
```
```

or

```
```
1
2
```

```
now("inc")
```
```

where `inc` is an optional increment of `(+/-)nn(y|M|w|d|h|m)`

* If the plus/minus `(+/-)` sign is omitted, plus is assumed.
* nn: number; y: year, M: month; w: week; d: day; h: hour; m: minute.

###### Supported Fields

* [created](/server/confluence/advanced-searching-using-cql/#created)
* [lastmodified](/server/confluence/advanced-searching-using-cql/#lastmodified)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Examples

* Find content created before current time.

  ```
  ```
  1
  2
  ```

  ```
  created <= now()
  ```
  ```

###### Available from version

5.7

#### Favorite spaces

Returns a list of space keys, corresponding to the favorite spaces of the logged in user.

###### Syntax

```
```
1
2
```

```
favouriteSpaces()
```
```

###### Supported Fields

* [space](/server/confluence/advanced-searching-using-cql/#space)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | No | No | No | No | No | No | No | Yes | Yes |

###### Examples

* Find content which exists in the favorite spaces of the logged in user.

```
```
1
2
```

```
space IN favouriteSpaces()
```
```

* Find content which exists in the favourite spaces of the logged in user as well as other listed spaces

```
```
1
2
```

```
space IN (favouriteSpaces(), 'FS', 'TS')
```
```

###### Available from version

5.9

#### Current space

Returns a current space. Requires `cqlcontext` with `spaceKey`.

###### Syntax

```
```
1
2
```

```
currentSpace()
```
```

###### Supported Fields

* [space](/server/confluence/advanced-searching-using-cql/#space)

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | Yes | No | No | No | No | No | No |

###### Examples

* Find content that exists in the current spaces.

```
```
1
2
```

```
space = currentSpace()
```
```

* Curl example.

```
```
1
2
```

```
curl -u user:pwd 'http://localhost:8080/confluence/rest/api/search?cql=space%20=%20currentSpace()&cqlcontext=%7B"spaceKey":"TEST"%7D'
```
```

###### Available from version

5.7

#### Recently viewed content

Returns a list of IDs of recently viewed content for the logged in user.

###### Syntax

```
```
1
2
```

```
recentlyViewedContent(limit, offset)
```
```

###### Supported Fields

* ancestor
* content
* id
* parent

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | No | No | No | No | No | No | No | Yes | Yes |

Examples

* Find contents with limit to recent 10 history.

```
```
1
2
```

```
id in recentlyViewedContent(10)
```
```

* Find contents with limit to recent 10 history, but skip first 20.

```
```
1
2
```

```
id in recentlyViewedContent(10, 20)
```
```

###### Available from version

5.9

#### Recently viewed spaces

Returns a list of key of spaces recently viewed by the logged in user.

###### Syntax

```
```
1
2
```

```
recentlyViewedSpaces(limit)
```
```

###### Supported Fields

* space

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | No | No | No | No | No | No | No | Yes | Yes |

Examples

* Find spaces with limit to recent 10 history.

```
```
1
2
```

```
 space in recentlyViewedSpaces(10)
```
```

###### Available from version

5.9

## Reserved Characters

CQL has a list of reserved characters:

* **space** (`" "`)
* `"+"`
* `"."`
* `","`
* `";"`
* `"?"`
* `"|"`
* `"*"`
* `"/"`
* `"%"`
* `"^"`
* `"$"`
* `"#"`
* `"@"`
* `"["`
* `"]"`
* `"-"`

If you wish to use these characters in queries, you need to:

* surround them with quote-marks (you can use either single quote-marks (`'`) or double quote-marks (`"`));
  *and*, if you are searching a text field and the character is on the list of [reserved characters for Text Searches](https://confluence.atlassian.com/display/JIRA/Performing+Text+Searches#PerformingTextSearches-escaping).
* precede them with two backslashes.

## Reserved Words

CQL has a list of reserved words. These words need to be surrounded by quote-marks if you wish to use them in queries:

"after", "and", "as", "avg", "before", "begin", "by","commit", "contains", "count", "distinct", "else", "empty", "end", "explain", "from", "having", "if", "in", "inner", "insert", "into", "is", "isnull", "left", "like", "limit", "max", "min", "not", "null", "or", "order", "outer", "right", "select", "sum", "then", "was", "where", "update"

### Related topics:

* [Advanced searching using CQL](/server/confluence/advanced-searching-using-cql).
* [Performing text searches using CQL](/server/confluence/performing-text-searches-using-cql).
* [CQL field reference](/server/confluence/cql-field-reference).
