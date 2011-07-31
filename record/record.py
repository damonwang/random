import sys 
import ast
import _ast
from ast_record import get_ast

def unsafe_define(typename, field_names, as_namedtuple=True):
    'does all the work.  Makes no attempt to sanity-check arguments.'

    class_definition = get_ast(typename, field_names, as_namedtuple)
    namespace = dict(__name__='Record_%s' % typename)

    # the following lines are closely copied from collections.namedtuple
    try: exec(class_definition, namespace)
    except SyntaxError as e:
        raise SyntaxError(e.msg + ':\n\n' + class_definition)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created. Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try: frame_globals = sys._getframe(1).f_globals
    except (AttributeError, ValueError): pass
    result.__module__ = frame_globals.get('__name__', '__main__')

    return result


class ExistingAttributeError (Exception): pass
class InvalidNameError (Exception): pass

existing_attributes = set(dir(unsafe_define('Foo', ())))

def make_safe_id(string):
  '''
  checks that the given field name parses as a Python identifier and
  will not shadow an existing attribute.  Also protects against template
  injection.
  '''

  try: node = ast.parse(string).body[0].value
  except Exception as e: raise InvalidNameError(string, e)

  if not isinstance(node, _ast.Name):
    raise InvalidNameError(string)
  elif node.id in existing_attributes:
    raise ExistingAttributeError(string)
  else: return node.id

class Record (object):

  @staticmethod
  def define(typename, field_names, allow_leading_underscores=True):
    '''
    define(typename, field_names, allow_leading_underscores=True)

    Returns:
    - a class named `typename` with fields from `field_names`

    Note that we are more permissive than collections.namedtuple in what
    constitutes a valid field name.  This means not all record objects
    can be cleanly converted into namedtuples.  If we detect that
    namedtuple would reject a field name, no as_namedtuple method will
    be generated.

    Raises:
    - InvalidNameError when a field name does not parse as a valid Python
      identifier, and, if `allow_leading_underscores` is False, also
      when a field name begins with `_`.
    - ExistingAttributeError when a field name would shadow an existing
      attribute (e.g., `__repr__`).

    Example:
    > Foo = Record.define('Foo', ('bar', 'baz'))
    > foo = Foo(bar=1, baz=2)
    > foo.bar
    1
    '''

    typename = make_safe_id(typename)
    field_names = map(make_safe_id, field_names)
    if not filter(lambda s: s[0] == '_', field_names): 
      # no underscores in field names
      return unsafe_define(typename, field_names)
    elif allow_leading_underscores: 
      return unsafe_define(typename, field_names, as_namedtuple=False)
    else: raise InvalidNameError
