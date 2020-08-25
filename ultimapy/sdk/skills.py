from struct import error, unpack

from ultimapy.settings import ultima_file_path

from .file_index import FileIndex


class SkillGroup:
    categories = []
    skill_list = []
    unicode = False

    @classmethod
    def load(cls):
        def read_char():
            return unpack('c', f.read(1))[0].decode('cp1252') if not cls.unicode else chr(unpack('h', f.read(2))[0])
        Skills.load()
        with open(ultima_file_path('skillgrp.mul'), 'rb') as f:
            start = 4
            strlen = 17
            count = unpack('i', f.read(4))[0]
            if count == -1:
                cls.unicode = True
                count = unpack('i', f.read(4))[0]
                start *= 2
                strlen *= 2

            cls.categories.append("Misc")
            for i in range(count - 1):
                f.seek(start + (i * strlen))
                name = ''
                c = read_char()
                while c != '\x00':
                    name += c
                    c = read_char()
                cls.categories.append(name)
            f.seek(start + (count-1)*strlen)
            skill_num = unpack('i', f.read(4))[0]
            for i, skill in enumerate(Skills.entries):
                skill.category = cls.categories[skill_num]
                try:
                    skill_num = unpack('i', f.read(4))[0]
                except error:
                    break


class Skills:
    entries = []
    @classmethod
    def load(cls):
        cls.file_index = FileIndex(ultima_file_path('Skills.idx'), ultima_file_path('skills.mul'), None, 16)
        for i in range(cls.file_index.index_length):
            stream, length, extra, patched = cls.file_index.seek(i)
            if stream is None:
                continue
            is_action = unpack('?', stream.read(1))[0]
            name = unpack(f'{(length-1)}s', stream.read(length-1))[0].decode('cp1252')[:-1]
            cls.entries.append(SkillInfo(i, name, is_action, extra))


class SkillInfo:
    def __init__(self, num, name, is_action, extra):
        self.index = num
        self.name = name or ''
        self.is_action = is_action
        self.extra = extra
        self.category = None


if not getattr(Skills, 'file_index', False):
    print("Loading skills")
    SkillGroup.load()
