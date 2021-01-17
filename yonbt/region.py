import logging
import gzip
import zlib
import time

from io import BytesIO
from struct import pack, unpack
from collections.abc import MutableMapping
from enum import Enum, unique
from functools import cached_property

from typing import NamedTuple, Tuple, Optional

from .nbt import NBTObj, NBTException

log = logging.getLogger(__name__)


SECTOR_LEN = 4096


@unique
class ChunkState(Enum):
    CORRUPTED = -3
    OVERLAPPING = -2
    TOO_BIG = -1
    OK = 0
    NOT_CREATED = 1


@unique
class Compression(Enum):
    GZIP = 1
    ZLIB = 2
    NONE = 3


class Coordinates(NamedTuple):
    x: int
    z: int

    def __repr__(self):
        return f'({self.x}, {self.z})'


class Chunk(NBTObj):

    def __init__(self, x: int, z: int):
        self._coords = Coordinates(x, z)

        self._offset = 0
        self._sectors = 0

        self._timestamp = 0

        self._length = 0
        self._compression = Compression.NONE

        self._data = None

        self._state = ChunkState.NOT_CREATED

        self._padding = 0

    @cached_property
    def entryloc(self) -> int:
        return (self._coords.x + self._coords.z * 32) * 4

    @cached_property
    def neighbour(self) -> Optional[Tuple[int, int]]:
        z = (self._coords.z + 1) % 32
        x = (self._coords.x + 1) if z == 0 else self._coords.x
        if x == 32:
            return None
        else:
            return x, z

    @staticmethod
    def _calc_sectors(length):
        whole, remaining = divmod(length + 5, SECTOR_LEN)
        return whole if remaining == 0 else whole + 1

    @property
    def sectors(self) -> int:
        length = self.length
        if length:
            sectors = self._calc_sectors(length)
            self._sectors = sectors

            if sectors > 255:
                self._state = ChunkState.TOO_BIG
            elif self._state is ChunkState.TOO_BIG:
                self._state = ChunkState.OK

        return self._sectors

    @property
    def timestamp(self) -> int:
        self._timestamp = int(time.time())
        return self._timestamp

    @property
    def length(self) -> int:
        data = self.data
        if data:
            self._length = len(data)
        return self._length

    @property
    def data(self) -> BytesIO:
        if hasattr(self, 'value'):
            if self.value:
                with BytesIO() as raw:
                    self.saveNBT(io=raw)
                    if self._compression is Compression.ZLIB:
                        self._data = zlib.compress(raw.getvalue())
                    elif self._compression is Compression.GZIP:
                        self._data = gzip.compress(raw.getvalue())
                    else:
                        self._data = raw.getvalue()
                self._state = ChunkState.OK
                return self._data

        if self._state is ChunkState.OK:
            self._state = ChunkState.NOT_CREATED
        self._data = None
        return self._data

    @property
    def compression(self) -> Compression:
        return self._compression

    @property
    def state(self) -> ChunkState:
        """Re-evalutes the chunk's state

        This property is a bit of a cheat actually,
        by getting the padding property it starts off
        a chain where all properties relevant to the state
        are called, they all update themselves and evaluate
        the state based on their new value.

        Returns
        -------
        ChunkState
            an enum representing the chunk's state
        """

        _ = self.padding
        return self._state

    @property
    def padding(self) -> int:
        self._padding = (self.sectors * SECTOR_LEN) - self._length - 5
        return self._padding

    def _decode_region_entry(self, io: BytesIO) -> None:
        io.seek(self.entryloc)
        offset, sectors = unpack('>IB', b'\x00' + io.read(4))
        self._offset, self._sectors = offset, sectors

        # determine viability based on region header entry
        # NOT_CREATED simply means the chunk is not yet generated,
        # CORRUPTED state allows no further decoding,
        # TOO_BIG will be checked again later
        if offset == 0 and sectors == 0:
            self._state = ChunkState.NOT_CREATED
        elif sectors == 0:
            self._state = ChunkState.CORRUPTED
        elif offset < 2:
            self._state = ChunkState.CORRUPTED
        elif sectors * SECTOR_LEN + 5 > io.seek(0, 2):
            self._state = ChunkState.CORRUPTED
        elif sectors > 255:
            self._state = ChunkState.TOO_BIG
        else:
            self._state = ChunkState.OK

        io.seek(self.entryloc + SECTOR_LEN)
        self._timestamp = unpack('>I', io.read(4))[0]

    def _decode_header(self, io: BytesIO) -> None:
        io.seek(self._offset * SECTOR_LEN)
        length = unpack('>I', io.read(4))[0]
        self._length = length

        # check for a missmatch between actually required sectors
        # and allocated sectors as given by the region header entry;
        # if more sectors are required than have been allocated
        # then, depending on write order, this chunk might overlap
        # into another, or the other way around
        sectors = self._calc_sectors(length)
        if sectors > self._sectors and self._state:
            self._state = ChunkState.OVERLAPPING

        # check if previously determined TOO_BIG state was wrong
        if self._state is ChunkState.TOO_BIG and sectors <= 255:
            self._sectors = sectors
            self._state = ChunkState.OK

        # a length of 1 or less means there is no data in the chunk
        if length <= 1:
            self._state = ChunkState.CORRUPTED

        comp = unpack('>B', io.read(1))[0]
        try:
            self._compression = Compression(comp)
        except ValueError:
            log.critical(f'Invalid compression type: {comp}')
            self._state = ChunkState.CORRUPTED

    def _decode_nbt(self, io: BytesIO) -> None:
        io.seek(self._offset * SECTOR_LEN + 5)
        try:
            with BytesIO() as tmpio:
                if self.compression is Compression.ZLIB:
                    tmpio.write(zlib.decompress(io.read(self._length - 1)))
                elif self.compression is Compression.GZIP:
                    tmpio.write(gzip.decompress(io.read(self._length - 1)))
                else:  # Compression is NONE
                    tmpio.write(io.read(self._length - 1))
                tmpio.seek(0)
                super().__init__(tmpio)
        except IOError as e:
            log.critical(f'Error decoding chunk {self._coords}')
            log.critical(e)
        except NBTException as e:
            log.critical(f'Decoding data of chunk {self._coords} failed')
            log.critical(e)
            if self._state is ChunkState.OVERLAPPING:
                log.info('This is likely a result of another chunk overlapping '
                         'into this chunk\'s data')

    def decode_chunk(self, io: BytesIO) -> None:
        self._decode_region_entry(io)

        if self._state in (ChunkState.OK, ChunkState.TOO_BIG):
            self._decode_header(io)

            if self._state in (ChunkState.OK, ChunkState.OVERLAPPING):
                self._decode_nbt(io)
            else:
                log.warning(f'Cannot decode any data for chunk {self._coords}')

        elif self._state is ChunkState.NOT_CREATED:
            log.debug(f'Chunk {self._coords} is not generated yet, nothing to decode')
        else:
            log.warning(f'Chunk {self._coords} is corrupted, cannot decode')

    def _encode_region_entry(self, io: BytesIO, offset=None, sectors=None) -> None:
        if offset is None:
            offset = self._offset
        if sectors is None:
            sectors = self._sectors

        io.seek(self.entryloc)
        io.write(pack('>IB', offset, sectors)[1:])

        io.seek(self.entryloc + SECTOR_LEN)
        io.write(pack('>I', self.timestamp))

    def _encode_header(self, io: BytesIO) -> None:
        io.seek(self._offset * SECTOR_LEN)
        io.write(pack('>I', self._length + 1))
        io.write(pack('>B', self.compression.value))

    def _encode_nbt(self, io: BytesIO) -> None:
        io.seek(self._offset * SECTOR_LEN + 5)
        io.write(self._data)

    def encode_chunk(self, io: BytesIO, update_state=True) -> None:
        if update_state:
            state = self.state
        else:
            state = self._state

        if state is ChunkState.OK:
            self._encode_region_entry(io)
            self._encode_header(io)
            self._encode_nbt(io)
            io.write(self._padding * b'\x00')
        elif state is ChunkState.NOT_CREATED:
            log.debug(f'Chunk {self._coords} not yet generated, '
                      'skipping further encoding')
            self._encode_region_entry(io, 0, 0)
        elif state is ChunkState.TOO_BIG:
            log.warning(f'Chunk {self.coords} is too big, '
                        'skipping further encoding')
            self._encode_region_entry(io, 0, 0)
        else:
            log.warning(f'Chunk {self._coords} was corrupted, '
                        'tagging it as "not created" in region header '
                        'and skipping further encoding')
            self._encode_region_entry(io, 0, 0)


class Region(MutableMapping):

    def __init__(self, coords: Tuple[int, int]):
        self._coords = Coordinates(coords[0], coords[1])
        self._chunks = {}

    def decode_region(self, io: BytesIO):
        size = io.seek(0, 2)
        if size == 0:
            log.info(f'Region {self._coords} is empty')
            return
        elif size < SECTOR_LEN * 2:
            log.critical(f'Region {self._coords} does not contain a header')
            return

        for x in range(32):
            for z in range(32):
                c = self._chunks[x, z] = Chunk(x, z)
                c.decode_chunk(io)

    def encode_region(self, io: BytesIO):
        size = io.seek(0, 2)

        header_len = SECTOR_LEN * 2
        if size > header_len:
            io.truncate(header_len)
        io.seek(0)
        io.write(header_len * b'\x00')

        first = True

        for x in range(32):
            for z in range(32):
                chunk = self._chunks[x, z]

                state = chunk.state
                nxt = chunk.neighbour

                if first:
                    if state is ChunkState.OK:
                        chunk._offset = 2
                        first = False

                offset = chunk._offset

                if nxt:
                    neighbour = self._chunks[nxt[0], nxt[1]]
                    if state is ChunkState.OK:
                        neighbour._offset = offset + chunk.sectors
                    else:
                        neighbour._offset = offset

                chunk.encode_chunk(io, update_state=False)

    def __getitem__(self, key):
        return self._chunks[key]

    def __setitem__(self, key, value):
        if key in self._chunks:
            self._chunks[key] = value
        else:
            raise KeyError(f'Chunk {key} not in region file!')

    def __delitem__(self, key):
        if key in self._chunks:
            self._chunks[key] = Chunk(key[0], key[1])
        else:
            raise KeyError(f'Chunk {key} not in region file!')

    def __iter__(self):
        return iter(self._chunks)

    def __len__(self):
        return len(self._chunks)
