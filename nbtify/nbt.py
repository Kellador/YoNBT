from struct import pack, unpack
import gzip
from collections.abc import MutableMapping, MutableSequence


class NBTException(Exception):
    pass


class TAGMixin:
    def encode(self, io, fmt, *args):
        io.write(pack(">" + fmt, *args))

    def decode(self, io, fmt, size):
        return unpack(">" + fmt, io.read(size))

    def encode_name(self, io):
        io.write(pack(">H", len(self.name)))
        io.write(self.name.encode('utf-8'))

    def decode_name(self, io):
        return io.read(unpack(">H", 2)[0]).decode('utf-8')

    def __str__(self):
        return f'{self.__class__.name__} {self.name}: {self.value}'


class TAG_End():
    pass


class TAG_Byte(TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = self.decode(io, 'b', 1)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 1)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'b', self.value)


class TAG_Short(TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = self.decode(io, 'h', 2)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 2)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'h', self.value)


class TAG_Int(TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = self.decode(io, 'i', 4)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 3)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'i', self.value)


class TAG_Long(TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = self.decode(io, 'q', 8)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 4)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'q', self.value)


class TAG_Float(TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = self.decode(io, 'f', 4)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 5)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'f', self.value)


class TAG_Double(TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = self.decode(io, 'd', 8)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 6)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'd', self.value)


class TAG_Byte_Array(MutableSequence, TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = bytearray(io.read(self.decode(io, 'i', 4)[0]))

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 7)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'i', len(self.value))
        for i in self.value:
            self.encode(io, 'b', i)

    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        self.value[index] = value

    def __delitem__(self, index):
        del self.value[index]

    def __len__(self):
        return len(self.value)

    def insert(self, index, value):
        self.value.insert(index, value)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.name}: ' + \
            '[' + ' '.join([str(x) for x in self.value]) + ']'


class TAG_String(TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = self.decode_name(io)

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 8)
        if self.name is not None:
            self.encode_name(io)
        io.write(pack(">H", len(self.value.encode('utf-8'))))
        io.write(self.value.encode('utf-8'))


class TAG_List(MutableSequence, TAGMixin):
    def __init__(self, name=None, value=None, tags_type=None, io=None):
        if io is None:
            self.name = name
            self.value = value
            self.tags_type = tags_type
        else:
            if name is not None:
                self.name = name
            self.value = []
            self.tags_type = self.decode(io, 'b', 1)[0]
            for _ in range(self.decode(io, 'i', 4)[0]):
                self.value.append(tag[self.tags_type](io=io))

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 9)
        if self.name is not None:
            self.encode_name(io)
        if len(self.value) > 0:
            self.encode(io, 'b', self.tags_type)
            self.encode(io, 'i', len(self.value))
            for i in self.value:
                i.saveNBT(io, typed=False)
        else:
            self.encode(io, 'b', 0)
            self.encode(io, 'i', 0)

    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        self.value[index] = value

    def __delitem__(self, index):
        del self.value[index]

    def __len__(self):
        return len(self.value)

    def insert(self, index, value):
        self.value.insert(index, value)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.name}: ' + \
            '[\n\t' + '\n\t'.join([str(x) for x in self.value]) + ']'


class TAG_Compound(MutableMapping, TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = {}
            while True:
                typeID = self.decode(io, 'b', 1)[0]
                if typeID == 0:
                    break
                tagName = self.decode_name(io)
                self.value[tagName] = tag[typeID](name=tagName, io=io)

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 10)
        if self.name is not None:
            self.encode_name(io)
        for i in self.value:
            i.saveNBT(io)
        self.encode(io, 'b', 0)

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __delitem__(self, key):
        del self.value[key]

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.name}: ' + \
            '{' + '\n\t'.join([str(x) for x in self.value]) + '}'


class TAG_Int_Array(MutableSequence, TAGMixin):
    def __init__(self, name=None, value=None, io=None):
        if io is None:
            self.name = name
            self.value = value
        else:
            if name is not None:
                self.name = name
            self.value = []
            for _ in range(self.decode(io, 'i', 4)[0]):
                self.value.append(self.decode(io, 'i', 4)[0])

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 11)
        if self.name is not None:
            self.encode_name(io)
        for i in self.value:
            self.encode(io, 'i', i)

    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        self.value[index] = value

    def __delitem__(self, index):
        del self.value[index]

    def __len__(self):
        return len(self.value)

    def insert(self, index, value):
        self.value.insert(index, value)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.name}: ' + \
            '[' + ' '.join([str(x) for x in self.value]) + ']'


class NBTObj(TAG_Compound):
    def __init__(self, nbtfile=None):
        if nbtfile is not None:
            self.nbtfile = nbtfile
            try:
                with gzip.open(self.nbtfile, 'rb') as io:
                    if self.decode(io, 'b', 1)[0] != 10:
                        raise NBTException("Invalid NBT File!")
                    super().__init__(io=io)
                self.gzipped = True
            except OSError:
                with open(self.nbtfile, 'rb') as io:
                    if self.decode(io, 'b', 1)[0] != 10:
                        raise NBTException("Invalid NBT File!")
                    super().__init__(io=io)
                self.gzipped = False

    def reload(self):
        if self.gzipped:
            with gzip.open(self.nbtfile, 'rb') as io:
                super().__init__(io=io)
        else:
            with open(self.nbtfile, 'rb') as io:
                super().__init__(io=io)

    def save(self, destfile=None):
        if destfile is None:
            destfile = self.nbtfile
        if self.gzipped:
            with gzip.open(destfile, 'wb') as io:
                super().saveNBT(io)
        else:
            with open(destfile, 'wb') as io:
                super().saveNBT(io)


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
