import gzip
import logging
import re
from pathlib import Path
from .nbt import NBTObj
from .region import Region

log = logging.getLogger(__name__)


class NBTFile(NBTObj):
    def __init__(self, filename):
        self.filename = filename
        try:
            with gzip.open(self.filename, 'rb') as io:
                super().__init__(io=io)
            self.compression = 'GZIP'
            log.info(f'{self.filename} was GZIP compressed.')
        except IOError:
            with open(self.filename, 'rb') as io:
                super().__init__(io=io)
            self.compression = 'NONE'
            log.info(f'{self.filename} was not compressed.')

    def save(self, destfile=None):
        if destfile is None:
            destfile = self.filename
            log.info('No save destination specified.')
        if self.compression == 'GZIP':
            with gzip.open(destfile, 'wb') as io:
                self.saveNBT(io)
            log.info(f'GZIP compression applied to \"{destfile}\".')
        elif self.compression == 'NONE':
            with open(destfile, 'wb') as io:
                self.saveNBT(io)
            log.info(f'No compression applied to \"{destfile}\".')


class RegionFile(Region):
    def __init__(self, filename):
        self.filename = filename
        if isinstance(filename, Path):
            tn = filename.name
        else:
            tn = filename

        n = re.search('r\.(?P<x>-?.+)\.(?P<z>-?.+)(?=\.mca)', tn)
        if n is None:
            log.warning('Invalid region filename!')
            coords = 0, 0
        else:
            coords = int(n.group('x')), int(n.group('z'))

        super().__init__(coords)
        with open(self.filename, 'rb') as io:
            self.decode(io)

        log.info(f'Loaded \"{self.filename}\" as Region{coords}')

    def save(self, destfile=None):
        if destfile is None:
            destfile = self.filename
        else:
            n = re.search('r\.-?.\.-?.(?=\.mca)', destfile)
            if n is None:
                log.warning('Invalid region filename!'
                            ' Minecraft will not be able to read this file!')

        with open(destfile, 'wb') as io:
            self.encode(io)

        log.info(f'Saved Region to \"{destfile}\"')
