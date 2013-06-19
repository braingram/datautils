Helper functions for using mongo dbs

io
------

read/write: 'sonify' input/output to make it more mongo friendly:
* convert numpy to python types
* fix keys with '.'
* pickle/unpickle structured arrays
* convert output to dotted dictionaries (see ddict)
