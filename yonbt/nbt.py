from struct import pack, unpack
from collections.abc import MutableMapping, MutableSequence


class NBTException(Exception):
    pass


class TAG:
    def encode(self, io, fmt, *args):
        io.write(pack(">" + fmt, *args))

    def decode(self, io, fmt, size):
        return unpack(">" + fmt, io.read(size))

    def encode_name(self, io):
        io.write(pack(">H", len(self.name)))
        io.write(self.name.encode('utf-8'))

    def decode_name(self, io):
        return io.read(unpack(">H", io.read(2))[0]).decode('utf-8')

    def __repr__(self):
        return f'{tagNames[self.__class__.__name__]}: ' + \
            (f'{self.name}: ' if self.name else '') + f'{self.value}'


class SequenceTAG(MutableSequence):
    def __init__(self, value):
        self.value = value

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

    def __repr__(self):
        length = len(self.value)
        return f'{tagNames[self.__class__.__name__]}: ' + \
               (f'{self.name}: ' if self.name else '') + \
               (f'{length} Entry' if length == 1 else f'{length} Entries')


class TAG_End():
    pass


class TAG_Byte(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = self.decode(io, 'b', 1)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 1)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'b', self.value)


class TAG_Short(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = self.decode(io, 'h', 2)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 2)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'h', self.value)


class TAG_Int(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = self.decode(io, 'i', 4)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 3)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'i', self.value)


class TAG_Long(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = self.decode(io, 'q', 8)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 4)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'q', self.value)


class TAG_Float(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = self.decode(io, 'f', 4)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 5)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'f', self.value)


class TAG_Double(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = self.decode(io, 'd', 8)[0]

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 6)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'd', self.value)


class TAG_Byte_Array(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = bytearray(io.read(self.decode(io, 'i', 4)[0]))

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 7)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'i', len(self.value))
        io.write(self.value)

    def __repr__(self):
        length = len(self.value)
        return f'{tagNames[self.__class__.__name__]}: ' + \
               (f'{self.name}: ' if self.name else '') + \
               (f'{length} Entry' if length == 1 else f'{length} Entries')

    def __str__(self):
        return repr(self) + '[\n\t' + self.value.hex(' ') + '\n]'


class TAG_String(TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
            self.value = self.decode_name(io)

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 8)
        if self.name is not None:
            self.encode_name(io)
        io.write(pack(">H", len(self.value.encode('utf-8'))))
        io.write(self.value.encode('utf-8'))


class TAG_List(SequenceTAG, TAG):
    def __init__(self, name=None, value=None, tags_type=None, io=None):
        self.name = name
        if io is None:
            super().__init__(value)
            self.tags_type = tags_type
        else:
            super().__init__([])
            self.tags_type = self.decode(io, 'b', 1)[0]
            self.list_size = self.decode(io, 'i', 4)[0]
            for _ in range(self.list_size):
                self.value.append(tag[self.tags_type](io=io))

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 9)
        if self.name is not None:
            self.encode_name(io)
        if len(self.value) > 0:
            self.encode(io, 'b', self.tags_type)
            self.encode(io, 'i', self.list_size)
            for i in self.value:
                i.saveNBT(io, typed=False)
        else:
            self.encode(io, 'b', 0)
            self.encode(io, 'i', 0)

    def __str__(self):
        return repr(self) + '{\n\t' + '\n\t'.join([f'[{idx}] {repr(tag)}' for idx, tag in enumerate(self.value)]) + '\n}'

    def pretty(self, indent=0):
        rep = []
        for v in self.value:
            if isinstance(v, TAG_Compound):
                rep.append('\t' * indent + '{')
                rep.extend(v.pretty(indent=indent + 1))
                rep.append('\t' * indent + '}')
            elif isinstance(v, TAG_List):
                rep.append('\t' * indent + '[')
                rep.extend(v.pretty(indent=indent + 1))
                rep.append('\t' * indent + ']')
            else:
                rep.append('\t' * indent + str(v))
        return rep

    def pprint(self, indent=0):
        for s in self.pretty():
            print(s)


class TAG_Compound(MutableMapping, TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            self.value = value
        else:
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
        for i in self.value.values():
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

    def __repr__(self):
        length = len(self.value)
        try:
            tagname = tagNames[self.__class__.__name__]
        except KeyError:
            tagname = 'OuterCompound'
        finally:
            return f'{tagname}: ' + \
                (f'{self.name}: ' if self.name else '') + \
                (f'{length} Entry' if length == 1 else f'{length} Entries')

    def __str__(self):
        return repr(self) + '{\n\t' + '\n\t'.join([repr(tag) for tag in self.value.values()]) + '\n}'

    def pretty(self, indent=0):
        rep = []
        for k, v in self.value.items():
            if isinstance(v, TAG_Compound):
                rep.append('\t' * indent + str(k) + ': {')
                rep.extend(v.pretty(indent=indent + 1))
                rep.append('\t' * indent + '}')
            elif isinstance(v, TAG_List):
                rep.append('\t' * indent + str(k) + ': [')
                rep.extend(v.pretty(indent=indent + 1))
                rep.append('\t' * indent + ']')
            else:
                rep.append('\t' * indent + str(v))
        return rep

    def pprint(self, indent=0):
        for s in self.pretty():
            print(s)


class TAG_Int_Array(SequenceTAG, TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            super().__init__(value)
        else:
            super().__init__([])
            for _ in range(self.decode(io, 'i', 4)[0]):
                self.value.append(self.decode(io, 'i', 4)[0])

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 11)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'i', len(self.value))
        for i in self.value:
            self.encode(io, 'i', i)

    def __str__(self):
        return repr(self) + '[\n\t' + ' '.join(self.value) + '\n]'


class TAG_Long_Array(SequenceTAG, TAG):
    def __init__(self, name=None, value=None, io=None):
        self.name = name
        if io is None:
            super().__init__(value)
        else:
            super().__init__([])
            for _ in range(self.decode(io, 'i', 4)[0]):
                self.value.append(self.decode(io, 'q', 8)[0])

    def saveNBT(self, io, typed=True):
        if typed:
            self.encode(io, 'b', 12)
        if self.name is not None:
            self.encode_name(io)
        self.encode(io, 'i', len(self.value))
        for i in self.value:
            self.encode(io, 'q', i)

    def __str__(self):
        return repr(self) + '[\n\t' + ' '.join(self.value) + '\n]'


class NBTObj(TAG_Compound):
    def __init__(self, io=None):
        if io is not None:
            if self.decode(io, 'b', 1)[0] != 10:
                raise NBTException("Invalid NBT Data!")
            baseName = self.decode_name(io)
            super().__init__(name=baseName, io=io)

    def pprint(self, indent=1):
        print('\t' * indent + 'BaseCompound: {\n' + '\t' * indent + '\n'.join(super().pretty(indent=indent)) + '\t' * indent + '\n}')


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
    11: TAG_Int_Array,
    12: TAG_Long_Array
}


tagNames = {
    'TAG_Byte': 'B',
    'TAG_Short': 'S',
    'TAG_Int': 'I',
    'TAG_Long': 'L',
    'TAG_Float': 'F',
    'TAG_Double': 'D',
    'TAG_String': 'Str',
    'TAG_Compound': 'Co',
    'TAG_List': 'Li',
    'TAG_Byte_Array': 'BA',
    'TAG_Int_Array': 'IA',
    'TAG_Long_Array': 'LA'
}
