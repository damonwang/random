from itertools import count

def lex(source):
  acc = []
  for c in source:
    if c == ' ': 
      if acc != []: yield ''.join(acc)
      acc = []
    elif c in '()':
      if acc != []: yield ''.join(acc)
      yield c
      acc = []
    else: acc.append(c)

# type sexp_t = 
# | List of sexp_t list
# | Atom of string

# [parse_list] consumes tokens from the lexer, trying to parse a single
# "level" of list at a time, where elements of that level may be either
# atoms or lists.  It returns a function [f] that knows how to parse a
# sexp out of at least the next token, and possibly many more.  The
# function [f] closes over a function [g] that can integrate the
# resulting sexp into what has previously been seen.  When [f] has
# parsed all it can, it calls [g], which returns the next [f].

def parse_list(cc, tokens):
  this_list = []
  for tok in tokens:
    if tok == ')': return cc(this_list)
    elif tok != '(': this_list.append(tok)
    else: # next element is a sublist
      def f(sublist):
        this_list.append(sublist)
        def g(rest_of_list):
          this_list.extend(rest_of_list)
          return cc(this_list)
        return lambda tokens: parse_list(g, tokens)
      return lambda tokens: parse_list(f, tokens)
  return cc(this_list)

def parse(source):
  tokens = lex(source)
  cc = parse_list(lambda x: x, tokens)
  while callable(cc):
    cc = cc(tokens)
  return cc
