
# Modules and Plugins

Plugins are the individual pieces of functionality used in log paths. Examples include `file`, `csv-parser`, and `base64-encode`. Modules are groups of one or more plugins. The modules that the aforementioned plugins belong to are `affile`, `csvparser`, and `basicfuncs`, respectively.

Modules are stored in `modules/` as directories (e.g. `modules/affile/`). Inside these directories are files that integrate the module, files that handle parsing for the module, and files that implement the plugins of the module. Modules are dynamically loaded by syslog-ng (one `.so` file per module).

## Parts of a Module

A module contains:
* `*-plugin.c`, a file which defines the module
* `*-grammar.ym`, a Bison grammar file
* `*-parser.[ch]`, files which handle the module's parsing
* `*.[ch]`, plugin and plugin helper files
* `Makefile.am`, an Automake file
* `CMakeLists.txt`, a CMake file
* `tests/`, a test directory
	* `test_*.c`, Various Criterion tests
	* `Makefile.am`, an Automake file for the tests
	* `CMakeLists.txt`, a CMake file for the tests

## Plugin File

The structure of the `*-plugin.c` file is the same for every module, and it is also outside the scope of inividual plugins, so we will cover how it works here. We will use the plugin file for `affile` as an example.

The purpose of the plugin file is to integrate a module and its plugins into syslog-ng.

### `affile-plugin.c`
```
#include "cfg-parser.h"
#include "plugin.h"
#include "plugin-types.h"
#include "affile-dest.h"

/* The CfgParser for this module (defined in the *-parser.c file) */
extern CfgParser affile_parser;
```

Syslog-ng needs a list of the module's plugins, in the form of `Plugin` objects, so the syslog-ng parser knows how to parse them in the configuration file. `Plugin` objects are defined by:

1. A `type` field, which is the context/block a plugin belongs in (source, destination, parser, etc.). This is set to one of the tokens defined under `lib/cfg-grammar.y` (e.g. `LL_CONTEXT_SOURCE`).
2. A `name` field, which is the string used to declare the use of the plugin.
3. A `parser` field, which is the `CfgParser` used to parse the plugin. Usually this is just the `CfgParser` for the module.

When the syslog-ng parser encounters `name` inside a context/block of the type, `type`, it will use `parser` to parse the block.

In this snippet of a config file, for example, the syslog-ng parser sees that it is inside a source context/block (`LL_CONTEXT_SOURCE`), and finds the string `file`, so it uses the parser for that plugin, which is `affile_parser`, to parse the configuration block.

```
source s_local {
    file("/var/log/syslog");
};
```

The `affile` module contains many plugins, so its list is pretty long, but most modules only have one or two `Plugin` objects in their lists.
```
static Plugin affile_plugins[] =
{
  {
    .type = LL_CONTEXT_SOURCE,
    .name = "file",
    .parser = &affile_parser,
  },
  {
    .type = LL_CONTEXT_SOURCE,
    .name = "pipe",
    .parser = &affile_parser,
  },
  {
    .type = LL_CONTEXT_SOURCE,
    .name = "wildcard_file",
    .parser = &affile_parser,
  },
  {
    .type = LL_CONTEXT_SOURCE,
    .name = "stdin",
    .parser = &affile_parser,
  },
  {
    .type = LL_CONTEXT_DESTINATION,
    .name = "file",
    .parser = &affile_parser,
  },
  {
    .type = LL_CONTEXT_DESTINATION,
    .name = "pipe",
    .parser = &affile_parser,
  },
};
```

This function is called to initialise the module. It just needs a simple `plugin_register` call.
```
gboolean
affile_module_init(PluginContext *context, CfgArgs *args)
{
  plugin_register(context, affile_plugins, G_N_ELEMENTS(affile_plugins));

  /* Specific to affile; most modules just need the above call */
  affile_dd_global_init();

  return TRUE;
}
```

Finally we fill out the `ModuleInfo` for this module.
```
const ModuleInfo module_info =
{
  .canonical_name = "affile",
  .version = SYSLOG_NG_VERSION,
  .description = "The affile module provides file source & destination support for syslog-ng.",
  .core_revision = SYSLOG_NG_SOURCE_REVISION,
  .plugins = affile_plugins,
  .plugins_len = G_N_ELEMENTS(affile_plugins),
};
```

## Parser Files

The `*-parser.h` and `*-parser.c` files are included in the individual plugin sections, but we will do most of the explaining for them here. We will use the parser files for `affile` as examples.

The purpose of the parser files is to provide the module's parsing functionality and integrate it into syslog-ng. The module's parsing functionality is represented by a `CfgParser` object.

### `affile-parser.h`
```
#ifndef AFFILE_PARSER_H_INCLUDED
#define AFFILE_PARSER_H_INCLUDED

#include "cfg-parser.h"
#include "driver.h"
```

Here we declare the `CfgParser`. It is defined in the source file for the parser (`affile-parser.c`).
```
extern CfgParser affile_parser;
```

This macro function declares the Bison lex and error functions for this module's parser.
```
CFG_PARSER_DECLARE_LEXER_BINDING(affile_, LogDriver **)

#endif
```

### `affile-parser.c`
```
#include "driver.h"
#include "cfg-parser.h"
```

`affile-grammar.h` is the header for the Bison parser implementation file. The implementation file and header are generated by Bison at compile-time, based on the module's grammar file (`affile-grammar.ym` in this case).
```
#include "affile-grammar.h"

extern int affile_debug;
```

This is the Bison parser that comes from the generated implementation file.
```
int affile_parse(CfgLexer *lexer, LogDriver **instance, gpointer arg);
```

The lexer for the module's parser needs a list of keywords to recognize, so we create an array of `CfgLexerKeyword` objects. These are defined by the string to recognize, along with the corresponding token's numerical code. The tokens are defined in the `*-grammar.ym` file and Bison makes their numerical codes available through a macro of the same name, so that is what we use. The array is null-terminated.

The keywords of modules include those that declare the use of the plugins (the first block here), as well as those that set the options for the plugins (the other blocks here).
```
static CfgLexerKeyword affile_keywords[] =
{
  { "file",               KW_FILE },
  { "fifo",               KW_PIPE },
  { "pipe",               KW_PIPE },
  { "stdin",              KW_STDIN },

  { "wildcard_file",      KW_WILDCARD_FILE },
  { "base_dir",           KW_BASE_DIR },
  { "filename_pattern",   KW_FILENAME_PATTERN },
  { "recursive",          KW_RECURSIVE },
  { "max_files",          KW_MAX_FILES },
  { "monitor_method",     KW_MONITOR_METHOD },

  { "fsync",              KW_FSYNC },
  { "remove_if_older",    KW_OVERWRITE_IF_OLDER, KWS_OBSOLETE, "overwrite_if_older" },
  { "overwrite_if_older", KW_OVERWRITE_IF_OLDER },
  { "follow_freq",        KW_FOLLOW_FREQ },
  { "multi_line_mode",    KW_MULTI_LINE_MODE  },
  { "multi_line_prefix",  KW_MULTI_LINE_PREFIX },
  { "multi_line_garbage", KW_MULTI_LINE_GARBAGE },
  { "multi_line_suffix",  KW_MULTI_LINE_GARBAGE },
  { NULL }
};
```

Now we can define our `CfgParser`.
```
CfgParser affile_parser =
{
#if SYSLOG_NG_ENABLE_DEBUG
  .debug_flag = &affile_debug,
#endif
  .name = "affile",
  .keywords = affile_keywords,
  .parse = (gint (*)(CfgLexer *, gpointer *, gpointer)) affile_parse,
  .cleanup = (void (*)(gpointer)) log_pipe_unref,
};
```

Lastly we need to call this macro function to define our lex and error functions.
```
CFG_PARSER_IMPLEMENT_LEXER_BINDING(affile_, LogDriver **)
```

## Structs as Classes

Syslog-ng is written in C but simulates the funcitonality of classes and objects by using structs. 

The first field of any struct that represents a subclass is `super`. The type of `super` is the struct that represents the superclass. This type is not a pointer.

The result of making `super` the first field and not a pointer is that an object will have all the data for it and its superclasses stored in one contiguous block of memory, ordered from most abstract to the least. So if `C` inherits from `B` inherits from `A`, the memory layout of a `C` object would look like:
```
[[[Members of A] Members of B] Members of C]
```

The best way to learn how this is used in practice is to look at and work with the codebase.
