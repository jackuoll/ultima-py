import ctypes
import os
from io import BytesIO
from pathlib import Path
from struct import unpack
from typing import Optional

from ultimapy.settings import ultima_file_path
from . import utils

from .verdata import Verdata


class FileIndex:
    def __init__(
        self,
        idx_filename: str,
        mul_filename: str,
        length: int,
        file_idx: int,
        uop_file: Optional[str] = None,
        uop_entry_extension: Optional[str] = None,
        uop_has_extra: Optional[bool] = None,
        uop_idx_length: Optional[int] = None
    ):
        """would really benefit from refactoring to not have the worst instantiation method of all time"""
        self.index = []
        if uop_file is not None and Path(ultima_file_path(uop_file)).exists():
            """uop file format does not use an index file."""
            self.index_length = uop_idx_length * 12 if uop_idx_length > 0 else 0
            # a lot of these might not be needed
            self.uop_file = uop_file
            self.file_name_without_ext = uop_file.replace(Path(uop_file).suffix, "").lower()
            self.uop_path = Path(ultima_file_path(uop_file))
            self.mul_file_path = str(self.uop_path)
            self.length = length
            self.uopEntryExtension = uop_entry_extension
            self.hasExtra = uop_has_extra
            self.file_stream = self.uop_path.open("rb")
            self.file_stream.seek(0)
            header = utils.read_int32(self.file_stream)
            if header != 0x50594D:
                raise ValueError(f"Invalid UOP file {uop_file}")
            utils.read_int64(self.file_stream)  # version + signature
            next_block = utils.read_int64(self.file_stream)
            utils.read_int32(self.file_stream)  # block capacity
            utils.read_int32(self.file_stream)  # TODO: check if we need value from here
            self.idx_length = uop_idx_length * 12
            hashes = {}
            for i in range(length):
                idx_str = str(i).zfill(8)
                entry_name = f"build/{self.file_name_without_ext}/{idx_str}{uop_entry_extension}"
                fn_hash = utils.hash_file_name(entry_name)
                # not sure if this actually matters.
                if fn_hash not in hashes:
                    hashes[fn_hash] = i
                else:
                    print("Warning: duplicate UOP hash!")
            self.file_stream.seek(next_block)
            for i in range(length):
                self.index.append(Entry3D(-1, -1, -1))

            # not totally sure this matches the do/while in c#
            while self.file_stream.seek(next_block) != 0:
                file_count = utils.read_int32(self.file_stream)
                next_block = utils.read_int64(self.file_stream)
                for i in range(file_count):
                    offset = utils.read_int64(self.file_stream)
                    header_length = utils.read_int32(self.file_stream)
                    compressed_length = utils.read_int32(self.file_stream)
                    decompressed_length = utils.read_int32(self.file_stream)
                    file_hash = utils.read_uint64(self.file_stream)
                    utils.read_int32(self.file_stream)  # adler32
                    flag = utils.read_int16(self.file_stream)
                    entry_length = compressed_length if flag == 1 else decompressed_length
                    # build/gumpartlegacymul/00000000.tga
                    idx = hashes.get(file_hash)
                    if offset == 0 or idx is None:
                        continue

                    if idx < 0 or idx > len(self.index):
                        raise ValueError("hashes dictionary and files collection have different count of entries!")

                    self.index[idx].lookup = offset + header_length
                    self.index[idx].length = entry_length

                    if not uop_has_extra:
                        continue

                    cur_pos = self.file_stream.tell()
                    self.file_stream.seek(offset + header_length)
                    extra = self.file_stream.read(8)
                    extra1 = ctypes.c_ushort((extra[3] << 24) | (extra[2] << 16) | (extra[1] << 8) | extra[0]).value
                    extra2 = ctypes.c_ushort((extra[7] << 24) | (extra[6] << 16) | (extra[5] << 8) | extra[4]).value
                    self.index[idx].lookup += 8  # ???
                    self.index[idx].extra = extra1 << 16 | ctypes.c_int32(extra2).value
                    self.file_stream.seek(cur_pos)
        else:  # is mul
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

    def seek(self, index: int, is_validation=False):
        null_return = None, 0, 0, False
        if index >= len(self.index) or index < 0:
            return null_return
        entry = self.index[index]
        if entry.lookup < 0 or entry.length < 0:
            # print(index, entry.lookup, entry.length, entry.extra)
            return null_return

        length = entry.length & 0x7FFFFFFF
        extra = entry.extra
        patched = False

        if (entry.length & (1 << 31)) != 0:
            patched = True
            stream = Verdata.get_stream()
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

    def __str__(self):
        return f"<Entry3D: lookup={self.lookup}, length={self.length}, extra={self.extra} />"
