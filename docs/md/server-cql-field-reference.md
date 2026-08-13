<!-- archived from https://developer.atlassian.com/server/confluence/cql-field-reference/ -->

# CQL field reference

A field in CQL is a word that represents an indexed property of content in Confluence. In a clause, a field is followed by an [operator](/server/confluence/advanced-searching-using-cql#operator), which in turn is followed by one or more values (or [functions](/server/confluence/cql-function-reference#function)). The operator compares the value of the field
with one or more values or functions on the right, such that only true results are retrieved by the clause.

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

Search for all pages that are descendants of a given ancestor page. This includes direct child pages and their descendants.
It is more general than the parent field.

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

* Find all descendant pages with a given ancestor page.

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

Search for content that is contained in the content with the given ID.

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

Search for content that have a given content ID.
This is an alias of the ID field.

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

Search for content that was created on, before, or after a particular date (or date range).

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

* [endOfDay()](/server/confluence/cql-function-reference/#end-of-day)
* [endOfMonth()](/server/confluence/cql-function-reference/#end-of-month)
* [endOfWeek()](/server/confluence/cql-function-reference/#end-of-week)
* [endOfYear()](/server/confluence/cql-function-reference/#end-of-year)
* [startOfDay()](/server/confluence/cql-function-reference/#start-of-day)
* [startOfMonth()](/server/confluence/cql-function-reference/#start-of-month)
* [startOfWeek()](/server/confluence/cql-function-reference/#start-of-week)
* [startOfYear()](/server/confluence/cql-function-reference/#start-of-year)

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

* [currentUser()](/server/confluence/cql-function-reference/#current-user)

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

* [currentUser()](/server/confluence/cql-function-reference/#current-user)

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

* [currentUser()](/server/confluence/cql-function-reference/#current-user)

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

###### Field Type

CONTENT

###### Supported Operators

| = | != | ~ | !~ | > | >= | < | <= | IN | NOT IN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | No | No | No | No | No | No | Yes | Yes |

###### Supported Functions

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

* Find content that has the label 'finished'.

  ```
  ```
  1
  2
  ```

  ```
  label = finished
  ```
  ```
* Find content that doesn't have the label 'draft' or 'review'.

  ```
  ```
  1
  2
  ```

  ```
  label not in (draft, review)
  ```
  ```

#### Last modified

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

* [endOfDay()](/server/confluence/cql-function-reference/#end-of-day)
* [endOfMonth()](/server/confluence/cql-function-reference/#end-of-month)
* [endOfWeek()](/server/confluence/cql-function-reference/#end-of-week)
* [endOfYear()](/server/confluence/cql-function-reference/#end-of-year)
* [startOfDay()](/server/confluence/cql-function-reference/#start-of-day)
* [startOfMonth()](/server/confluence/cql-function-reference/#start-of-month)
* [startOfWeek()](/server/confluence/cql-function-reference/#start-of-week)
* [startOfYear()](/server/confluence/cql-function-reference/#start-of-year)

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
* Find content that was last modified on or after 1st September, but before 9am on 3rd September 2014.

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

* Find content that has the Jira issue macro.

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

* [currentUser()](/server/confluence/cql-function-reference/#current-user)

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
| Yes | Yes | No | No | No | No | No | No | No | No |

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
These are the same fields used by Confluence's search user interface.

* Title
* Content body
* Labels

Note: [Confluence text-search syntax](/server/confluence/performing-text-searches-using-cql) can be used with this field.

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

Note: [Confluence text-search syntax](/server/confluence/performing-text-searches-using-cql) can be used with this fields when used with the [CONTAINS](/server/confluence/advanced-searching-using-cql/#contains) operator ("~~", "!~~")

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
* Find content that matches Searching CQL (i.e. a "fuzzy" match):

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

* Find blogposts or pages.

  ```
  ```
  1
  2
  ```

  ```
  type IN (blogpost, page)
  ```
  ```
* Find attachments.

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

* [currentUser()](/server/confluence/cql-function-reference/#current-user)

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
