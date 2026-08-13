<!-- archived from https://developer.atlassian.com/server/confluence/advanced-searching-using-cql/ -->

# Advanced Searching using CQL

The instructions on this page describe how to define and execute a search using the advanced search capabilities of the Confluence REST API.

## What is an advanced search?

An advanced search allows you to use structured queries to search for content in Confluence. Your search results will take the same form as the Content model returned by the Content REST API.

When you perform an advanced search, you use the Confluence Query Language (CQL).

A simple query in CQL (also known as a 'clause') consists of a *[field](#field)*, followed by an *[operator](#cql-operators)*, followed by one or more *values* or *[functions](/server/confluence/cql-function-reference)*. For example, the following simple query will find all content in the "TEST" space. It uses the Space *[field](#field)*, the [EQUALS](#equals) *operator*, and the *value* `"TEST"`.)

```
```
1
2
```

```
space = "TEST"
```
```

It is not possible to compare two [fields](#fields).

NOTE: CQL gives you some SQL-like syntax, such as the [ORDER BY](#order-by) SQL keyword. However, CQL is not a database query language.
For example, CQL does not have a `SELECT` statement.

* [Function Reference](/server/confluence/cql-function-reference)

**Related topics:**

* [Performing text searches using CQL](/server/confluence/performing-text-searches-using-cql).
* [Adding a field to CQL](/server/confluence/adding-a-field-to-cql).
* [CQL Field Module](/server/confluence/cql-field-module).
* [CQL Function Module](/server/confluence/cql-function-module).

### How to perform an advanced search

The Content API REST Resource now supports CQL as a query parameter to filter the list of returned content.

```
```
1
2
```

```
curl -u username:password http://myhost:8080/rest/api/content/search?cql=space=TEST
```
```

The previous example is a simple query, if your query is more complicated you can use the following example:

```
```
1
2
```

```
curl -u username:password -G "http://myhost:8080/context/rest/api/content/search" \
--data-urlencode "cql=(type=page and space=DEV) OR (creator=admin and type=blogpost)" \
| python -m json.tool
```
```

To perform an advanced search:

1. Add your query using the [fields](#fields), [operators](#cql-operators), and field values or [functions](#functions) as the value for the CQL query parameter.
2. Execute a GET request on the resource, you can apply expansions and pagination as you would normally do in the Confluence REST API.

### Performing text searches

You can use the [CONTAINS](#contains) operator to use Lucene's text-searching features when performing searches on these fields:

* title
* text
* space.title

For details, see the page on [Performing text searches](/server/confluence/performing-text-searches-using-cql).

### Setting precedence of operators

To enforce the precedence of [operators](#cql-operators), you can use parentheses in complex CQL statements.

For example, if you want to find all pages in the Developer space as well as all blog posts created by the the system administrator (bobsmith),
you can use parentheses to enforce the precedence of the boolean operators in your query. For example:

```
```
1
2
```

```
(type=page and Space=DEV) OR (creator=bobsmith and type=blogpost)
```
```

Note: if you do not use parentheses, the statement will be evaluated left to right.

You can also use parentheses to group clauses, so that you can apply the [NOT](#not) operator to the group.

## Keyword reference

A keyword in CQL is a word or phrase that:

* Joins two or more clauses together to form a complex CQL query.
* Alters the logic of one or more clauses.
* Alters the logic of [operators](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-operators).
* Has an explicit definition in a CQL query.
* Performs a specific function that alters the results of a CQL query.

See the detailed examples for each keyword next.

#### AND

Used to combine multiple clauses, allowing you to refine your search.

Note: to control the order in which clauses are executed, you can use [parentheses](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-parentheses).

##### Examples

* Find all blogposts with the label "performance".

  ```
  ```
  1
  2
  ```

  ```
  label = "performance" and type = "blogpost"
  ```
  ```
* Find all pages created by jsmith in the DEV space.

  ```
  ```
  1
  2
  ```

  ```
  type = page and creator = jsmith and space = DEV
  ```
  ```
* Find all content that mentions jsmith but was not created by jsmith.

  ```
  ```
  1
  2
  ```

  ```
  mention = jsmith and creator != jsmith
  ```
  ```

#### OR

Used to combine multiple clauses, allowing you to expand your search.

Note: to control the order in which clauses are executed, you can use [parentheses](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-parentheses).
Also see [IN](/server/confluence/cql-operators-reference/#CQLOperatorsReference-IN),
which can be a more convenient way to search for multiple values of a field.)

##### Examples

* Find all content in the IDEAS space or with the label idea.

  ```
  ```
  1
  2
  ```

  ```
  space = IDEAS or label = idea
  ```
  ```
* Find all content last modified before the start of the year or with the label `needs\_review`.

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

Used to negate individual clauses or a complex CQL query (a query made up of more than one clause) using [parentheses](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-parentheses), allowing you to refine your search.

(Note: also see [NOT EQUALS](/server/confluence/cql-operators-reference/#CQLOperatorsReference-NOT_EQUALS) ("!="), [DOES NOT CONTAIN](#does-not-contain) ("!~") and [NOT IN](https://developer.atlassian.com/display/CONFDEV/CQL+Operators+Reference#CQLOperatorsReference-NOT_IN).)

##### Example

* Find all pages with the "cql" label that aren't in the dev space.

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

By default, the field's own sorting order is used. You can override this by specifying ascending order ("`asc`") or descending order ("`desc`").

Not all fields support ordering. Generally, ordering is not supported where a piece of content can have multiple values for a field,
for instance ordering is not supported on labels.

##### Examples

* Find content in the DEV space ordered by creation date.

  ```
  ```
  1
  2
  ```

  ```
  space = DEV order by created
  ```
  ```
* Find content in the DEV space ordered by creation date with the newest first, then title.

  ```
  ```
  1
  2
  ```

  ```
  space = DEV order by created desc, title
  ```
  ```
* Find pages created by jsmith ordered by created, then title.

  ```
  ```
  1
  2
  ```

  ```
  creator = jsmith order by created, title asc
  ```
  ```

## Operator reference

CQL Operators

An operator in CQL is one or more symbols or words that compare the value of a [field](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-field) on its left with one or more values (or [functions](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-functions)) on its right, such that only true results are retrieved by the clause. Some operators may use the [NOT](https://developer.atlassian.com/display/CONFDEV/CQL+Keywords+Reference#CQLKeywordsReference-NOT) keyword.

**List of Operators:**

* [EQUALS: =](#equals)
* [NOT EQUALS: !=](#not-equals)
* [GREATER THAN: >](#greater-than-gt)
* [GREATER THAN EQUALS: >=](#greater-than-equals-gt)
* [LESS THAN: <](#less-than-lt)
* [LESS THAN EQUALS: <=](#less-than-equals-lt)
* [IN](#in)
* [NOT IN](#not-in)
* [CONTAINS: ~](#contains)
* [DOES NOT CONTAIN: !~](#does-not-contain)

#### EQUALS: =

The "`=`" operator is used to search for content where the value of the specified field exactly matches the specified value. (Note: cannot be used with [text](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-text) fields; see the [CONTAINS](#contains) operator instead.)

To find content where the value of a specified field exactly matches *multiple* values, use multiple "`=`" statements with the [AND](https://developer.atlassian.com/display/CONFDEV/CQL+Keywords+Reference#CQLKeywordsReference-AND) operator.

##### Examples

* Find all content that were created by jsmith.

  ```
  ```
  1
  2
  ```

  ```
  creator = jsmith
  ```
  ```
* Find all content that has the title "Advanced Searching".

  ```
  ```
  1
  2
  ```

  ```
  title = "Advanced Searching"
  ```
  ```

#### NOT EQUALS: !=

The "`!=`" operator is used to search for content where the value of the specified field does not match the specified value. (Note: cannot be used with [text](#performing-text-searches) fields; see the [DOES NOT MATCH](#does-not-match) ("`!~`") operator instead.)

Note: typing `field != value` is the same as typing `NOT field = value`.

Currently a negative expression cannot be the first clause in a CQL statement.

##### Examples

* Find all content in the DEV space that was created by someone other than jsmith.

  ```
  ```
  1
  2
  ```

  ```
  space = DEV and not creator = jsmith
  ```
  ```

  or:

  ```
  ```
  1
  2
  ```

  ```
  space = DEV and creator != jsmith
  ```
  ```
* Find all content that was created by me but doesn't mention me.

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

The "`>`" operator is used to search for content where the value of the specified field is greater than the specified value.
Cannot be used with [text](#performing-text-searches) fields.

Note that the "`>`" operator can only be used with fields which support range operators (e.g. date fields and numeric fields).
To see a field's supported operators, check the individual [field](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-field) reference.

##### Examples

* Find all content created in the last 4 weeks.

  ```
  ```
  1
  2
  ```

  ```
  created > now("-4w")
  ```
  ```
* Find all attachments last modified since the start of the month.

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

The "`>=`" operator is used to search for content where the value of the specified field is greater than or equal to the specified value.
Cannot be used with [text](#performing-text-searches) fields.

Note that the "`>=`" operator can only be used with fields which support range operators (e.g. date fields).
To see a field's supported operators, check the individual [field](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-field) reference.

##### Examples

* Find all content created on or after 31/12/2008.

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

The "`<`" operator is used to search for content where the value of the specified field is less than the specified value. Cannot be used with [text](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-text) fields.

Note that the "`<`" operator can only be used with fields which support range operators (e.g. date fields). To see a field's supported operators, check the individual [field](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-field) reference.

##### Examples

* Find all pages `lastModified` before the start of the year.

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

The "`<=`" operator is used to search for content where the value of the specified field is less than or equals to the specified value.
Cannot be used with [text](#performing-text-searches) fields.

Note that the "`<=`" operator can only be used with fields which support range operators (e.g. date fields). To see a field's supported operators,
check the individual [field](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-field) reference.

##### Examples

* Find blog posts created in the since the start of the fortnight.

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

The "`IN`" operator is used to search for content where the value of the specified field is one of multiple specified values.
The values are specified as a comma-delimited list, surrounded by parentheses.

Using "`IN`" is equivalent to using multiple [EQUALS](#equals) (=) statements with the OR keyword, but is shorter and more convenient.
That is, typing `creator IN (tom, jane, harry)` is the same as typing `creator = "tom"` [OR](https://developer.atlassian.com/display/CONFDEV/CQL+Keywords+Reference#CQLKeywordsReference-OR)`creator = "jane"`[OR](https://developer.atlassian.com/display/CONFDEV/CQL+Keywords+Reference#CQLKeywordsReference-OR) `creator = "harry"`.

##### Examples

* Find all content that mentions either jsmith or jbrown or jjones.

  ```
  ```
  1
  2
  ```

  ```
  mention in (jsmith,jbrown,jjones)
  ```
  ```
* Find all content where the creator or contributor is either Jack or Jill.

  ```
  ```
  1
  2
  ```

  ```
  creator in (Jack,Jill) or contributor in (Jack,Jill)
  ```
  ```

#### NOT IN

The "`NOT IN`" operator is used to search for content where the value of the specified field is not one of multiple specified values.

Using "`NOT IN`" is equivalent to using multiple

[NOT\_EQUALS](#not-equals) (`!=`) statements, but is shorter and more convenient. That is, typing `creator NOT IN (tom, jane, harry)` is the same as typing `creator != "tom"` [AND](https://developer.atlassian.com/display/CONFDEV/CQL+Keywords+Reference#CQLKeywordsReference-AND) `creator != "jane"` [AND](#and) `creator != "harry"`.

##### Examples

* Find all content where the creator is someone other than Jack, Jill or John.

  ```
  ```
  1
  2
  ```

  ```
  space = DEV and creator not in (Jack,Jill,John)
  ```
  ```

#### CONTAINS: ~

The "`~`" operator is used to search for content where the value of the specified field matches the specified value (either an exact match or a "fuzzy" match -- see examples below). The "~" operator can only be used with text fields, for example:

* title
* text

Note: when using the "`~`" operator, the value on the right-hand side of the operator can be specified using [Confluence text-search syntax](https://developer.atlassian.com/display/CONFDEV/Performing+text+searches+using+CQL).

##### Examples

* Find all content where the title contains the word "win" (or simple derivatives of that word, such as "wins").

  ```
  ```
  1
  2
  ```

  ```
  title ~ win
  ```
  ```
* Find all content where the title contains a [wild-card](/server/confluence/cql-operators-reference) match for the word "win".

  ```
  ```
  1
  2
  ```

  ```
  title ~ "win*"
  ```
  ```
* Find all content where the text contains the word "advanced" and the word "search".

  ```
  ```
  1
  2
  ```

  ```
  text ~ "advanced search"
  ```
  ```

#### DOES NOT CONTAIN: !~

The "`!~`" operator is used to search for content where the value of the specified field is not a "fuzzy" match for the specified value.
The "!~" operator can only be used with text fields, for example:

* title
* text

Note: when using the "`!~`" operator, the value on the right-hand side of the operator can be specified using [Confluence text-search syntax](https://developer.atlassian.com/display/CONFDEV/Performing+text+searches+using+CQL).

##### Examples

* Find all content where the title does not contain the word "run" (or derivatives of that word, such as "running" or "ran").

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

A field in CQL is a word that represents an indexed property of content in Confluence. In a clause, a field is followed by an [operator](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-operator),
that in turn is followed by one or more values (or [functions](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-function)).
The operator compares the value of the field with one or more values or functions on the right, such that only true results are retrieved by the clause.

**List of Fields:**

* [Ancestor](#ancestor)
* [Container](#container)
* [Content](#content)
* [Created](#created)
* [Creator](#creator)
* [Contributor](#contributor)
* [Favourite, favorite](#favourite-favorite)
* [ID](#id)
* [Label](#label)
* [Last modified](#lastmodified)
* [Macro](#macro)
* [Mention](#mention)
* [Parent](#parent)
* [Space](#space)
  + [Space category](#space-category)
  + [Space key](#space-key)
  + [Space title](#space-title)
  + [Space type](#space-type)
* [Text](#text)
* [Title](#title)
* [Type](#type)
* [Watcher](#watcher)

#### Ancestor

Search for all pages that are descendants of a given ancestor page. This includes direct child pages and their descendents. It is more general than the [parent](#parent) field.

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

###### Field Type

CONTENT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find all descendent pages with a given anscestor page.

  ```
  ```
  1
  2
  ```

  ```
  ancestor = 123
  ```
  ```
* Find descendants of a group of ancestor pages.

  ```
  ```
  1
  2
  ```

  ```
  ancestor in (123, 456, 789)
  ```
  ```

#### Container

Search for content that is contained in the content with the given ID

###### Syntax

```
```
1
2
```

```
container
```
```

###### Field Type

CONTENT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find attachments contained in a page with the given content ID.

  ```
  ```
  1
  2
  ```

  ```
  container = 123 and type = attachment
  ```
  ```
* Find content container in a set of pages with the given IDs.

  ```
  ```
  1
  2
  ```

  ```
  container in (123, 223, 323)
  ```
  ```

#### Content

Search for content that have a given content ID. This is an alias of the [ID](https://developer.atlassian.com/display/CONFDEV/CQL+Field+Reference#ID) field.

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

###### Field Type

CONTENT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find content with a given content ID.

  ```
  ```
  1
  2
  ```

  ```
  content = 123
  ```
  ```
* Find content in a set of content IDs.

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

Note: search results will be relative to your configured time zone (which is by default the Confluence server time zone).

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

###### Field Type

DATE

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Supported Functions

* [endOfDay()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfDay)
* [endOfMonth()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfMonth)
* [endOfWeek()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfWeek)
* [endOfYear()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfYear)
* [startOfDay()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfDay)
* [startOfMonth()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfMonth)
* [startOfWeek()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfWeek)
* [startOfYear()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfYear)

###### Examples

* Find content created after the 1st September 2014.

  ```
  ```
  1
  2
  ```

  ```
  created > 2014/09/01
  ```
  ```
* Find content created in the last 4 weeks.

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

Search for content that was created by a particular user. You can search by the user's username.

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

###### Field Type

USER

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

* [currentUser()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-currentUser())

###### Examples

* Find content created by jsmith.

  ```
  ```
  1
  2
  ```

  ```
  created = jsmith
  ```
  ```
* Find content created by john smith or bob nguyen.

  ```
  ```
  1
  2
  ```

  ```
  created in (jsmith, bnguyen)
  ```
  ```

#### Contributor

Search for content that was created or edited by a particular user. You can search by the user's username.

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

###### Field Type

USER

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

* [currentUser()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-currentUser())

###### Examples

* Find content created by jsmith.

  ```
  ```
  1
  2
  ```

  ```
  contributor = jsmith
  ```
  ```
* Find content created by john smith or bob nguyen.

  ```
  ```
  1
  2
  ```

  ```
  contributor in (jsmith, bnguyen)
  ```
  ```

#### Favourite, favorite

Search for content that was favorited by a particular user. You can search by the user's username.

Due to security restrictions you are only allowed to filter on the logged in user's favourites.
This field is available in both British and American spellings.

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

###### Field Type

USER

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

* [currentUser()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-currentUser())

###### Examples

* Find content that is favorited by the current user.

  ```
  ```
  1
  2
  ```

  ```
  favourite = currentUser()
  ```
  ```
* Find content favorited by jsmith, where jsmith is also the logged in user.

  ```
  ```
  1
  2
  ```

  ```
  favourite = jsmith
  ```
  ```

#### ID

Search for content that has a given content ID.

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

###### Field Type

CONTENT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find content with the ID 123.

  ```
  ```
  1
  2
  ```

  ```
  id = 123
  ```
  ```
* Find content in a set of content IDs.

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

Search for content that has a particular label.

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

###### Field Type

STRING

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find content that has the label finished.

  ```
  ```
  1
  2
  ```

  ```
  label = finished
  ```
  ```
* Find content that doesn't have the label draft or review.

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

The search results will be relative to your configured time zone (which is by default the Confluence server time zone).

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

###### Field Type

DATE

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | Yes | Yes | Yes | Yes | No | No |

###### Supported Functions

* [endOfDay()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfDay)
* [endOfMonth()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfMonth)
* [endOfWeek()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfWeek)
* [endOfYear()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-endOfYear)
* [startOfDay()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfDay)
* [startOfMonth()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfMonth)
* [startOfWeek()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfWeek)
* [startOfYear()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-startOfYear)

###### Examples

* Find content that was last modified on 1st September 2014.

  ```
  ```
  1
  2
  ```

  ```
  lastmodified = 2014-09-01
  ```
  ```
* Find content that was last modified before the start of the year.

  ```
  ```
  1
  2
  ```

  ```
  lastmodified < startOfYear()
  ```
  ```
* Find content that was last modified on or after 1st September but before 9am on 3rd September 2014.

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

Search for content that has an instance of the macro with the given name in the body of the content.

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

###### Field Type

STRING

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

none

###### Examples

* Find content that has the JIRA issue macro.

  ```
  ```
  1
  2
  ```

  ```
  macro = jira
  ```
  ```
* Find content that has Table of content macro or the widget macro.

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

Search for content that mentions a particular user. You can search by the user's username.

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

###### Field Type

USER

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

* [currentUser()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-currentUser())

###### Examples

* Find content that mentions jsmith or kjones.

  ```
  ```
  1
  2
  ```

  ```
  mention in (jsmith, kjones)
  ```
  ```
* Find content that mentions jsmith.

  ```
  ```
  1
  2
  ```

  ```
  mention = jsmith
  ```
  ```

#### Parent

Search for child content of a particular parent page.

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

###### Field Type

CONTENT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

###### Examples

* Find child pages of a parent page with ID 123.

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

Search for content that is in a particular Space. By default, this searches by space key. You can also search by category, title, and type (see below).

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

###### Field Type

SPACE

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

none

###### Examples

* Find content in the development space or the QA space.

  ```
  ```
  1
  2
  ```

  ```
  space in (DEV, QA)
  ```
  ```
* Find content in the development space.

  ```
  ```
  1
  2
  ```

  ```
  space = DEV
  ```
  ```

#### Space category

Search for spaces with a particular space category applied. Categories are used to organise spaces in the space directory. Available from Confluence 6.15 and later.

###### Syntax

```
```
1
2
```

```
space.category
```
```

###### Field Type

STRING

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find spaces that have the category 'development'

  ```
  ```
  1
  2
  ```

  ```
  space.category = development
  ```
  ```
* Find spaces that don't have the category 'marketing' or 'operations'

  ```
  ```
  1
  2
  ```

  ```
  space.category not in (marketing, operations)
  ```
  ```

#### Space key

Search for spaces by space key.

###### Syntax

```
```
1
2
```

```
space.key
```
```

###### Field Type

STRING

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find the space that has the key 'DEV'

  ```
  ```
  1
  2
  ```

  ```
  space.key = DEV
  ```
  ```
* Find spaces that have either 'MKT' or 'OPS' or 'DEV'

  ```
  ```
  1
  2
  ```

  ```
  space.key in (MKT, OPS, DEV)
  ```
  ```

#### Space title

Search for spaces by title.

###### Syntax

```
```
1
2
```

```
space.title
```
```

###### Field Type

TEXT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | No | Yes | Yes | No | No | No | No | No | No |

###### Supported Functions

None

###### Examples

* Find spaces with titles that match 'Development Team' (fuzzy match)

  ```
  ```
  1
  2
  ```

  ```
  space.title ~ "Development Team"
  ```
  ```
* Find spaces with titles that don't match "Project" (fuzzy match)

  ```
  ```
  1
  2
  ```

  ```
  space.title !~ "Project"
  ```
  ```

#### Space type

Search for spaces of a particular type. Supported content types are:

* personal
* global (also known as site spaces)
* favourite, favorite (also known as My Spaces)

###### Syntax

```
```
1
2
```

```
space.type
```
```

###### Field Type

TYPE

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

None

###### Examples

* Find only personal spaces

  ```
  ```
  1
  2
  ```

  ```
  space.type = personal
  ```
  ```
* Find only site / global spaces

  ```
  ```
  1
  2
  ```

  ```
  space.type = global
  ```
  ```
* Find only site / favorite spaces

  ```
  ```
  1
  2
  ```

  ```
  space.type = favorite
  ```
  ```

#### Text

This is a "master-field" that allows you to search for text across a number of other text fields.
These are the same fields used by Confluence search user interface.

* [Title](http://developer.atlassian.com#Title)
* Content body
* [Labels](http://developer.atlassian.com#Labels)

Note: [Confluence text-search syntax](https://developer.atlassian.com/display/CONFDEV/Performing+text+searches+using+CQL) can be used with this field.

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

###### Field Type

TEXT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | No | Yes | Yes | No | No | No | No | No | No |

###### Supported Functions

none

###### Examples

* Find content that contains the word Confluence.

  ```
  ```
  1
  2
  ```

  ```
  text ~ Confluence
  ```
  ```
* Find content in the development space.

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

Note: [Confluence text-search syntax](https://developer.atlassian.com/display/CONFDEV/Performing+text+searches+using+CQL) can be used with this fields when used with the [CONTAINS](https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL#AdvancedSearchingusingCQL-CONTAINS:~) operator ("~~", "!~~")

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

###### Field Type

TEXT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | Yes | Yes | No | No | No | No | Yes | Yes |

###### Supported Functions

none

###### Examples

* Find content with the title "Advanced Searching using CQL".

  ```
  ```
  1
  2
  ```

  ```
  title = "Advanced Searching using CQL"
  ```
  ```
* Find content that matches Searching CQL (i.e. a "fuzzy" match).

  ```
  ```
  1
  2
  ```

  ```
  title ~ "Searching CQL"
  ```
  ```

#### Type

Search for content of a particular type. Supported content types are:

* page
* blogpost
* comment
* attachment

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

###### Field Type

TYPE

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

none

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

Search for content that a particular user is watching. You can search by the user's username.

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

###### Field Type

USER

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

* [currentUser()](https://developer.atlassian.com/display/CONFDEV/CQL+Function+Reference#CQLFunctionReference-currentUser())

###### Examples

* Search for content that you are watching.

  ```
  ```
  1
  2
  ```

  ```
  watcher = currentUser()
  ```
  ```
* Search for content that the user "jsmith" is watching.

  ```
  ```
  1
  2
  ```

  ```
  watcher = "jsmith"
  ```
  ```
