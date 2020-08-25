import os
from io import BytesIO
from struct import unpack

from ultimapy.settings import ultima_file_path

from .verdata import Verdata


class FileIndex:
    """No current UOP support."""
    def __init__(self, idx_filename, mul_filename, length, file_idx):
        try:
            index_file = None
            self.index_file_path = ultima_file_path(idx_filename)
            index_file = open(self.index_file_path, 'rb')
            self.mul_file_path = ultima_file_path(mul_filename)
        except FileNotFoundError:
            print(f"No file for index {idx_filename if not index_file else mul_filename}")
            return
        idx_file_bytes = len(index_file.read())
        index_file.seek(0)
        count = int(idx_file_bytes / 12)
        length = length or count
        self.index_length = idx_file_bytes
        self.index = []
        for i in range(count):
            self.index.append(Entry3D(*unpack('i'*3, index_file.read(4*3))))
        for i in range(count, length):
            self.index.append(Entry3D(-1, -1, -1))
        patches = Verdata.patches
        if file_idx > -1:
            for idx, patch in enumerate(patches):
                if patch.file == file_idx and 0 < patch.index < length:
                    self.index[patch.index].lookup = patch.lookup
                    self.index[patch.index].length = patch.length | (1 << 31)
                    self.index[patch.index].extra = patch.extra

    def seek(self, index, is_validation=False):
        null_return = None, 0, 0, False
        if index >= len(self.index) or index < 0:
            return null_return
        entry = self.index[index]
        if entry.lookup < 0 or entry.length < 0:
            return null_return

        length = entry.length & 0x7FFFFFFF
        extra = entry.extra
        patched = False

        if (entry.length & (1 << 31)) != 0:
            patched = True
            stream = Verdata.FILE
            stream.seek(entry.lookup)
            return BytesIO(stream.read(length)), length, extra, patched

        if not is_validation:
            with open(self.mul_file_path, 'rb') as stream:
                stream.seek(entry.lookup)
                byte_stream = BytesIO(stream.read(length))
            return byte_stream, length, extra, patched

        return True, length, extra, patched

    def valid(self, index):
        stream, length, extra, patched = self.seek(index, is_validation=True)
        return bool(stream), length, extra, patched


class Entry3D:
    def __init__(self, lookup, length, extra):
        self.lookup = lookup
        self.length = length
        self.extra = extra
