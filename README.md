# YoNBT
`yonbt` is yet another NBT parsing library, which allows you to decode and encode files in the Named Binary Tag (NBT) file format,
used by many Minecraft files.

## Features
A few simple high level classes for easy decoding and re-encoding of generic NBT formatted files, such as playerdata files,
and the more complex region files, containing all the chunk data for a Minecraft world.

Low level classes representing the underlying NBT format.

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

#

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
- contains metadata and inherits `NBTObj` (which inherits `TAG_Compound`... you get the idea)

The two most important tags are, as you might have noticed,
the `TAG_Compound` and also the `TAG_List`;
Both of these are important because they're the only tags that can contain other tags.

`TAG_Compound` is a MutableMapping (a dictionary), holding tags with their names
as their keys.

`TAG_List` is a MutableSequence (a list), holding unnamed tags with only index keys.

`Region` holds all the chunks in a region with tuples of their x, z coordinates as the keys (these are chunk coordinates, NOT block coordinates), both `in-region` and `in-world` coordinates may be used to access a chunk (`in-world` is probably what you'd get from a crashreport or in-game reporting tool);

`Chunk` inherits `NBTObj`, so it works just like a `TAG_Compound`.

Okay with that out of the way, let's move on!

#

### Editing
Loading up an nbt file and a region file as described
in the Encoding and Decoding section above, you can start looking at their contents and editing them.

```python
from yonbt import NBTFile, RegionFile

nbt = NBTFile('/home/nbt/playerdata.dat')
region = RegionFile('/home/nbt/r.1.-2.mca')

# You can print your nbt:
print(nbt)
# and region objects:
print(region)
# giving you a very basic representation of the content within.

# Pretty-print a "tree" view of List and Compound tags
# (works on NBTFile since it inherits from Compound):
nbt.pprint()
# giving you a nicer representation with indentation and everything.

# Pretty-print a region:
region.pprint()
# to get a full listing of all chunks in it, with their coordinates.


# Navigation within an nbt file is just like traversing nested dictionaries.

# So to grab a tag in the top level of our `nbt` object:
someTag = nbt['someTag']
# and to grab a tag two levels deeper:
deepList = nbt['topLevelEntry']['oneDown']['deepList']
# etc.

# Remember to print (or pprint) often to find your way around:
print(someTag)
# as mentioned above, pretty printing is only available for TAG_List and TAG_Compound:
deepList.pprint()

# Edit the value of the second tag in `deepList`:
deepList[1].value = "over 9000!"
# make sure the type of the new value matches the tag, or you'll get an error on saving!

# And of course, deleting a tag:
del nbt['someTag']


# Region files are much the same, except that here (unlike in generic NBT files) the top level is not a TAG_Compound, but a mapping of all the chunks in the region;
# Once you've select a chunk to work on, by accessing it via it's coordinates:
chunk = region[22, 30]
# you can start working with it like any other nbt file as described above.

# If you just want to completely delete a chunk:
del region[22, 30]
# This will not fully remove the chunk, since the registry header of a region file must always contain information such as where in the file a chunk can be found, so instead 'del' replaces the chunk with an empty one, with no data, and a registry entry that identifies it as "not yet created".
```

Of course you can do much more than just navigating around and editing some attributes, such as copy pasting a tag from one file to another, adding new tags, or writing a whole chunk from scratch, but for that I would suggest familiarizing yourself with the [NBT Format](https://minecraft.gamepedia.com/NBT_format) beforehand.

#

### Utility Functions

To make navigating around inside regions, or just finding out which region file you need to open, some utility functions are also provided:

```python
from yonbt import chunkByBlock, locateBlock, locateChunk

# Finding chunk coordinates, given block coordinates:
chunkByBlock(x, z)
# returns a tuple of two integers, being the coordinates of the chunk that the given block is in.
# You could use it like this, to get the chunk of block x,z from a region:
region[chunkByBlock(10, -24)]


# Getting both region filename and chunk coords, given block coords:
locateBlock(x, z)
# returns a tuple consisting of the region filename as a string, and another tuple being the chunk coordinates.
# Could be used like this:
rfile, chunkcoords = locateBlock(x, z)
region = RegionFile(f'/home/nbt/regions/{rfile}')
chunk = region[chunkcoords]


# Getting region filename, given chunk coords:
locateChunk(x, z)
# here x and z are the in-world coordinates of a chunk,
# returns the filename of the region, containing given chunk, as a string.
# Might be used like this:
region = RegionFile(f'/home/nbt/regions/{locateChunk(x, z)}')
```
