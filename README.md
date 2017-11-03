# YoNBT
`yonbt` is yet another NBT parsing library, which allows you to decode and encode files in the Named Binary Tag (NBT) file format,
used by many Minecraft files.

## Features
A few simple high level classes for easy decoding and re-encoding of generic NBT formatted files, such as playerdata files,
and the more complex region files, containing all the chunk data for a Minecraft world.

Low level classes representing the underlying NBT structure, allowing you to create new tag entries in decoded NBT files
or to create whole NBT files from scratch. Be sure to familiarize yourself with the [NBT Format](http://wiki.vg/NBT) beforehand.


## Basic Usage
### Encoding and Decoding
```python
from yonbt import NBTFile, RegionFile

# Load a generic nbt formatted file.
genericNBT = NBTFile("/home/nbt/genericPlayer.dat")

# Save an NBTFile object back to file,
# either providing a new target file:
genericNBT.save("/home/nbt/genericPlayer2.dat")

# or not providing any filename, in which case the original filename is used:
genericNBT.save()
# in this example this would be identical to:
genericNBT.save("/home/nbt/genericPlayer.dat")


# Loading and saving region files (e.g. r.1.0.mca) follows the same pattern.
region = RegionFile("/home/nbt/r.1.1.mca")

region.save("/home/nbt/r.0.2.mca")

region.save()
```

### Editing
```python
# NBTFile and RegionFile are childclasses of the NBTObj and Region classes,
# which are the real meat doing all the decoding and encoding,
# so anything you can do with NBTObj and Region you can do with NBTFile and RegionFile, too.

# An NBTObj acts like a regular python dictionary, 
# exposing all contained nbt entries with their names as the keys.

# You can get a string representation of each tag
print(genericNBT['Invulnerable'])
> B: Invulnerable: 0

# manipulate their values
genericNBT['Invulnerable'] = 1

# create new tag entries from scratch
from yonbt import TAG_String
genericNBT['WOW'] = TAG_String('WOW', 'what have I done?')

# delete them completely
del genericNBT['Score']

# Normally an NBTObj will contain several nested compound tags and list tags,
# which will have their own nested compounds and lists, 
# but they can be accessed like regular dictionaries and regular lists respectively.
genericNBT['Inventory'][2]['id'] = 46

# If you're getting turned around with all this nesting you can also print a
# somewhat nicely formatted string representation of the entire NBTObj
genericNBT.pretty()


# Region objects act like regular python dictionaries as well,
# exposing all contained chunks, using a tuple of their (x, z) coordinates as the keys.

# And because each chunk is itself an NBTObj, you can access and manipulate 
# any contained tag entries as you would with a generic NBTObj.

print(region[(10, 0)]['Level']['LightPopulated'])
> B: LightPopulated: 1

# You can also delete a whole chunk entry
del region[(1, 1)]

# do note however, that the entry will not actually be removed;
# Instead the chunk behind that key will be overwritten with an empty chunk.
# This is to ensure that Minecraft will still recognize the file as valid
# after it is encoded again.
```
