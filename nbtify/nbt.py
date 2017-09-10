from struct import unpack, pack
import gzip


def decode_name(decode, named=True):
    if not named:
        name = None
    else:
        name = decode.io.read(decode("H", 2)[0]).decode('utf-8')
    return name


def encode_name(self, encode):
    if self.name is not None:
        encode("H", len(self.name))
        encode.io.write(self.name.encode('utf-8'))


class TAG_End:
    pass


class TAG_Byte:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            self.value = decode("b", 1)[0]

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 1)
        encode_name(self, encode)
        encode("b", self.value)

    def editValue(self, value):
        self.value = int(value)


class TAG_Short:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            self.value = decode("h", 2)[0]

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 2)
        encode_name(self, encode)
        encode("h", self.value)

    def editValue(self, value):
        self.value = int(value)


class TAG_Int:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            self.value = decode("i", 4)[0]

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 3)
        encode_name(self, encode)
        encode("i", self.value)

    def editValue(self, value):
        self.value = int(value)


class TAG_Long:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            self.value = decode("q", 8)[0]

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 4)
        encode_name(self, encode)
        encode("q", self.value)

    def editValue(self, value):
        self.value = int(value)


class TAG_Float:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            self.value = decode("f", 4)[0]

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 5)
        encode_name(self, encode)
        encode("f", self.value)

    def editValue(self, value):
        self.value = float(value)


class TAG_Double:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            self.value = decode("d", 8)[0]

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 6)
        encode_name(self, encode)
        encode("d", self.value)

    def editValue(self, value):
        self.value = float(value)


class TAG_String:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            length = decode("H", 2)[0]
            self.value = decode.io.read(length).decode('utf-8')

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 8)
        encode_name(self, encode)
        encode("H", len(self.value.encode('utf-8')))
        encode.io.write(self.value.encode('utf-8'))

    def editValue(self, value):
        self.value = value


class TAG_List:
    def __init__(self, value=None, name=None, decode=None, named=True, tags_type=None, list_size=None):
        if decode is None:
            self.name = name
            self.value = value
            self.tags_type = tags_type
            self.list_size = list_size
        else:
            self.name = decode_name(decode, named)
            self.tags_type = decode("b", 1)[0]
            self.list_size = decode("i", 4)[0]
            taglist = []
            for i in range(self.list_size):
                taglist.append(tag[self.tags_type](decode=decode, named=False))
            self.value = taglist

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 9)
        encode_name(self, encode)
        encode("b", self.tags_type)
        encode("i", self.list_size)
        for i in self.value:
            i.nbtify(encode, hastag=False)

    def addTAG(self, value):
        self.value.append(tag[self.tags_type](value=value))


class TAG_Compound:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            compound = []
            while True:
                _type = decode("b", 1)[0]
                if _type == 0:
                    break
                compound.append(tag[_type](decode=decode))
            self.value = compound

    def nbtify(self, encode=None, hastag=True, io=None):
        if io is not None:
            encode = lambda fmt, *args: io.write(pack(">" + fmt, *args))
            encode.io = io
        if hastag:
            encode("b", 10)
        encode_name(self, encode)
        for i in self.value:
            i.nbtify(encode)
        encode("b", 0)

    def addTAG(self, tagtype, name):
        self.value.append(tag[tagtype](name=name))


class TAG_Int_Array:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            arlen = decode("i", 4)
            arlen = arlen[0]
            if arlen == 0:
                self.value = []
            else:
                self.value = []
                while arlen > 0:
                    self.value.append(decode("i", 4)[0])
                    arlen -= 1

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 11)
        encode_name(self, encode)
        encode("i", len(self.value))
        if len(self.value) != 0:
            for n in self.value:
                encode("i", n)


class TAG_Byte_Array:
    def __init__(self, value=None, name=None, decode=None, named=True):
        if decode is None:
            self.name = name
            self.value = value
        else:
            self.name = decode_name(decode, named)
            self.value = bytearray(decode.io.read(decode("i", 4)[0]))

    def nbtify(self, encode, hastag=True):
        if hastag:
            encode("b", 7)
        encode_name(self, encode)
        encode("i", len(self.value))
        for i in self.value:
            encode("b", i)


class NBTObj(TAG_Compound):
    def __init__(self, nbtfile):
        self.nbtfile = nbtfile
        try:
            with gzip.open(nbtfile, 'rb') as io:
                decode = lambda fmt, size: unpack(">" + fmt, io.read(size))
                decode.io = io
                if decode("b", 1)[0] != 10:
                    raise NBTException("Invalid NBT data! Maybe it's gzipped?")
                super().__init__(decode=decode)
                io.close()
            self.gzipped = True
        except OSError:
            with open(nbtfile, 'rb') as io:
                decode = lambda fmt, size: unpack(">" + fmt, io.read(size))
                decode.io = io
                if decode("b", 1)[0] != 10:
                    raise NBTException("Invalid NBT data! Maybe it's gzipped?")
                super().__init__(decode=decode)
                io.close()
            self.gzipped = False

    def reload(self):
        try:
            with gzip.open(self.nbtfile, 'rb') as io:
                super().__init__(io=io)
                io.close()
            self.gzipped = True
        except OSError:
            with open(self.nbtfile, 'rb') as io:
                super().__init__(io=io)
                io.close()
            self.gzipped = False

    def save(self, destfile=None):
        if destfile is None:
            nbtfile = self.nbtfile
        else:
            nbtfile = destfile
        if self.gzipped:
            with gzip.open(nbtfile, 'wb') as io:
                self.nbtify(io=io)
                io.close()
        else:
            with open(nbtfile, 'wb') as io:
                self.nbtify(io=io)
                io.close()
        return True


tag = {
    0: TAG_End,
    1: TAG_Byte,
    2: TAG_Short,
    3: TAG_Int,
    4: TAG_Long,
    5: TAG_Float,
    6: TAG_Double,
    7: TAG_Byte_Array,
    8: TAG_String,
    9: TAG_List,
    10: TAG_Compound,
    11: TAG_Int_Array
}


tagString = {
    TAG_End: 'End',
    TAG_Byte: 'Byte',
    TAG_Short: 'Short',
    TAG_Int: 'Int',
    TAG_Long: 'Long',
    TAG_Float: 'Float',
    TAG_Double: 'Double',
    TAG_Byte_Array: 'Byte_Array',
    TAG_String: 'String',
    TAG_List: 'List',
    TAG_Compound: 'Compound',
    TAG_Int_Array: 'Int_Array'
}


class NBTException(Exception):
    pass
