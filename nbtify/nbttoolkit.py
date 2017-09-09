from nbt import TAG_Int, TAG_Long, TAG_Byte, TAG_List, TAG_Float
from nbt import TAG_Short, TAG_String, TAG_Double, TAG_Compound


def addByteTAG(nbtobj, value, name=None):
    byteTag = TAG_Byte(name=name, value=value.encode())
    nbtobj.append(byteTag)


def editByteTAG(nbtobj, value):
    nbtobj.value = int(value)


def addShortTAG(nbtobj, value, name=None):
    shortTag = TAG_Short(name=name, value=int(value))
    nbtobj.append(shortTag)


def editShortTAG(nbtobj, value):
    nbtobj.value = int(value)


def addIntTAG(nbtobj, value, name=None):
    intTag = TAG_Int(name=name, value=int(value))
    nbtobj.append(intTag)


def editIntTAG(nbtobj, value):
    nbtobj.value = int(value)


def addLongTAG(nbtobj, value, name=None):
    longTag = TAG_Long(name=name, value=int(value))
    nbtobj.append(longTag)


def editLongTAG(nbtobj, value):
    nbtobj.value = int(value)


def addFloatTAG(nbtobj, value, name=None):
    floatTag = TAG_Float(name=name, value=float(value))
    nbtobj.append(floatTag)


def editFloatTAG(nbtobj, value):
    nbtobj.value = float(value)


def addDoubleTAG(nbtobj, value, name=None):
    doubleTag = TAG_Double(name=name, value=float(value))
    nbtobj.append(doubleTag)


def editDoubleTAG(nbtobj, value):
    nbtobj.value = float(value)


def addStringTAG(nbtobj, value, name=None):
    stringTag = TAG_String(name=name, value=value)
    nbtobj.append(stringTag)


def editStringTAG(nbtobj, value):
    nbtobj.value = value


def addListTAG(nbtobj, name=None):
    listTag = TAG_List(name=name, value=[])
    nbtobj.append(listTag)


def addCompoundTAG(nbtobj, name=None):
    compTag = TAG_Compound(name=name, value=[])
    nbtobj.append(compTag)


def retrieveTAG(nbtobj, name):
    for tag in nbtobj:
        if tag.name == name:
            return tag
    print('TAG could not be found!')
    return None


addTagFuncs = {
    'ByteTag': addByteTAG,
    'ShortTag': addShortTAG,
    'IntTag': addIntTAG,
    'LongTag': addLongTAG,
    'FloatTag': addFloatTAG,
    'DoubleTag': addDoubleTAG,
    'StringTag': addStringTAG,
    'ListTag': addListTAG,
    'CompundTag': addCompoundTAG
}


editTagFuncs = {
    TAG_Byte: editByteTAG,
    TAG_Short: editShortTAG,
    TAG_Int: editIntTAG,
    TAG_Long: editLongTAG,
    TAG_Float: editFloatTAG,
    TAG_Double: editDoubleTAG,
    TAG_String: editStringTAG
}


simpleTags = [
    'ByteTag',
    'ShortTag',
    'IntTag',
    'LongTag',
    'FloatTag',
    'DoubleTag',
    'StringTag'
]
