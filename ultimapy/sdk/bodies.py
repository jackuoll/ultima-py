from ultimapy.settings import ultima_file_path

from .utils import safe_list_get


class BodyConverter:
    """No known issues."""
    loaded = False
    TABLE_1 = []
    TABLE_2 = []
    TABLE_3 = []
    TABLE_4 = []

    @classmethod
    def load(cls):
        print("Loading BodyConverter")
        f = open(ultima_file_path('Bodyconv.def'), 'r')
        max1 = max2 = max3 = max4 = 0
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split("\t")
            try:
                orig = int(safe_list_get(fields, 0, -1))
                anim2 = int(safe_list_get(fields, 1, -1))
                anim3 = int(safe_list_get(fields, 2, -1))
                anim4 = int(safe_list_get(fields, 3, -1))
                anim5 = int(safe_list_get(fields, 4, -1))
            except:
                continue
            if anim2 >= 0:
                anim2 = 122 if anim2 == 68 else anim2
                max1 = max(max1, orig)
                list1.append(orig)
                list1.append(anim2)
            if anim3 >= 0:
                max2 = max(max2, orig)
                list2.append(orig)
                list2.append(anim3)
            if anim4 >= 0:
                max3 = max(max3, orig)
                list3.append(orig)
                list3.append(anim4)
            if anim5 >= 0:
                max4 = max(max4, orig)
                list4.append(orig)
                list4.append(anim5)
        cls.TABLE_1 = [-1 for i in range(max1 + 1)]
        cls.TABLE_2 = [-1 for i in range(max2 + 1)]
        cls.TABLE_3 = [-1 for i in range(max3 + 1)]
        cls.TABLE_4 = [-1 for i in range(max4 + 1)]
        for i in range(0, len(list1), 2):
            cls.TABLE_1[list1[i]] = list1[i + 1]
        for i in range(0, len(list2), 2):
            cls.TABLE_2[list2[i]] = list2[i + 1]
        for i in range(0, len(list3), 2):
            cls.TABLE_3[list3[i]] = list3[i + 1]
        for i in range(0, len(list4), 2):
            cls.TABLE_4[list4[i]] = list4[i + 1]
        cls.loaded = True

    @classmethod
    def contains(cls, body):
        if body < 0:
            return False
        for table in [cls.TABLE_1, cls.TABLE_2, cls.TABLE_3, cls.TABLE_4]:
            if safe_list_get(table, body, -1) >= 0:
                return True
        return False

    @classmethod
    def convert(cls, body):
        if body < 0:
            return False
        for idx, table in enumerate([cls.TABLE_1, cls.TABLE_2, cls.TABLE_3, cls.TABLE_4]):
            new_body = safe_list_get(table, body, -1)
            if new_body != -1:
                return new_body, idx + 1
        return body, 1  # todo: default to returning orig body + 1 file idx, is it correct?

    @classmethod
    def get_true_body(cls, file_type, index):
        if file_type > 5 or file_type < 0 or index < 0:
            return -1
        if file_type == 1:
            return index
        try:
            return [cls.TABLE_1, cls.TABLE_2, cls.TABLE_3, cls.TABLE_4][file_type - 2].index(index)
        except ValueError:
            pass
        return -1


class BodyTable:
    entries = {}

    @classmethod
    def load(cls):
        print("Loading BodyTable")
        f = open(ultima_file_path('Body.def'), 'r')
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # ultima sdk try catches this, but there are no exceptions thrown
            index1 = line.index("{")
            index2 = line.index("}")
            param1 = line[:index1].strip()
            param2 = line[index1+1:index2]
            param3 = line[index2+1:].strip()
            if "," in param2:
                param2 = param2[:param2.index(",")].strip()
            cls.entries[int(param1)] = BodyTableEntry(int(param2), int(param1), int(param3))


class BodyTableEntry:
    def __init__(self, old_id, new_id, new_hue):
        self.old_id = old_id
        self.new_id = new_id
        self.new_hue = new_hue


if not BodyTable.entries:
    BodyTable.load()
if not BodyConverter.loaded:
    BodyConverter.load()