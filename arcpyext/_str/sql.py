# coding=utf-8
"""This module contains a class for formatting definition queries."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position,import-error,no-name-in-module

from sqlparse import engine
from sqlparse import filters
from sqlparse import filters, tokens
from sqlparse.compat import text_type
from sqlparse.exceptions import SQLParseError

__all__ = ["format_def_query"]


class IdentifierQuotesFilter(object):
    ttype = tokens.Name, tokens.String.Symbol

    def __init__(self, quote=None):
        self.quote = quote

    def convert(self, value):
        quote_chars = "\"'[]"
        if self.quote == "double":
            value = '"{}"'.format(value.strip(quote_chars))
        elif self.quote == "bracket":
            value = "[{}]".format(value.strip(quote_chars))
        elif self.quote == "strip":
            value = value.strip(quote_chars)
        return value

    def process(self, stream):
        for ttype, value in stream:
            if ttype in self.ttype:
                value = self.convert(value)
            yield ttype, value


class ExtendedIdentifierCaseFilter(object):
    convert = None
    ignore_quotes = False
    ttype = tokens.Name, tokens.String.Symbol

    def __init__(self, case=None):
        if case is None:
            # perform no conversion
            self.convert = lambda v: v
        else:
            case = case.lower()
            ignore_quotes_keywords = "_ignore_quotes"
            if case.endswith(ignore_quotes_keywords):
                self.ignore_quotes = True
                case = case[:-len(ignore_quotes_keywords)]
            self.convert = getattr(text_type, case)

    def process(self, stream):
        for ttype, value in stream:
            if ttype in self.ttype:
                if self.ignore_quotes == True or value.strip()[0] != '"':
                    value = self.convert(value)
            yield ttype, value


def build_filter_stack(options):
    stack = engine.FilterStack()

    if options.get("identifier_case"):
        stack.preprocess.append(ExtendedIdentifierCaseFilter(options['identifier_case']))

    if options.get("identifier_quotes"):
        stack.preprocess.append(IdentifierQuotesFilter(options['identifier_quotes']))

    return stack


def format_def_query(def_query, encoding=None, **options):
    """Format *sql* according to *options*.
    Available options are documented in :ref:`formatting`.
    In addition to the formatting options this function accepts the
    keyword "encoding" which determines the encoding of the statement.
    :returns: The formatted SQL statement as string.
    """
    options = validate_options(options)
    stack = build_filter_stack(options)
    stack.postprocess.append(filters.SerializerUnicode())
    return u''.join(stack.run(def_query, encoding))


def validate_options(options):
    identifier_case = options.get("identifier_case")
    if identifier_case not in [
            None, "upper", "upper_ignore_quotes", "lower", "lower_ignore_quotes", "capitalize",
            "capitalize_ignore_quotes"
    ]:
        raise SQLParseError("Invalid value for identifier_case: {0!r}".format(identifier_case))

    identifier_quotes = options.get("identifier_quotes")
    if identifier_quotes not in [None, "double", "bracket", "strip"]:
        raise SQLParseError("Invalid value for identifier_quotes: {0!r}".format(identifier_quotes))

    return options
