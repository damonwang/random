# Macros in Python: pick at least one of unsafe, tedious, or illegible

My [memoization code] [memo] defined two custom classes ClockRecord and HashRecord which were basically mutable namedtuples, written out manually.  Fed up with this manual macro expansion, I sat down yesterday to out a proper Record macro, and ended up implementing it twice: once by interpolating Python source code into a string, and again by generating the abstract syntax tree directly.  In other words, I implemented the [Record macro] [record-code] twice, once in the C macro style and again in the Lisp macro style.

## C-style macro implementation

The C-style implementation was a very straightforward tweak of the collections.namedtuple code, with the slight improvement of validating field names by checking that they parse as valid Python ast.Name nodes.  This protects against both template injection attacks and also general mistakes, and I like to think it would be a little more reliable and future-proof than rolling your own validation.

But C-style macros are fragile, limited things even in C, and they only get worse when applied in a whitespace-sensitive language that distinguishes expressions from statements.  I couldn't even get a multi-line interpolation to work reliably, because indentation matters.  As a result, I was pretty much limited to expressions and single statements.

## Lisp-style macro implementation

The Lisp-style implementation was much more tedious, since Python has a reasonably complex grammar and therefore writing out an abstract syntax tree using the raw constructors gets to be a very verbose process.  Here's the AST for generating a one-line "return dict(a=1, b=2)" function:

    FunctionDef(name='as_dict', decorator_list=[],
      args=__AST_only_self_as_arg__,
      body=[
        docstring('return a new dict representing the same key->value mapping'),
        Return(value=Call(args=[], starargs=None, kwargs=None,
          keywords=[
            keyword(arg=field,
              value=Attribute(attr=field, ctx=Load(), 
                value=Name(id='self', ctx=Load())))
              for field in field_names],
          func=Name(id='dict', ctx=Load())))])

Lisp has both great macros and basically no syntax, and apparently this is not a coincidence.

## Literature review

Laziness being a programmer's virtue, I did first search for existing projects which implemented a Python macro language with some semblance of maturity and active development, and mainstream.  Unfortunately, the only two projects I could find which tried to implement a Python macro language were [Logix] [logix] and [MetaPython] [metapython].  On the maturity front, they were alpha and proof-of-concept, respectively.  Neither is maintained, although the MetaPython author has [offered to pass it to a new maintainer] [metapython-maintenance].  And as for mainstream integration, well, Logix didn't even claim to be Python anymore.  So I was on my own.

[memo]: <https://github.com/damonwang/random/tree/master/memoization> 

[record-code]: <https://github.com/damonwang/random/tree/master/record> 

[logix]: <http://logix-language.sourceforge.net/> 

[metapython]: <http://metapython.org/> 

[metapython-maintenance]: <http://groups.google.com/group/metapython/browse_thread/thread/4a83716c409eb012> "If anyone wants to take on the maintenance or has some project that really needs metapython, I'm open to either giving up the reigns or spending a little more time on it. "
