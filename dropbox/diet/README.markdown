# NOTE

In case you found this via Google or something, note that what follows is incorrect.  The diet problem is actually an example of the subset-sum problem; there is a well-documented dynamic programming solution, but it is not the one I describe below.

# Dropbox Diet Challenge

This is the third of three problems posed by Dropbox.  Stripped of its cutesy recruiting pitch about finding calorie-neutral combinations of (free) food and (paid) work, the problem is this: *given a set of integers U and its cardinality n, return a subset S whose sum is zero or decide that no such subset exists.*

The naive solution (try all possible subsets) runs in O(2^n) time.  However, we can infer a faster solution by solving a slightly harder problem.  Our harder problem admits a simple dynamic programming solution in O(n^2) time, and can be parallelized to run in O(n) time given an unlimited number of processors or in O(n^2 / p) time for a fixed p number of processors.

Unfortunately, all of these runtimes are purely theoretical, and therefore extremely optimistic.  If anyone would like to contribute some experimental data, be my guest.

## Problem (Re)Statement

Let's solve a slightly different problem: *given a set of integers U and its cardinality n, return the subset S whose sum is closest to zero.*

First, our problem is always solvable.  We are asking for a minimum element over a set of integers, and at least one such element must exist.

Second, if S solves our problem for U, then for all other subsets S' of U, sum S = sum S' iff S' also solves our problem for U.

Third, our problem is at least as hard as the Dropbox problem.  If we find a subset which solves our problem with sum exactly zero, then that subset also solves the Dropbox problem.  Otherwise, we say no solution exists.

## Optimal substructure

The relevant optimal substructure is that, every subset of S is the solution to some subset of U.  Or, in a more immediately useful form, for every (not necessarily proper) subset U' of U, either U' is solved by S or else U' is solved by some S' such that S \ S' is a subset of U \ U'. [1]

Proof by contradiction:  suppose U is solved by S but U' has no solution S' such that either S' solves U or S \ S' is a subset of U \ U'.  Then U' must be solved by some S' such that S \ S' is non-empty and has some elements not in U \ U'.  But every element of S must be in U, so those elements must be in (U \ (U \ U')), also known as U'.  Then every element of S is in U'.  

Now apply trichotomy and consider the cases that sum S is less than, equal to, or greater than sum S'.  If sum S < sum S' then U' is not solved by S'.  If sum S > sum S' then U is not solved by S.  If sum S = sum S' then U is solved by S'.  All of these possibilities contradict our original hypothesis. [2]

## Algorithm

I tried to write this in English, and just found myself redefining OCaml.  So, here's some very OCaml-like pseudocode.

Let l be a linked list [3] holding the elements of U in any order.

    let f l = 
    | [] -> []
    | (_::_) as l -> snd (List.hd_exn (fold l ~init:[] ~f:(fun cdr x ->
	let (<) a b = (absolute_value a) < (absolute_value b) in
 	let car = fold cdr ~init:(x, x::[]) ~f:(fun (score', s') y ->
 	    if y < score' then (y, y::[])
 	    else if y + x < score' then (y + x, x::y::[])
 	    else if score' + x < score' then (score' + x, x::s')
 	    else (score', s'))
 	in car::cdr)))

## Variations

Since we generate every possible solution, we can walk back through the list to look for the longest or shortest solution.  

Since there is nothing special that distinguishes the final solution from any of the intermediate solutions, this algorithm can easily be run online, doing linear work per update to give the solution over the known input.

We can also look for subsets with sum closest to a number other than zero, which allows us to support people who want a non-zero calorie balance (negative for dieters, positive for athletes) and people who have already done some eating and working (search for the negative of the sum over some given set).

## Parallelization

We could scale our problem in one of two ways:  by solving many instances at once, or by solving a single very large instance.  Solving many instances at once is so embarassingly parallel that it just becomes an exercise in load-balancing and, as load-balancing goes, not a particularly interesting exercise either.  Solving a large instance, though, is slightly nontrivial.

Using p processors, I think I can solve our problem for n elements in O(n log n) time, where the logarithm is base p [4], by rewriting the inner fold as a map-reduce.

Our outer fold initializes each node of its output list by searching all the previous nodes.  It must initialize the nodes in order, but it can search them out of order.  In fact, it can search every already-initialized node independently.  So we distribute the initialized nodes across the available processors and write some version of this pseudocode:

    define (<) a b as before
    define f shard = fold shard ~init:(x, x::[]) ~f:(fun (score', s') y ->
	if y < score' then (y, y::[])
	else if y + x < score' then (y + x, x::y::[])
 	else if score' + x < score' then (score' + x, x::s')
 	else (score', s'))
    where `shard` refers to the initialized nodes assigned to that processor

    let `reduce` use Lisp's foldl semantics:  if no ~init is supplied, use the last element as the initial value.

    for integer `x` in U:
        replies <- map f over all processors
 	n <- reduce replies ~f:(fun x y -> if fst y < fst x then y else x)
	send the new node n to one of the processors

    The solution is snd n where n was the last node constructed.

Of course, in practice we would want some sort of p-ary tree of reductions.  I've elided this bit because it's probably easier for you to imagine than for me to describe.

Also, I'm cheating a little by assuming we have arbitrarily many processors available.  In practice, we would have each of p processors do a non-constant amount of work, which brings the asymptotic performance right back up to O(n (n/p + log n)).

## Pipelining

Even with the implicit p-ary tree of reductions, our map operation consumes processors like this:

    0       1       2       3       4       5       6       7

    01      23      45      67

    03      47

    07

    0'      1'      2'      3'      4'      5'      6'      7'

    0'1'    2'3'    4'5     6'7'

    0'3'    4'7'

    0'7'    07

    07'

    0"      1"      2"      3"      4"      5"      6"      7"

    0"1"    2"3"    4"5"    6"7"

    0"3"    4"7"

    0"7"    07'

    07"

producing a new node every log n + 1 time intervals.

But we don't need to wait for the 07 node to finish before we can begin the 0'7' node.  We just need the 07 node to finish before we can finish the 0'7' node.  So we can pipeline the nodes like this:

    0       1       2       3       4       5       6       7

    01      23      45      67      0'      1'      2'      3'

    03      47      0'1'    2'3'    4'      5'      6'      7'

    07      0'3'    4'5'    6'7'    0"      1"      2"      3"

    03'     4'7'    0"1"    2"3"    4"      5"      6"      7"

    07'     0"3"    4"5"    6"7"    0`      1`      2`      3`

    03"     4"7"    0`1`    2`3`    4`      5`      6`      7`

    07"     0`3`    4`5`    6`7`    0~      1~      2~      3~

    03`     4`7`    0~1~    2~3~    4~      5~      6~      7~

    07`     0~3~    4~5~    6~7~    ...

After a small start-up lag, we complete a node every two time intervals, regardless of the input size.  So pipelining gets us down to (almost) linear time.

## Footnotes

[1]: As an aside, does anyone else wish that Google Plus supported some kind of math markup?  I've requested the feature...

[2]: A Laci Babai anecdote:  apparently, back in Hungary wherever it was that Prof. Babai learned to write proofs by contradiction, it was customary to end them not by drawing two opposed arrows but by drawing a bolt of lightning, as though Zeus himself had descended to strike down your hypothesis.

[3]: the algorithm can also be implemented as iteration over an array, but I've chosen to present it as recursion over a linked list for two reasons: first, the notions of cdr and car correspond more directly to the notions of S' and S \ S'; and second, because arrays require contiguous memory, and for large n it will be harder to allocate a single array than it will be to allocate the individual nodes of a (possibly unrolled) linked list.

[4] Of course, to say O(log_p n) abuses the notation a bit, since the constant introduced by converting between bases just gets swallowed up by the big-Oh.  But constants do matter.  Also, it's kind of unexciting to say O(n log n) for any p.
