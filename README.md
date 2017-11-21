# YoNBT
`yonbt` is yet another NBT parsing library, which allows you to decode and encode files in the Named Binary Tag (NBT) file format,
used by many Minecraft files.

## Features
A few simple high level classes for easy decoding and re-encoding of generic NBT formatted files, such as playerdata files,
and the more complex region files, containing all the chunk data for a Minecraft world.

Low level classes representing the underlying NBT structure, allowing you to create new tag entries in decoded NBT files
or to create whole NBT files from scratch. Be sure to familiarize yourself with the [NBT Format](http://wiki.vg/NBT) beforehand.

A few utility functions to make working with this library easier, especially if you're just using it from a Python REPL for quick edits.

## Basic Usage
### Encoding and Decoding
```python
from yonbt import NBTFile, RegionFile

# Load a generic nbt formatted file.
nbt = NBTFile("/home/nbt/genericPlayer.dat")

# Save an NBTFile object back to file,
# either providing a new target file:
nbt.save("/home/nbt/genericPlayer2.dat")

# or not providing any filename, in which case the original filename is used:
nbt.save()
# in this example this would be identical to:
nbt.save("/home/nbt/genericPlayer.dat")


# Loading and saving region files (e.g. r.1.0.mca) follows the same pattern.
region = RegionFile("/home/nbt/r.1.1.mca")

region.save("/home/nbt/r.0.2.mca")

region.save()
```

### Editing
Underneath NBTFile and RegionFile are the NBTObj and Region classes,
which provide the actual editing functionalities

```python
# You can get a really simple string representation of each tag
print(nbtCompound['Invulnerable'])
> B: Invulnerable: 0
# for Compounds or List it only prints the amount of entries.

# manipulate their values
nbtCompound['Invulnerable'] = 1

# create new tag entries from scratch
from yonbt import TAG_String
nbtCompound['WOW'] = TAG_String('WOW', 'what have I done?')

# delete a tag completely
nbtCompound.remove(nbtCompound['WOW'])
# or, if you already hold the tag object itself
nbtCompound.remove(someTag)

# Normally an NBTObj will contain several nested compound tags and list tags,
# which will have their own nested compounds and lists,
# but they can be accessed like regular dictionaries and regular lists respectively.
nbtCompound['Inventory'][2]['id'] = 46

# If you're getting turned around with all this nesting you can also print a
# somewhat nicely formatted string representation of any compound or list tag.
nbtCompound.pretty()


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

# And pretty print the chunk.
chunk = region[12, 5]
chunk.pretty()

```

### Utility Functions
```python
chunkByBlock(x, z)
# returns a tuple of two integers, which is the same coordinate of the chunk
# that the given block is in.
# You could use it like this, to get the chunk of block x,z from a region:
region[chunkByBlock(10, -24)]
# If the block is not in that region then a KeyError will be raised.

regionByBlock(x, z)
# returns a string with the name of the region that the block is in.
# like so: 'r.1.-5.mca', you could use this directly like this:
region = RegionFile(regionByBlock(x, z))

regionByChunk(x, z)
# same deal, just that here x, z are the coordinates of the chunk, not any block.

getTileEntity(x, z, region)
# or
getTileEntity(x, z, chunk)
# this returns a tuple consisting of the tag for the tile entity, with the given
# coordinates, and the list that it is contained in: (entity, listContainingEntity)
# You also pass in either a Region or Chunk object, that you have
# instantiated beforehand. Just passing in the string returned by regionByBlock
# won't work.

deleteTileEntity(x, z, region)
# or
deleteTileEntity(x, z, chunk)
# same deal as getTileEntity, but this deletes the tag for the tile entity.
# Good for quick edits, for example when a tile entity is causing crashes.
# Note that this function does not handle saving the change, you gotta save
# the region file back yourself, as described above.
```
