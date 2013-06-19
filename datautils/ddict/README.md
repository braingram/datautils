A dictionary subclass that treats keys containing '.' as nested gets.

See ddict.ops for:

* recursive gets (using some delimiter, such as '.')
* recursive sets
* recursive deletes
* try-gets (something like d.get('a', 'default'))

Example
------

```python
from datautils import ddict
d = ddict.DDict({'a': {'b': 1}})
assert d['a.b'] == 1
```
