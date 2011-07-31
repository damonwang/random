import ast
from _ast import *

def get_ast(typename, field_names, as_namedtuple=True):

  docstring = lambda s: Expr(value=Str(s=s))

  slots = Assign(targets=[Name(id='__slots__', ctx=Store())],
          value=Tuple(ctx=Load(), elts=[Str(s=field) for field in field_names] ))

  __AST_only_self_as_arg__ = arguments(varargs=[], kwargs=[], defaults=[],
        args=[Name(id='self', ctx=Param())])

  __AST_self_and_fields_as_args__ = arguments(varargs=[], kwargs=[],
        args= [Name(id='self', ctx=Param())]
        + [Name(id=field, ctx=Param()) for field in field_names],
        defaults=[Name(id='None', ctx=Load()) for x in field_names])

  __AST_fields_as_keywords__ = [ 
      keyword(arg=field, 
      value=Attribute(attr=field, ctx=Load(), value=Name(id='self', ctx=Load())))
      for field in field_names]

  def_init = FunctionDef(name='__init__', decorator_list=[],
      args=__AST_self_and_fields_as_args__,
      body=[
        Assign(
          targets=[
            Attribute(attr=field, ctx=Store(),
              value=Name(id='self', ctx=Load()))],
            value=Name(id=field, ctx=Load()))
        for field in field_names]
        if len(field_names) > 0 else [Pass()])

  def_repr = FunctionDef(name='__repr__', decorator_list=[],
      args=__AST_only_self_as_arg__,
      body=[
        docstring('return a nicely formatted representation string'),
        Return(value=Call(args=[], starargs=None, kwargs=None,
          keywords=__AST_fields_as_keywords__,
          func=Attribute(attr='format', ctx=Load(),
            value=Str(s='{typename}({values})'.format(
              typename=typename,
              values=', '.join('%s={%s}' % (f, f) for f in field_names))))))])

  def_as_dict = FunctionDef(name='as_dict', decorator_list=[],
      args=__AST_only_self_as_arg__,
      body=[
        docstring('return a new dict representing the same key->value mapping'),
        Return(value=Call(args=[], starargs=None, kwargs=None,
          keywords=__AST_fields_as_keywords__,
          func=Name(id='dict', ctx=Load())))])

  def_but_with = FunctionDef(name='but_with', decorator_list=[],
      args=__AST_self_and_fields_as_args__,
      body=[
        docstring('''
        a functional update: return a new record, filling in unspecified
        fields with the corresponding values in this record.
        '''),
        Return(value=Call(args=[], starargs=None, kwargs=None,
          func=Name(id=typename, ctx=Load()),
          keywords=[
            keyword(arg=field, 
              value=BoolOp(op=Or(), 
                values=[Name(id=field, ctx=Load()),
                  Attribute(attr=field, ctx=Load(),
                    value=Name(id='self', ctx=Load()))]))
            for field in field_names]))])

  class_def = ClassDef(
      name=typename, 
      bases=[Name(id='object', ctx=Load())], 
      decorator_list=[],
      body=[
        docstring('{typename}({fields})'.format(typename=typename,
          fields=', '.join('%s' % field for field in field_names))),
        slots,
        def_init,
        def_repr,
        def_as_dict,
        def_but_with,
        ])

  if as_namedtuple:
    class_def.body.extend([
      ImportFrom(module='collections', 
        names=[alias(name='namedtuple', asname=None)], level=0),
      Assign(targets=[Name(id='immutable_form', ctx=Store())],
        value=Call(keywords=[], stargs=None, kwargs=None,
          func=Name(id='namedtuple', ctx=Load()),
          args=[Str(s='Immutable%s' % typename), 
            Name(id='__slots__', ctx=Load())])),
      FunctionDef(name='as_namedtuple', decorator_list=[],
        args=__AST_only_self_as_arg__,
        body=[
          docstring('return an immutable copy using collections.namedtuple.'),
          Return(value=Call(args=[], starargs=None, kwargs=None,
            keywords=__AST_fields_as_keywords__,
            func=Attribute(attr='immutable_form', ctx=Load(),
              value=Name(id='self', ctx=Load()))))])])
        
  return compile(filename='Record_%s' % typename, mode='exec',
      source=ast.fix_missing_locations(Module(body=[class_def], 
        lineno=1, col_offset=0)))
