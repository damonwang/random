import sys 
import ast
import _ast
from ast_record import get_ast

def unsafe_define(typename, field_names, as_namedtuple=True):

    class_definition = get_ast(typename, field_names, as_namedtuple)
    namespace = dict(__name__='Record_%s' % typename)

    # the following lines are closely copied from collections.namedtuple
    try: exec(class_definition, namespace)
    except SyntaxError as e:
        raise SyntaxError(e.msg + ':\n\n' + class_definition)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the
    # frame
    # where the named tuple is created. Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try: frame_globals = sys._getframe(1).f_globals
    except (AttributeError, ValueError): pass
    result.__module__ = frame_globals.get('__name__', '__main__')

    return result


class WouldShadowExistingAttribute (Exception): pass
class InvalidName (Exception): pass

def get_existing_attributes():
  # TODO fix the zero-fields bug and them remove the if not 'foo' clause
  return [x for x in dir(unsafe_define('Foo', ('foo',))) if x != 'foo']

existing_attributes = set(get_existing_attributes())

def make_safe_id(string):
  try: node = ast.parse(string).body[0].value
  except Exception as e: raise InvalidName(string, e)
  if not isinstance(node, _ast.Name):
    raise InvalidName(string)
  elif node.id in existing_attributes:
    raise WouldShadowExistingAttribute(string)
  else: return node.id

class Record (object):
  '''
  Names may be anything AST.parse will accept for an _ast.Name object,
  although we will try (but not promise!) to throw an exception if you
  shadow an existing method (e.g., __repr__).

  Note that this means not all record objects can be cleanly converted
  into namedtuples.  If we detect that namedtuple would reject a field
  name, no as_namedtuple method will be generated.
  '''

  @staticmethod
  def define(typename, field_names, allow_leading_underscores=True):
    typename = make_safe_id(typename)
    field_names = map(make_safe_id, field_names)
    if not filter(lambda s: s[0] == '_', field_names): 
      # no underscores in field names
      return unsafe_define(typename, field_names)
    elif allow_leading_underscores: 
      return unsafe_define(typename, field_names, as_namedtuple=False)
    else: raise InvalidName
