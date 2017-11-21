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

### Structure
In the following section we'll look at how to use the NBTFile and RegionFile objects, but for that you'll need to understand how those are structured underneath.

This is a crude presentation:

`NBTFile` : (represents an nbt file)
- inherits `NBTObj` : (base tag for the content in an nbt file)
  - inherits `TAG_Compound` : (representing a compound tag)
    - contains other tags, including other compound tags, heavily nested

`RegionFile` : (represents a region file)
- inherits `Region` : (representation of the content in a region file)
  - contains metadata and `Chunk`(s)

`Chunk` : (represents a chunk)
- contains metadata and an `NBTObj` (which inherits `TAG_Compound`... you get the idea)

The two most important tags are for one, as you might have noticed,
the `TAG_Compound` and also the `TAG_List`;
Both these are important because they're the only tags that can contain other tags.

`TAG_Compound` is a MutableMapping (a dictionary), holding tags with their names
as their keys.

`TAG_List` is a MutableSequence (a list), holding unnamed tags with only index keys.

`Region` and `Chunk`, while not tags, are also MutableMappings (dictionaries).

`Region` holds all the chunks in a region by the tuple of their x, z coordinates as the keys (these are chunk coordinates, NOT block coordinates, there's a difference).

`Chunk` exposes the `NBTObj` within, so it works just like a `TAG_Compound`.

Okay with that out of the way, let's move on!

### Editing
Assuming you've already loaded up an nbt file and a region file as described
in the Encoding and Decoding section above, you'll have yourself an
`nbt` and a `region` variable.

```python
# You can print your nbt object:
print(nbt)
# giving you a very basic representation of the content within.

# Pretty-print a "tree" view:
nbt.pretty()
# giving you a nicer representation with indentation and everything.

# Fetch a tag within `nbt` by its name:
someTag = nbt['someTag']

# Print or pretty-print `someTag`:
print(someTag)

# Edit `someTag`s value (make sure the value matches the type of tag):
someTag.value = "over 9000!"

# Delete `someTag` from `nbt`:
del nbt['someTag']
# or, if you already hold the `someTag` object:
nbt.remove(someTag)
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
