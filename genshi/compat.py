# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2009 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://genshi.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://genshi.edgewall.org/log/.

"""Various Python version compatibility classes and functions."""

import _ast
import sys
from types import CodeType


IS_PYTHON2 = (sys.version_info[0] == 2)


# This function should only be called in Python 2, and will fail in Python 3

if IS_PYTHON2:
    def stringrepr(string):
        ascii = string.encode('ascii', 'backslashreplace')
        quoted = "'" +  ascii.replace("'", "\\'") + "'"
        if len(ascii) > len(string):
            return 'u' + quoted
        return quoted
else:
    def stringrepr(string):
        raise RuntimeError(
                'Python 2 compatibility function. Not usable in Python 3.')


# We need to test if an object is an instance of a string type in places

if IS_PYTHON2:
    def isstring(obj):
        return isinstance(obj, basestring)
else:
    def isstring(obj):
        return isinstance(obj, str)

# We need to differentiate between StringIO and BytesIO in places

if IS_PYTHON2:
    from StringIO import StringIO
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        BytesIO = StringIO
else:
    from io import StringIO, BytesIO


# We want to test bytestring input to some stuff.

if IS_PYTHON2:
    def wrapped_bytes(bstr):
        assert bstr.startswith('b')
        return bstr[1:]
else:
    def wrapped_bytes(bstr):
        assert bstr.startswith('b')
        return bstr


# We do some scary stuff with CodeType() in template/eval.py

if IS_PYTHON2:
    def get_code_params(code):
        return (code.co_nlocals, code.co_stacksize, code.co_flags,
                code.co_code, code.co_consts, code.co_names, code.co_varnames,
                code.co_filename, code.co_name, code.co_firstlineno,
                code.co_lnotab, (), ())

    def build_code_chunk(code, filename, name, lineno):
        return CodeType(0, code.co_nlocals, code.co_stacksize,
                        code.co_flags | 0x0040, code.co_code, code.co_consts,
                        code.co_names, code.co_varnames, filename, name,
                        lineno, code.co_lnotab, (), ())
else:
    def get_code_params(code):
        params = [code.co_nlocals, code.co_kwonlyargcount, code.co_stacksize,
                  code.co_flags, code.co_code, code.co_consts, code.co_names,
                  code.co_varnames, code.co_filename, code.co_name,
                  code.co_firstlineno, code.co_lnotab, (), ()]
        if hasattr(code, "co_posonlyargcount"):
            # PEP 570 added "positional only arguments"
            params.insert(1, code.co_posonlyargcount)
        return tuple(params)


    def build_code_chunk(code, filename, name, lineno):
        params =  [0, code.co_nlocals, code.co_kwonlyargcount,
                  code.co_stacksize, code.co_flags | 0x0040,
                  code.co_code, code.co_consts, code.co_names,
                  code.co_varnames, filename, name, lineno,
                  code.co_lnotab, (), ()]
        if hasattr(code, "co_posonlyargcount"):
            # PEP 570 added "positional only arguments"
            params.insert(2, code.co_posonlyargcount)
        return CodeType(*params)


# In Python 3.8, Str and Ellipsis was replaced by Constant

try:
    _ast_Ellipsis = _ast.Ellipsis
    _ast_Str = _ast.Str
    _ast_Str_value = lambda obj: obj.s
except AttributeError:
    _ast_Ellipsis = _ast_Str = _ast.Constant
    _ast_Str_value = lambda obj: obj.value


# Compatibility fallback implementations for Python < 2.6

try:
    next = next
except NameError:
    def next(iterator):
        return iterator.next()

# Compatibility fallback implementations for Python < 2.5

try:
    all = all
    any = any
except NameError:
    def any(S):
        for x in S:
            if x:
                return True
        return False

    def all(S):
        for x in S:
            if not x:
                return False
        return True
