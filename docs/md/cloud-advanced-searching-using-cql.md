<!-- archived from https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/ -->

# Advanced searching using CQL

The instructions on this page describe how to define and execute a search using the advanced search capabilities of the Confluence REST API.

## What is an advanced search?

An advanced search allows you to use structured queries to search for content in Confluence. Your search results will take the same form as the Content model returned by the Content REST API.

When you perform an advanced search, you are using the Confluence Query Language (CQL).

A simple query in CQL (also known as a 'clause') consists of a [field](#field-reference), followed by an [operator](#operator-reference), followed by one or more values or [functions](/cloud/confluence/cql-functions). For example, the following simple query will find all content in the "TEST" space. It uses the Space [field](#field-reference), the [EQUALS](#equals) operator, and the value (`"TEST"`.)

```
```
1
2
```

```
space = "TEST"
```
```

It is not possible to compare two [fields](#field-reference).

CQL gives you some SQL-like syntax, such as the [ORDER BY](#order-by) SQL keyword. However, CQL is not a database query language. For example, CQL does not have a `SELECT` statement.

### How to perform an advanced search

The Content API REST Resource now supports CQL as a query parameter to filter the list of returned content.

```
```
1
2
```

```
https://your-domain.atlassian.net/wiki/rest/api/content/search?cql=space=TEST
```
```

To perform an advanced search:

1. Add your query using the [fields](#field-reference), [operators](#operator-reference) and field values or [functions](/cloud/confluence/cql-functions) as the value for the CQL query parameter.
2. Execute a GET request on the resource, you can apply expansions and pagination as you would normally in the Confluence REST API.

Expansion and pagination results will be limited in certain circumstances. For example, using the `expand=body.storage.value` will return a maximum of 50 results even when you add a `limit` greater than 50. The response will not call out that the results are arbitrarily limited to 50 records. Removing the `expand` parameter will return larger limits.

### Performing text searches

You can use the [CONTAINS](#contains) operator to use Lucene's text-searching features when performing searches on these fields:

* title
* text
* space.title

For details, please see the page on [Performing text searches](/cloud/confluence/performing-text-searches-using-cql).

### Setting precedence of operators

You can use parentheses in complex CQL statements to enforce the precedence of [operators](#operator-reference).

For example, if you want to find all pages in the Developer space as well as all blog posts created by the user with accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`, you can use parentheses to enforce the precedence of the boolean operators in your query. For example:

```
```
1
2
```

```
(type=page and Space=DEV) OR (creator="99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e" and type=blogpost)
```
```

If you do not use parentheses, the statement will be evaluated left to right.

You can also use parentheses to group clauses, so that you can apply the [NOT](#not) operator to the group.

## Keyword reference

A keyword in CQL is a word or phrase that:

* joins two or more clauses together to form a complex CQL query, or
* alters the logic of one or more clauses, or
* alters the logic of [operators](#operator-reference), or
* has an explicit definition in a CQL query, or
* performs a specific function that alters the results of a CQL query.

**List of keywords:**

* [AND](#and)
* [OR](#or)
* [NOT](#not)
* [ORDER BY](#order-by)

#### AND

Used to combine multiple clauses, allowing you to refine your search.

You can use [parentheses](#setting-precedence-of-operators) to control the order in which clauses are executed.

###### Examples

* Find all blogposts with the label "performance"

  ```
  ```
  1
  2
  ```

  ```
  label = "performance" and type = "blogpost"
  ```
  ```
* Find all pages created in the DEV space by the user with accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`

  ```
  ```
  1
  2
  ```

  ```
  type = page and creator = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e" and space = DEV
  ```
  ```
* Find all content that mentions the user with accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`, but was not created by the same user

  ```
  ```
  1
  2
  ```

  ```
  mention = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e" and creator != "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```

#### OR

Used to combine multiple clauses, allowing you to expand your search.

You can use [parentheses](#setting-precedence-of-operators) to control the order in which clauses are executed.

Also see [IN](#in), which can be a more convenient way to search for multiple values of a field.

###### Examples

* Find all content in the IDEAS space or with the label idea

  ```
  ```
  1
  2
  ```

  ```
  space = IDEAS or label = idea
  ```
  ```
* Find all content last modified before the start of the year or with the label needs\_review

  ```
  ```
  1
  2
  ```

  ```
  lastModified < startOfYear() or label = needs_review
  ```
  ```

#### NOT

Used to negate individual clauses or a complex CQL query (a query made up of more than one clause) using [parentheses](#setting-precedence-of-operators), allowing you to refine your search.

Also see [NOT EQUALS](#not-equals)("!="), [DOES NOT CONTAIN](#does-not-contain)("!~") and [NOT IN](#not-in).

###### Examples

* Find all pages with the "cql" label that aren't in the dev space

  ```
  ```
  1
  2
  ```

  ```
  label = cql and not space = dev
  ```
  ```

#### ORDER BY

Used to specify the fields by whose values the search results will be sorted.

By default, the field's own sorting order will be used. You can override this by specifying ascending order ("`asc`") or descending order ("`desc`").

Not all fields support Ordering. Generally, ordering is not supported where a piece of content can have multiple values for a field, for instance ordering is not supported on labels.

###### Examples

* Find content in the DEV space ordered by creation date

  ```
  ```
  1
  2
  ```

  ```
  space = DEV order by created
  ```
  ```
* Find content in the DEV space ordered by creation date with the newest first, then title

  ```
  ```
  1
  2
  ```

  ```
  space = DEV order by created desc, title
  ```
  ```

## Operator reference

An operator in CQL is one or more symbols or words which compares the value of a [field](#field-reference) on its left with one or more values (or functions) on its right, such that only true results are retrieved by the clause. Some operators may use the [NOT](#not) keyword.

**List of operators:**

* [EQUALS: =](#equals)
* [NOT EQUALS: !=](#not-equals)
* [GREATER THAN: >](#greater-than)
* [GREATER THAN EQUALS: >=](#greater-than-equals)
* [LESS THAN: <](#less-than)
* [LESS THAN EQUALS: <=](#less-than-equals)
* [IN](#in)
* [NOT IN](#not-in)
* [CONTAINS: ~](#contains)
* [DOES NOT CONTAIN: !~](#does-not-contain)

#### EQUALS: =

The "`=`" operator is used to search for content where the value of the specified field exactly matches the specified value (cannot be used with [text](#text) fields; see the [CONTAINS](#contains) operator instead.)

To find content where the value of a specified field exactly matches *multiple* values, use multiple "`=`" statements with the [AND](#and) operator.

###### Examples

* Find all content that was created by the user with accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`

  ```
  ```
  1
  2
  ```

  ```
  creator = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```
* Find all content that has the title "Advanced Searching"

  ```
  ```
  1
  2
  ```

  ```
  title = "\"Advanced Searching\""
  ```
  ```

#### NOT EQUALS: !=

The "`!=`" operator is used to search for content where the value of the specified field does not match the specified value. (Note: cannot be used with [text](#text) fields; see the [DOES NOT MATCH](#does-not-contain) ("`!~`") operator instead.)

Typing `field != value` is the same as typing `NOT field = value`.

Currently a negative expression cannot be the first clause in a CQL statement

###### Examples

* Find all content in the DEV space that was created by someone other than the user with accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`

  ```
  ```
  1
  2
  ```

  ```
  space = DEV and not creator = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```

  or:

  ```
  ```
  1
  2
  ```

  ```
  space = DEV and creator != "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```
* Find all content that was created by me but doesn't mention me

  ```
  ```
  1
  2
  ```

  ```
  creator = currentUser() and mention != currentUser()
  ```
  ```

#### GREATER THAN: >

The "`>`" operator is used to search for content where the value of the specified field is greater than the specified value. Cannot be used with [text](#text) fields.

Note that the "`>`" operator can only be used with fields which support range operators (e.g. date fields and numeric fields). To see a field's supported operators, check the individual [field](#field-reference) reference.

###### Examples

* Find all content created in the last 4 weeks

  ```
  ```
  1
  2
  ```

  ```
  created > now("-4w")
  ```
  ```
* Find all attachments last modified since the start of the month

  ```
  ```
  1
  2
  ```

  ```
  created > startOfMonth() and type = attachment
  ```
  ```

#### GREATER THAN EQUALS: >=

The "`>=`" operator is used to search for content where the value of the specified field is greater than or equal to the specified value. Cannot be used with [text](#text) fields.

Note that the "`>=`" operator can only be used with fields which support range operators (e.g. date fields). To see a field's supported operators, check the individual [field](#field-reference) reference.

###### Examples

* Find all content created on or after 31/12/2008:

  ```
  ```
  1
  2
  ```

  ```
  created >= "2008/12/31"
  ```
  ```

#### LESS THAN: <

The "`<`" operator is used to search for content where the value of the specified field is less than the specified value. Cannot be used with [text](#text) fields.

Note that the "`<`" operator can only be used with fields which support range operators (e.g. date fields). To see a field's supported operators, check the individual [field](#field-reference) reference.

###### Examples

* Find all pages lastModified before the start of the year

  ```
  ```
  1
  2
  ```

  ```
  lastModified < startOfYear() and type = page
  ```
  ```

#### LESS THAN EQUALS: <=

The "`<=`" operator is used to search for content where the value of the specified field is less than or equal to than the specified value. Cannot be used with [text](#text) fields.

Note that the "`<=`" operator can only be used with fields which support range operators (e.g. date fields). To see a field's supported operators, check the individual [field](#field-reference) reference.

###### Examples

* Find blogposts created in the since the start of the fortnight

  ```
  ```
  1
  2
  ```

  ```
  created >= startOfWeek("-1w") and type = blogpost
  ```
  ```

#### IN

The "`IN`" operator is used to search for content where the value of the specified field is one of multiple specified values. The values are specified as a comma-delimited list, surrounded by parentheses.

Using "`IN`" is equivalent to using multiple `EQUALS (=)` statements with the OR keyword, but is shorter and more convenient. That is, typing `creator IN ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01", "2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7")` is the same as typing `creator = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e" OR creator = "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01" OR creator = "2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7"`.

###### Examples

* Find all content that mentions any of the users with the accountIds `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`,`48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01`, or `2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7`

  ```
  ```
  1
  2
  ```

  ```
  mention in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01", "2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7")
  ```
  ```
* Find all content where the creator or contributor is either the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e` or the user with the accountId `48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01`

  ```
  ```
  1
  2
  ```

  ```
  creator in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01") or contributor in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01")
  ```
  ```

#### NOT IN

The "`NOT IN`" operator is used to search for content where the value of the specified field is not one of multiple specified values.

Using "`NOT IN`" is equivalent to using multiple `NOT_EQUALS (!=)` statements, but is shorter and more convenient. That is, typing `creator NOT IN ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01", "2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7")` is the same as typing `creator != "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e" AND creator != "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01" AND creator != "2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7"`.

###### Examples

* Find all content where the creator is someone other than the users with the accountIds `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`,`48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01`, or `2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7`

  ```
  ```
  1
  2
  ```

  ```
  space = DEV and creator not in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01", "2223:48d-3a-XXXX-XXXX-XXXX-8d9dd0e98as7")
  ```
  ```

#### CONTAINS: ~

The "`~`" operator is used to search for content where the value of the specified field matches the specified value (either an exact match or a "fuzzy" match -- see examples below). The "~" operator can only be used with text fields, for example:

* title
* text

When using the "`~`" operator, the value on the right-hand side of the operator can be specified using [Confluence text-search syntax](/cloud/confluence/performing-text-searches-using-cql).

###### Examples

* Find content created by users with a full name (depending on profile visibility) like *alana*

  ```
  ```
  1
  2
  ```

  ```
  creator.fullname ~ "alana"
  ```
  ```
* Find all content where the title contains the word "win" (or simple derivatives of that word, such as "wins"):

  ```
  ```
  1
  2
  ```

  ```
  title ~ win
  ```
  ```
* Find all content where the title contains a [wild-card](/cloud/confluence/cql-operators) match for the word "win":

  ```
  ```
  1
  2
  ```

  ```
  title ~ "win*"
  ```
  ```
* Find all content where the text contains the exact phrase "advanced search":

  ```
  ```
  1
  2
  ```

  ```
  text ~ "\"advanced search\""
  ```
  ```

#### DOES NOT CONTAIN: !~

The "`!~`" operator is used to search for content where the value of the specified field is not a "fuzzy" match for the specified value. The "!~" operator can only be used with text fields, for example:

* title
* text

When using the "`!~`" operator, the value on the right-hand side of the operator can be specified using [Confluence text-search syntax](/cloud/confluence/performing-text-searches-using-cql).

###### Examples

* Find all content where the title does not contain the word "run" (or derivatives of that word, such as "running" or "ran"):

  ```
  ```
  1
  2
  ```

  ```
  space = DEV and title !~ run
  ```
  ```

## Field reference

A field in CQL is a word that represents an indexed property of content in Confluence. In a clause, a field is followed by an [operator](#operator-reference), which in turn is followed by one or more values (or functions). The operator compares the value of the field with one or more values or functions on the right, such that only true results are retrieved by the clause.

CQL input queries submitted through the `/wiki/rest/api/search` endpoint no longer support user-specific fields like `user`, `user.fullname`, `user.accountid`, and `user.userkey`.

CQL input queries submitted through the `/wiki/rest/api/search/user` endpoint only support user-specific fields like `user`, `user.fullname`, `user.accountid`, and `user.userkey`.

See this [deprecation notice](https://developer.atlassian.com/cloud/confluence/deprecation-notice-search-api/) for more details.

**List of fields:**

* [Ancestor](#ancestor)
* [Content](#content)
* [Created](#created)
* [Creator](#creator)
* [Contributor](#contributor)
* [favourite, favourite](#favourite--favourite)
* [ID](#id)
* [Label](#label)
* [LastModified](#lastmodified)
* [Macro](#macro)
* [Mention](#mention)
* [Parent](#parent)
* [PageStatus](#pagestatus)
* [Space](#space)
* [Text](#text)
* [Title](#title)
* [Type](#type)
* [Watcher](#watcher)
* [User](#user)

#### Ancestor

Search for all content items that are descendants of a given ancestor content item. This includes direct child contents and their descendants. It is more general than the [parent](#parent) field.

###### Syntax

```
```
1
2
```

```
ancestor
```
```

###### Field type

CONTENT

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find all descendants with a given ancestor content ID

  ```
  ```
  1
  2
  ```

  ```
  ancestor = 123
  ```
  ```
* Find descendants of a group of ancestor content items

  ```
  ```
  1
  2
  ```

  ```
  ancestor in (123, 456, 789)
  ```
  ```

#### Content

Search for content that have a given content ID. This is an alias of the [ID](#id) field.

###### Syntax

```
```
1
2
```

```
content
```
```

###### Field type

CONTENT

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find content with a given content id

  ```
  ```
  1
  2
  ```

  ```
  content = 123
  ```
  ```
* Find content in a set of content ids

  ```
  ```
  1
  2
  ```

  ```
  content in (123, 223, 323)
  ```
  ```

#### Created

Search for content that was created on, before or after a particular date (or date range).

Search results will be relative to your configured time zone (which is by default the Confluence server's time zone).

Use one of the following formats:

`"yyyy/MM/dd HH:mm"`
`"yyyy-MM-dd HH:mm"`
`"yyyy/MM/dd"`
`"yyyy-MM-dd"`

###### Syntax

```
```
1
2
```

```
created
```
```

###### Field type

DATE

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | yes | yes | yes | yes | no | no |

###### Supported functions

* [endOfDay()](/cloud/confluence/cql-functions/#endofday)
* [endOfMonth()](/cloud/confluence/cql-functions/#endofmonth)
* [endOfWeek()](/cloud/confluence/cql-functions/#endofweek)
* [endOfYear()](/cloud/confluence/cql-functions/#endofyear)
* [startOfDay()](/cloud/confluence/cql-functions/#startofday)
* [startOfMonth()](/cloud/confluence/cql-functions/#startofmonth)
* [startOfWeek()](/cloud/confluence/cql-functions/#startofweek)
* [startOfYear()](/cloud/confluence/cql-functions/#startofyear)

###### Examples

* Find content created after the 1st September 2014

  ```
  ```
  1
  2
  ```

  ```
  created > 2014/09/01
  ```
  ```
* Find content created in the last 4 weeks

  ```
  ```
  1
  2
  ```

  ```
  created >= now("-4w")
  ```
  ```

#### Creator

Search for content that was created by a particular user. You can search by the user's accountId.

###### Syntax

```
```
1
2
```

```
creator
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

* [currentUser()](/cloud/confluence/cql-functions/#currentuser)

###### Examples

* Find content created by the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`

  ```
  ```
  1
  2
  ```

  ```
  creator = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```
* Find content created by the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e` or the user with the accountId `48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01`

  ```
  ```
  1
  2
  ```

  ```
  creator in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01")
  ```
  ```

#### Contributor

Search for content that was created or edited by a particular user. You can search by the user's accountId.

###### Syntax

```
```
1
2
```

```
contributor
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

* [currentUser()](/cloud/confluence/cql-functions/#currentuser)

###### Examples

* Find content created by 99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e

  ```
  ```
  1
  2
  ```

  ```
  contributor = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```
* Find content created by the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e` or the user with the accountId `48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01`

  ```
  ```
  1
  2
  ```

  ```
  contributor in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01")
  ```
  ```

#### favourite, favourite

Search for content that was favorited by a particular user. You can search by the user's accountId.

Due to security restrictions you are only allowed to filter on the logged in user's favorites. This field is available in both British and American spellings.

###### Syntax

```
```
1
2
```

```
favourite
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

* [currentUser()](/cloud/confluence/cql-functions/#currentuser)

###### Examples

* Find content that is favorited by the current user

  ```
  ```
  1
  2
  ```

  ```
  favourite = currentUser()
  ```
  ```
* Find content favorited by the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`, where the same user is also the logged-in user

  ```
  ```
  1
  2
  ```

  ```
  favourite = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```

#### ID

Search for content that have a given content ID.

###### Syntax

```
```
1
2
```

```
id
```
```

###### Field type

CONTENT

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find content with the ID 123

  ```
  ```
  1
  2
  ```

  ```
  id = 123
  ```
  ```
* Find content in a set of content IDs

  ```
  ```
  1
  2
  ```

  ```
  id in (123, 223, 323)
  ```
  ```

#### Label

Search for content that has a particular label

###### Syntax

```
```
1
2
```

```
label
```
```

###### Field type

STRING

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find content that has the label finished

  ```
  ```
  1
  2
  ```

  ```
  label = finished
  ```
  ```
* Find content that doesn't have the label draft or review

  ```
  ```
  1
  2
  ```

  ```
  label not in (draft, review)
  ```
  ```

#### LastModified

Search for content that was last modified on, before, or after a particular date (or date range).

The search results will be relative to your configured time zone (which is by default the Confluence server's time zone)

Use one of the following formats:

`"yyyy/MM/dd HH:mm"`
`"yyyy-MM-dd HH:mm"`
`"yyyy/MM/dd"`
`"yyyy-MM-dd"`

###### Syntax

```
```
1
2
```

```
lastmodified
```
```

###### Field type

DATE

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | yes | yes | yes | yes | no | no |

###### Supported functions

* [endOfDay()](/cloud/confluence/cql-functions/#endofday)
* [endOfMonth()](/cloud/confluence/cql-functions/#endofmonth)
* [endOfWeek()](/cloud/confluence/cql-functions/#endofweek)
* [endOfYear()](/cloud/confluence/cql-functions/#endofyear)
* [startOfDay()](/cloud/confluence/cql-functions/#startofday)
* [startOfMonth()](/cloud/confluence/cql-functions/#startofmonth)
* [startOfWeek()](/cloud/confluence/cql-functions/#startofweek)
* [startOfYear()](/cloud/confluence/cql-functions/#startofyear)

###### Examples

* Find content that was last modified on 1st September 2014

  ```
  ```
  1
  2
  ```

  ```
  lastmodified = 2014-09-01
  ```
  ```
* Find content that was last modified before the start of the year

  ```
  ```
  1
  2
  ```

  ```
  lastmodified < startOfYear()
  ```
  ```
* Find content that was last modified on or after 1st September but before 9am on 3rd September 2014

  ```
  ```
  1
  2
  ```

  ```
  lastmodified >= 2014-09-01 and lastmodified < "2014-09-03 09:00"
  ```
  ```

#### Macro

Search for content that has an instance of the macro with the given name in the body of the content

###### Syntax

```
```
1
2
```

```
macro
```
```

###### Field type

STRING

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find content that has the Jira issue macro

  ```
  ```
  1
  2
  ```

  ```
  macro = jira
  ```
  ```
* Find content that has Table of content macro or the widget macro

  ```
  ```
  1
  2
  ```

  ```
  macro in (toc, widget)
  ```
  ```

#### Mention

Search for content that mentions a particular user. You can search by the user's accountId.

###### Syntax

```
```
1
2
```

```
mention
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

* [currentUser()](/cloud/confluence/cql-functions/#currentuser)

###### Examples

* Find content that mentions the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e` or the user with the accountId `48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01`

  ```
  ```
  1
  2
  ```

  ```
  mention in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01")
  ```
  ```
* Find content that mentions the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e`

  ```
  ```
  1
  2
  ```

  ```
  mention = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```

#### PageStatus

Search for content that have a given page status.

###### Syntax

```
```
1
2
```

```
pageStatus
```
```

###### Field type

TEXT

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find content that has the page status "Rough draft"

  ```
  ```
  1
  2
  ```

  ```
  pageStatus = "Rough draft"
  ```
  ```
* Find content that doesn't have the page status "In progress" or "Ready for review"

  ```
  ```
  1
  2
  ```

  ```
  pageStatus not in ("\"In progress\"", "\"Ready for review\"")
  ```
  ```

#### Parent

Search for child content of a particular parent content item

###### Syntax

```
```
1
2
```

```
parent
```
```

###### Field type

CONTENT

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find children of a parent content item with ID 123

  ```
  ```
  1
  2
  ```

  ```
  parent = 123
  ```
  ```

#### Space

Search for content that is in a particular Space. You can search by the space's key.

###### Syntax

```
```
1
2
```

```
space
```
```

###### Field type

SPACE

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find content in the development space or the QA space

  ```
  ```
  1
  2
  ```

  ```
  space in (DEV, QA)
  ```
  ```
* Find content in the development space

  ```
  ```
  1
  2
  ```

  ```
  space = DEV
  ```
  ```

#### Text

This is a "master-field" that allows you to search for text across a number of other text fields. These are the same fields used by Confluence's search user interface.

* [Title](#title)
* Content body
* [Labels](#label)

[Confluence text-search syntax](/cloud/confluence/performing-text-searches-using-cql) can be used with this field.

###### Syntax

```
```
1
2
```

```
text
```
```

###### Field type

TEXT

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no | no | yes | yes | no | no | no | no | no | no |

###### Supported functions

None

###### Examples

* Find content that contains the word Confluence

  ```
  ```
  1
  2
  ```

  ```
  text ~ Confluence
  ```
  ```
* Find content in the development space

  ```
  ```
  1
  2
  ```

  ```
  space = DEV
  ```
  ```

#### Title

Search for content by title, or with a title that contains particular text.

[Confluence text-search syntax](/cloud/confluence/performing-text-searches-using-cql) can be used with these fields when used with the [CONTAINS](#contains) operator ("~", "!~").

###### Syntax

```
```
1
2
```

```
title
```
```

###### Field type

TEXT

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | yes | yes | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find content with the title "Advanced Searching using CQL"

  ```
  ```
  1
  2
  ```

  ```
  title = "\"Advanced Searching using CQL\""
  ```
  ```
* Find content where the title contains the exact phrase "Searching CQL" (i.e. a "fuzzy" match):

  ```
  ```
  1
  2
  ```

  ```
  title ~ "\"Searching CQL\""
  ```
  ```

#### Type

Search for content of a particular type. Supported content types are:

* page
* blogpost
* comment
* attachment
* whiteboard
* database
* embed
* folder

###### Syntax

```
```
1
2
```

```
type
```
```

###### Field type

TYPE

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

None

###### Examples

* Find blogposts or pages

  ```
  ```
  1
  2
  ```

  ```
  type IN (blogpost, page)
  ```
  ```
* Find attachments

  ```
  ```
  1
  2
  ```

  ```
  type = attachment
  ```
  ```

#### Watcher

Search for content that a particular user is watching. You can search by the user's accountId.

###### Syntax

```
```
1
2
```

```
watcher
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | no | no | no | no | no | no | yes | yes |

###### Supported functions

* [currentUser()](/cloud/confluence/cql-functions/#currentuser)

###### Examples

* Search for content that you are watching:

  ```
  ```
  1
  2
  ```

  ```
  watcher = currentUser()
  ```
  ```
* Search for content that the user with the accountId `99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e` is watching:

  ```
  ```
  1
  2
  ```

  ```
  watcher = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```

#### User

Search for users visible to you. There are several ways to perform a user search.

###### Syntax

```
```
1
2
```

```
user
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | no | no | no | no | no | no | no | yes | no |

###### Supported functions

* [currentUser()](/cloud/confluence/cql-functions/#currentuser)

###### Examples

* Search for current user:

  ```
  ```
  1
  2
  ```

  ```
  user = currentUser()
  ```
  ```
* Search for users by their accountIds:

  ```
  ```
  1
  2
  ```

  ```
  user = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  user in ("99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e", "48293:5s04-XXXX-XXXX-XXXX-d7a9b9d8c9f01")
  ```
  ```

###### Syntax

```
```
1
2
```

```
user.fullname
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no | no | yes | no | no | no | no | no | no | no |

###### Supported functions

None

###### Examples

* Search for users by their partial full name or public name, whichever is visible:

  ```
  ```
  1
  2
  ```

  ```
  user.fullname ~ "John"
  ```
  ```

###### Syntax

```
```
1
2
```

```
user.accountid
```
```

###### Field type

USER

###### Supported operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yes | no | no | no | no | no | no | no | yes | no |

###### Supported functions

None

###### Examples

* Search for users by their accountId:

  ```
  ```
  1
  2
  ```

  ```
  user.accountid = "99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"
  ```
  ```

### Related topics

* [Performing text searches using CQL](/cloud/confluence/performing-text-searches-using-cql/)
* [Adding a field to CQL](/cloud/confluence/cql-fields)
* [CQL field module](https://developer.atlassian.com/confdev/confluence-plugin-guide/confluence-plugin-module-types/cql-field-module)
* [CQL function module](/cloud/confluence/cql-functions)
