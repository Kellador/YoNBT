import gzip
import zlib
import logging
import coloredlogs
from nbt import NBTObj

log = logging.getLogger('nbt')
coloredlogs.install(level='DEBUG', logger=log)


class NBTFile(NBTObj):
    def __init__(self, filename):
        self.filename = filename
        try:
            with gzip.open(self.filename, 'rb') as io:
                super().__init__(io=io)
            self.compression = 'GZIP'
        except IOError:
            with open(self.filename, 'rb') as io:
                super().__init__(io=io)
            self.compression = 'NONE'

    def save(self, destfile=None):
        if destfile is None:
            destfile = self.filename
        if self.compression == 'GZIP':
            with gzip.open(destfile, 'wb') as io:
                self.saveNBT(io)
        elif self.compression == 'NONE':
            with open(destfile, 'wb') as io:
                self.saveNBT(io)
