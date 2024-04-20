from struct import unpack

from ultimapy.settings import ultima_file_path


class Verdata:
    """
        No reason to instantiate.
        Assumed to be working as per C# Ultima SDK but untested.
    """
    patches = []
    _stream = None

    @classmethod
    def get_stream(cls):
        if cls._stream is not None:
            return cls._stream
        try:
            return open(ultima_file_path('verdata.mul'), 'rb')
        except FileNotFoundError:
            pass

    @classmethod
    def load(cls):
        stream = cls.get_stream()
        if stream is None:
            return
        total_patches = unpack('i', stream.read(4))[0]
        for i in range(total_patches):
            cls.patches.append(Entry5D(*unpack('i'*5, stream.read(20))))

    @classmethod
    def seek(cls, lookup):
        stream = cls.get_stream()
        if stream is None:
            return
        stream.Seek(lookup)



class Entry5D:
    def __init__(self, file, index, lookup, length, extra):
        self.file = file
        self.index = index
        self.lookup = lookup
        self.length = length
        self.extra = extra


if len(Verdata.patches) == 0:
    print("Loading Verdata")
    Verdata.load()
