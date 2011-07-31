import ast 

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

def get_ast(typename, field_names, as_namedtuple=True):
    class_definition = specialize_class(typename, field_names)
    if as_namedtuple: 
      class_definition += specialize_as_namedtuple(typename, field_names)
    return compile(class_definition, filename='Record_%s' % typename,
      mode='exec')

