import logging
import gzip
import zlib
import time
from io import BytesIO
from struct import pack, unpack
from collections.abc import MutableMapping
from nbt import NBTObj

log = logging.getLogger('nbt')


class RegionException(Exception):
    pass


class ChunkException(Exception):
    pass


class Chunk:
    def __init__(self, x, z, **contents):
        self.x = x
        self.z = z
        self.offset = contents.pop('offset', 0)
        self.sectors = contents.pop('sectors', 0)
        self.timestamp = contents.pop('timestamp', 0)
        self.length = contents.pop('length', 0)
        self.compression = contents.pop('compression', 2)
        self.nbt = contents.pop('nbt', None)
        self.compressed = contents.pop('compressed', None)
        self.padding = contents.pop('padding', 0)


class Region(MutableMapping):
    def __init__(self, name=None, io=None, **contents):
        self.name = name
        if io is None:
            self.chunks = contents.pop('chunks', {})
        else:
            self.chunks = {}
            self.decodeRegion(io)

    def decodeRegion(self, io):
        for x in range(32):
            for z in range(32):
                self.chunks[x, z] = Chunk(x, z)
        for n in range(0, 4096, 4):
            chunk = self.chunks[(int(n // 4) % 32), (int(n // 4) // 32)]
            chunk.offset = unpack('>I', b'\x00' + io.read(3))[0]
            chunk.sectors = unpack('>B', io.read(1))[0]
        for n in range(0, 4096, 4):
            chunk = self.chunks[(int(n // 4) % 32), (int(n // 4) // 32)]
            chunk.timestamp = unpack('>I', io.read(4))[0]
        for chunk in self.chunks.values():
            if chunk.offset == 0 and chunk.sectors == 0:
                continue
            try:
                io.seek(chunk.offset * 4096)
                chunk.length = unpack('>I', io.read(4))[0]
                chunk.compression = unpack('>B', io.read(1))[0]
                if chunk.compression == 2:
                    rawChunk = BytesIO(zlib.decompress(io.read(chunk.length - 1)))
                elif chunk.compression == 1:
                    rawChunk = BytesIO(gzip.decompress(io.read(chunk.length - 1)))
                else:
                    raise ChunkException('Invalid chunk compression!')
                chunk.nbt = NBTObj(io=rawChunk)
            except IOError as e:
                log.critical('Error decoding Region!')
                log.critical(e)
            finally:
                rawChunk.close()

    def encodeRegion(self, io):
        self.encodeChunks()
        self.calculateOffsets()
        for n in range(0, 4096, 4):
            chunk = self.chunks[(int(n // 4) % 32), (int(n // 4) // 32)]
            io.write(pack('>I', chunk.offset)[1:])
            io.write(pack('>B', chunk.sectors))
        for n in range(0, 4096, 4):
            chunk = self.chunks[(int(n // 4) % 32), (int(n // 4) // 32)]
            io.write(pack('>I', chunk.timestamp))
        for chunk in sorted(self.chunks.values(), key=lambda x: x.offset):
            if chunk.compressed is None:
                continue
            io.write(pack('>I', chunk.length))
            io.write(pack('>B', chunk.compression))
            io.write(chunk.compressed)
            io.write(chunk.padding * b'\x00')

    def encodeChunks(self):
        for chunk in self.chunks.values():
            if chunk.offset == 0 and chunk.sectors == 0:
                continue
            try:
                rawChunk = BytesIO()
                chunk.nbt.saveNBT(io=rawChunk)
                if chunk.compression == 2:
                    compChunk = zlib.compress(rawChunk.getvalue())
                elif chunk.compression == 1:
                    compChunk = gzip.compress(rawChunk.getvalue())
                else:
                    raise ChunkException('Invalid chunk compression!')
            except IOError as e:
                log.critical(e)
            chunk.compressed = compChunk
            chunk.timestamp = int(time.time())
            chunk.length = len(compChunk) + 1
            sectors, r = divmod((chunk.length + 4), 4096)
            if r == 0:
                chunk.sectors = sectors
            else:
                chunk.sectors = sectors + 1
            chunk.padding = 4096 * chunk.sectors - chunk.length - 4

    def calculateOffsets(self):
        sortedChunks = sorted(self.chunks.values(), key=lambda x: x.offset)
        for i in range(len(sortedChunks)):
            if sortedChunks[i].offset <= 2:
                continue
            prevChunk = sortedChunks[i - 1]
            sortedChunks[i].offset = prevChunk.offset + prevChunk.sectors

    def __getitem__(self, key):
        return self.chunks[key]

    def __setitem__(self, key, value):
        self.chunks[key] = value

    def __delitem__(self, key):
        self.chunks[key] = Chunk(key[0], key[1])

    def __iter__(self):
        return iter(self.chunks)

    def __len__(self):
        return len(self.chunks)
