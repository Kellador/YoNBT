import gzip
import logging
import re
import coloredlogs
from nbt import NBTObj
from region import Region

log = logging.getLogger('nbt')
coloredlogs.install(level='DEBUG', logger=log)


class NBTFile(NBTObj):
    def __init__(self, filename):
        self.filename = filename
        try:
            with gzip.open(self.filename, 'rb') as io:
                super().__init__(io=io)
                io.close()
            self.compression = 'GZIP'
        except IOError:
            with open(self.filename, 'rb') as io:
                super().__init__(io=io)
                io.close()
            self.compression = 'NONE'

    def save(self, destfile=None):
        if destfile is None:
            destfile = self.filename
        if self.compression == 'GZIP':
            with gzip.open(destfile, 'wb') as io:
                self.saveNBT(io)
                io.close()
        elif self.compression == 'NONE':
            with open(destfile, 'wb') as io:
                self.saveNBT(io)
                io.close()


class RegionFile(Region):
    def __init__(self, filename):
        self.filename = filename
        n = re.search('r\..\..(?=\.mca)', filename)
        if n is None:
            log.warning('Invalid region filename!'
                        ' Minecraft will not be able to read this file!')
            name = filename
        else:
            name = n[0]
        with open(self.filename, 'rb') as io:
            super().__init__(name=name, io=io)
            io.close()

    def save(self, destfile=None):
        if destfile is None:
            destfile = self.filename
        else:
            n = re.search('r\..\..(?=\.mca)', destfile)
            if n is None:
                log.warning('Invalid region filename!'
                            ' Minecraft will not be able to read this file!')
        with open(destfile, 'wb') as io:
            self.encodeRegion(io)
            io.close()
