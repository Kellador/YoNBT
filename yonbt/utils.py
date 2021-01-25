import logging

from typing import Tuple

log = logging.getLogger(__name__)


def chunkByBlock(x: int, z: int) -> Tuple[int, int]:
    return (x >> 4), (z >> 4)


def locateBlock(x: int, z: int) -> Tuple[str, Tuple[int, int]]:
    region = 'r.' + str((x >> 4) // 32) + '.' + str((z >> 4) // 32) + '.mca'
    chunk = (x >> 4), (z >> 4)
    return region, chunk


def locateChunk(x: int, z: int) -> str:
    return 'r.' + str(x // 32) + '.' + str(z // 32) + '.mca'
