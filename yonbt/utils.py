import logging
from .region import Region

log = logging.getLogger(__name__)


def chunkByBlock(x, z):
    return (x >> 4), (z >> 4)


def regionByBlock(x, z):
    return 'r.' + str((x >> 4) // 32) + '.' + str((z >> 4) // 32) + '.mca'


def regionByChunk(x, z):
    return 'r.' + str(x // 32) + '.' + str(z // 32) + '.mca'


def getTileEntity(x, z, obj):
    if isinstance(obj, Region):
        chunk = obj[chunkByBlock(x, z)]
    else:
        chunk = obj
    entities = chunk.nbt['Level']['TileEntities']
    if len(entities) > 0:
        for e in entities:
            if e['x'].value == x and e['z'].value == z:
                return e, entities
        else:
            log.info(f'No TileEntity at {x},{z} in given chunk!')
            return None
    else:
        log.info('No TileEntities in given chunk!')
        return None


def deleteTileEntity(x, z, obj):
    e = getTileEntity(x, z, obj)
    if e is not None:
        e[1].remove(e[0])
        log.info(f'TileEntity at {x},{z} removed!')
