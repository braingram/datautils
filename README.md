Data manipulation tools for python.

This is a collection of various submodules and useful functions
for manipulating some (what I've found to be) common data
structures in python.

Outline
======

*  ddict : dotted-dictionary class and operations
*  grouping : data grouping routines
*  mongo : pymongo-related functions
*  np : numpy-related functions
*  qfilter : list-of-dicts filtering with a mongo query syntax
*  listify : make something a list (if it isn't already)
*  plot : matplotlib-related functions
*  rmap : data remapping


ddict
======
see ddict/README


grouping
======
see grouping/README


mongo
======
see mongo/README


np
======
see np/README


qfilter
======
see qfilter/README



listify
======
Take an item, make it into a list.

```python
from datautils import listify
listify(1) == [1, ]
listify(1, n=2) == [1, 1]
listify([1, ]) == [1, ]
listify('a') == ['a, ]
```


plot
======
Wrap matplotlib (pylab) plotting functions to accept:

* list of dicts (like mongo document lists)
* dicts of [dicts of] lists (i.e. groupings)

the basic structure of each plotting call is:

```python
plot(documents, mapping, **kwargs)
```

for mapping details see rmap


rmap
======
Remapping from list of dicts (or dicts of lists) to dicts of lists.

Types of mappings:

* simple: b = a
* function: b = f(a)
* query: b = qf(a, q) [see qfilter, or mongo queries]
