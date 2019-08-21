# Filter Function

This section will guide you through the process of creating a filter function, by going through the files of filter-length, a set of filter functions which filter log messages based on the length of their `${MESSAGE}`. `${MESSAGE}` refers to the syslog-ng macro and not MSG as defined by the syslog protocols.

Filter functions are written under `lib/filter/`, and so they do not belong to any module and are not technically plugins. To add a filter function we only need to modify the parser and grammar files; there is no plugin file.

### Example Config
```
source s_local {
    file("/tmp/input.log");
};

filter f_one_to_onehundred {
    len_gtle(0 100);

    # The old way of doing this:
    # "$(length ${MSG})" > "0" and "$(length ${MSG})" <= "100"
};

destination d_local {
    file("/tmp/output.log");
};

log {
    source(s_local);
    filter(f_one_to_onehundred);
    destination(d_local);
};
```

### UML Diagram

![](https://i.imgur.com/X3w29kA.png)

### `filter-expr-parser.c`

This is the parser file for filter functions. We add a `CfgLexerKeyword` for each of our filter functions to the list of keywords.

```
#include "filter/filter-expr-parser.h"
#include "filter/filter-expr-grammar.h"
#include "filter/filter-expr.h"

extern int filter_expr_debug;
int filter_expr_parse(CfgLexer *lexer, FilterExprNode **node, gpointer arg);

static CfgLexerKeyword filter_expr_keywords[] =
{
  { "or",                 KW_OR },
  { "and",                KW_AND },
  { "not",                KW_NOT },
  { "lt",                 KW_LT },
  { "le",                 KW_LE },
  { "eq",                 KW_EQ },
  { "ne",                 KW_NE },
  { "ge",                 KW_GE },
  { "gt",                 KW_GT },

  { "<",                  KW_NUM_LT   },
  { "<=",                 KW_NUM_LE   },
  { "==",                 KW_NUM_EQ   },
  { "!=",                 KW_NUM_NE   },
  { ">=",                 KW_NUM_GE   },
  { ">",                  KW_NUM_GT   },
  { "level",              KW_LEVEL    },
  { "priority",           KW_LEVEL    },
  { "facility",           KW_FACILITY },
  { "program",            KW_PROGRAM  },
  { "host",               KW_HOST     },
  { "message",            KW_MESSAGE  },
  { "match",              KW_MATCH    },
  { "netmask",            KW_NETMASK  },
  { "tags",               KW_TAGS     },
  { "in_list",            KW_IN_LIST  },
#if SYSLOG_NG_ENABLE_IPV6
  { "netmask6",     KW_NETMASK6 },
#endif

  { "value",              KW_VALUE },
  { "flags",              KW_FLAGS },

  /* Our keywords */
  { "len_lt",             KW_LEN_LT   },
  { "len_le",             KW_LEN_LE   },
  { "len_gt",             KW_LEN_GT   },
  { "len_ge",             KW_LEN_GE   },
  { "len_eq",             KW_LEN_EQ   },
  { "len_ne",             KW_LEN_NE   },
  { "len_gtlt",           KW_LEN_GTLT },
  { "len_gtle",           KW_LEN_GTLE },
  { "len_gelt",           KW_LEN_GELT },
  { "len_gele",           KW_LEN_GELE },

  { NULL }
};

CfgParser filter_expr_parser =
{
#if SYSLOG_NG_ENABLE_DEBUG
  .debug_flag = &filter_expr_debug,
#endif
  .name = "filter expression",
  .context = LL_CONTEXT_FILTER,
  .keywords = filter_expr_keywords,
  .parse = (gint (*)(CfgLexer *, gpointer *, gpointer)) filter_expr_parse,
};

CFG_PARSER_IMPLEMENT_LEXER_BINDING(filter_expr_, FilterExprNode **)
```

### `filter-expr-grammar.ym`

This is the grammar file for filter functions. We add a token and grammar rule for each of our filter functions.
```
/* ... */

%token KW_LEN_LT
%token KW_LEN_LE
%token KW_LEN_GT
%token KW_LEN_GE
%token KW_LEN_EQ
%token KW_LEN_NE
%token KW_LEN_GTLT
%token KW_LEN_GTLE
%token KW_LEN_GELT
%token KW_LEN_GELE

/* ... */

filter_simple_expr
	: KW_FACILITY '(' filter_fac_list ')'       { $$ = filter_facility_new($3);  }
	| KW_FACILITY '(' LL_NUMBER ')'             { $$ = filter_facility_new(0x80000000 | $3); }
	| KW_LEVEL    '(' filter_level_list ')'     { $$ = filter_level_new($3); }
	| KW_FILTER   '(' string ')'                { $$ = filter_call_new($3, configuration); free($3); }
	| KW_LEN_LT   '(' LL_NUMBER ')'             { $$ = filter_len_lt_new($3); }
	| KW_LEN_LE   '(' LL_NUMBER ')'             { $$ = filter_len_le_new($3); }
	| KW_LEN_GT   '(' LL_NUMBER ')'             { $$ = filter_len_gt_new($3); }
	| KW_LEN_GE   '(' LL_NUMBER ')'             { $$ = filter_len_ge_new($3); }
	| KW_LEN_EQ   '(' LL_NUMBER ')'             { $$ = filter_len_eq_new($3); }
	| KW_LEN_NE   '(' LL_NUMBER ')'             { $$ = filter_len_ne_new($3); }
	| KW_LEN_GTLT '(' LL_NUMBER LL_NUMBER ')'   { $$ = filter_len_gtlt_new($3, $4); }
	| KW_LEN_GTLE '(' LL_NUMBER LL_NUMBER ')'   { $$ = filter_len_gtle_new($3, $4); }
	| KW_LEN_GELT '(' LL_NUMBER LL_NUMBER ')'   { $$ = filter_len_gelt_new($3, $4); }
	| KW_LEN_GELE '(' LL_NUMBER LL_NUMBER ')'   { $$ = filter_len_gele_new($3, $4); }

/* ... */
```

### `filter-length.h`
```
#ifndef FILTER_LENGTH_H_INCLUDED
#define FILTER_LENGTH_H_INCLUDED

#include "filter/filter-expr.h"

/* Single comparison filter-length functions */
FilterExprNode *filter_len_lt_new(int length);
FilterExprNode *filter_len_le_new(int length);
FilterExprNode *filter_len_gt_new(int length);
FilterExprNode *filter_len_ge_new(int length);
FilterExprNode *filter_len_eq_new(int length);
FilterExprNode *filter_len_ne_new(int length);

/* Range comparison filter-length functions */
FilterExprNode *filter_len_gtlt_new(int min, int max);
FilterExprNode *filter_len_gtle_new(int min, int max);
FilterExprNode *filter_len_gelt_new(int min, int max);
FilterExprNode *filter_len_gele_new(int min, int max);

#endif
```

### `filter-length.c`

Filter function classes extend `FilterExprNode`. `FilterExprNode` has abstract methods `init`, `free_fn`, and `eval`. `eval` contains the main functionality of filter functions; it is what determines if a log message passes the filter or not.

The reason why filter functions are "expression nodes" is because a filter expression in the config file is made up of one or more filter statements, connected by logical operators. So, when a filter expression is parsed, it gets represented as a `FilterExprNode` binary tree, to make calculating the result simple (this is all handled by the existing code in `lib/filter/` and we don't need to do anything special in our implementation).

We need to create two filter function classes for `filter-length`: one for single length comparisons and one for range-based comparisons.
```
#include "filter-length.h"

typedef struct _FilterLengthSingle
{
  FilterExprNode super;
  gint length;
} FilterLengthSingle;

typedef struct _FilterLengthRange
{
  FilterExprNode super;
  gint min;
  gint max;
} FilterLengthRange;
```

In the actual code, we use a macro function to generate the code needed for our filter functions, since for each type (single and range) the only thing that changes is the comparison operator(s) used. But for this guide we will just look at a single example of each type, implemented without any macros.

First we have the `new` function for our single comparison filter functions. Our filter function does not have anything that needs to be initialised, nor any fields that use dynamic memory, so we only implement and set the `eval` method, not `init` or `free_fn`.
```
FilterExprNode *
filter_len_lt_new(gint length)
{
  FilterLengthSingle *self = g_new0(FilterLengthSingle, 1);
  filter_expr_node_init_instance(&self->super);
  self->super.eval = filter_len_lt_eval;
  self->length = length;
  return &self->super;
}
```

Here is the `eval` method for our single comparison filter functions. The first parameter is a `FilterExprNode` representing the filter function. The second parameter is a `LogMessage` pointer array and the third parameter is the index of the `LogMessage` to evaluate.
```
static gboolean
filter_len_lt_eval(FilterExprNode *s, LogMessage **msgs, gint num_msg)
{
  FilterLengthSingle *self = (FilterLengthSingle *) s;
  gboolean result;
```
    
First we need to get the message we want from the array. `num_msg` starts counting from one, so `num_msg` less one gives us the index for the `LogMessage` to evaluate.
```
  LogMessage *msg = msgs[num_msg - 1];
```

Now that we have our `LogMessage`, we will extract the `${MESSAGE}` part from it to evaluate its length. To do so, we call the `log_msg_get_value` function with the appropriate constant.
```
  const gchar *message_part = log_msg_get_value(msg, LM_V_MESSAGE, NULL);
```
Finally we can calculate our result.
```
  result = (gint) strlen(message_part) < self->length;
```

`FilterExprNode` has a bit field `comp` (complement), which when on, tells the filter function to negate its results (i.e. negate the return value of `eval`). It is switched on when a logical NOT operator is applied to the filter function in a filter expression. So, before we return our result, we need to bitwise XOR it with `comp`.
```
  return result ^ s->comp;
}
```

This is an example range-based filter function. There are just a few differences from the single comparison filter function, so we will skip over this part.
```
static gboolean
filter_len_gtlt_eval(FilterExprNode *s, LogMessage **msgs, gint num_msg)
{
  FilterLengthRange *self = (FilterLengthRange *) s;
  gboolean result;

  LogMessage *msg = msgs[num_msg - 1];
  const gchar *message_part = log_msg_get_value(msg, LM_V_MESSAGE, NULL);
  result = ((gint) strlen(message_part) > self->min) &&
           ((gint) strlen(message_part) < self->max);
  return result ^ s->comp;
}

FilterExprNode *
filter_len_gtlt_new(gint min, gint max)
{
  FilterLengthRange *self = g_new0(FilterLengthRange, 1);
  filter_expr_node_init_instance(&self->super);
  self->super.eval = filter_len_gtlt_eval;
  self->min = min;
  self->max = max;
  return &self->super;
}
```


### `test_filters_length.c`

```
#include "filter/filter-expr.h"
#include "filter/filter-length.h"
#include "cfg.h"
#include "test_filters_common.h"

#include <criterion/criterion.h>
#include <criterion/parameterized.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/* Use the setup and teardown functions provided in test_filters_common.h */
TestSuite(filter, .init = setup, .fini = teardown);
```

Because our filter functions always have the same input and output structure, we will use Criterion's parameterized tests. There is one for each of our filter functions, but for this guide we will just look at the test for a single comparison filter function.
```
#include "filter/filter-expr.h"
#include "filter/filter-length.h"
#include "cfg.h"
#include "test_filters_common.h"

#include <criterion/criterion.h>
#include <criterion/parameterized.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/* Use the setup and teardown functions provided in test_filters_common.h */
TestSuite(filter, .init = setup, .fini = teardown);
```

This is the struct for holding our test parameters.
```
typedef struct _FilterParamLengthSingle
{
  const gchar *msg;
  gint length;
  gboolean expected_result;
} FilterParamLengthSingle;
```

This is the Criterion function that generates the parameters for our tests. All we need to do is create an array of our `FilterParamLengthSingle`, and pass it into a `cr_make_param_array` call, and return the value of the function.

The other test files for filter functions use some variation of an openvpn log message as test messages, so we will do the same.
```
ParameterizedTestParameters(filter, test_filter_len_lt)
{
  static FilterParamLengthSingle test_data_list[] =
    {
      {.msg = "",                                                 .length = 0,   .expected_result = FALSE},
      {.msg = "<15> openvpn[2499]: ",                             .length = -1,  .expected_result = FALSE},
      {.msg = "<15> openvpn[2499]: PTHREAD support initialized",  .length = 26,  .expected_result = FALSE},
      {.msg = "<15> openvpn[2499]: PTHREAD support initialized",  .length = 27,  .expected_result = FALSE},
      {.msg = "<15> openvpn[2499]: PTHREAD support initialized",  .length = 28,  .expected_result = TRUE},
    };

  return cr_make_param_array(FilterParamLengthSingle, test_data_list,  G_N_ELEMENTS(test_data_list));
}
```

Here is our actual parameterized test. After creating a new `FilterExprNode` of the type we are testing (`filter_len_lt`), we call `testcase` to do all the actual testing. It comes from `test_filters_common.c`.
```
ParameterizedTest(FilterParamLengthSingle *param, filter, test_filter_len_lt)
{
  FilterExprNode *filter = filter_len_lt_new(param->length);
  testcase(param->msg, filter, param->expected_result);
}
```
