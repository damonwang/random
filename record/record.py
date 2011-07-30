import sys 
import ast
import _ast

class_template = '''
from collections import namedtuple
class {typename} (object):
    '{typename}({fields_as_args})'

    __slots__ = {fields}

    def __init__(self{fields_as_args}):
        {init}
    def __repr__(self):
        'return a nicely formatted representation string'
        return '{repr_format}'.format({field_values})

    def as_dict(self):
        'return a new dict representing the same key->value mapping'
        return dict({field_values})

    def but_with(self{fields_as_args}):
        \'\'\'
        a functional update: return a new record, filling in unspecified
        fields with the corresponding values in this record.
        \'\'\'
        return {typename}({field_values_as_defaults})
'''

def specialize_class(typename, field_names):
  if len(field_names) > 0:
    # hence the strange "self{fields_as_args syntax in the template
    fields_as_args = ', ' + ', '.join('%s=None' % field for field in field_names)
    # this strange tuple assignment syntax is but necessary because
    # making the indentation work out across multiple lines is difficult
    # (This is clearly a limitation of the technique that will
    # become more of a problem if we try to generalize it into a
    # macro system.)
    init = '%s = %s' % (
      ', '.join('self.%s' % field for field in field_names),
      ', '.join('%s' % field for field in field_names))
  else: fields_as_args, init = '', 'pass'

  return class_template.format(
      typename=typename,
      fields = repr(tuple(field_names)),
      fields_as_args = fields_as_args,
      init = init,
      repr_format = '{typename}({values})'.format(
        typename=typename,
        values = ', '.join('%s={%s}' % (field, field) 
          for field in field_names)),
      field_values = ', '.join('%s=self.%s' % (field, field)
        for field in field_names),
      field_values_as_defaults = 
      ', '.join('{field} = {field} or self.{field}'.format(field=field)
        for field in field_names)
      )

as_namedtuple_template = '''
    immutable_form = namedtuple('Immutable{typename}', __slots__)

    def as_namedtuple(self):
        'return an immutable copy using collections.namedtuple.'
        return self.immutable_form({field_values})
'''

def specialize_as_namedtuple(typename, field_names):
  return as_namedtuple_template.format(
      typename=typename,
      field_values = ', '.join('%s=self.%s' % (field, field)
        for field in field_names))

def unsafe_define(typename, field_names, as_namedtuple=True):
    class_definition = specialize_class(typename, field_names)
    if as_namedtuple: 
      class_definition += specialize_as_namedtuple(typename, field_names)
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
