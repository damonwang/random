# *Macros in Python: pick at least one of unsafe, tedious, or illegible*

My [memoization code] [memo] defined two custom classes ClockRecord and HashRecord which were basically mutable namedtuples, written out manually.  Fed up with this manual macro expansion, I sat down yesterday to out a proper Record macro, and ended up implementing it twice: once by interpolating Python source code into a string, and again by generating the abstract syntax tree directly.  In other words, I implemented the [Record macro] [recoord-code] twice, once in the C macro style and again in the Lisp macro style.

## Literature review

Laziness being a programmer's virtue, I did first search for existing projects which implemented a Python macro language with some semblance of maturity and active development, and mainstream.  Unfortunately, the only two projects I could find which tried to implement a Python macro language were [Logix] [logix] and [MetaPython] [metapython].  On the maturity front, they were alpha and proof-of-concept, respectively.  Neither is maintained, although the MetaPython author has [offered to pass it to a new maintainer] [metapython-maintenance].  And as for mainstream integration, well, Logix didn't even claim to be Python anymore.  So I was on my own.

[memo]: <https://github.com/damonwang/random/tree/master/memoization> 

[record-code]: <https://github.com/damonwang/random/tree/master/record> 

[logix]: <http://logix-language.sourceforge.net/> 

[metapython]: <http://metapython.org/> 

[metapython-maintenance]: <http://groups.google.com/group/metapython/browse_thread/thread/4a83716c409eb012> "If anyone wants to take on the maintenance or has some project that really needs metapython, I'm open to either giving up the reigns or spending a little more time on it. "

References:
Why Lisp Macros are cool, a Perl perspective.
<http://lists.warhead.org.uk/pipermail/iwe/2005-July/000130.html>
