# import re
#
# from enum import *
#
#
# class StringEntry:
#     class ClilocFlag(Flag):
#         orig = 0x0,
#         custom = 0x1,
#         modified = 0x2
#
#     number = -1
#     text = ''
#     flag = ClilocFlag.orig.value
#     regex = re.regex("~(\d+)[_\w]+~")  # todo: ??
#
#     def __init__(self, number, text, flag):
#         self.number = number
#         self.text = text
#         self.flag = flag  # todo: byte / clilocflag?
#
#     def format(self):
#         if not self.format_text:
#             self.format_text = re.replace()
# todo: cbf with regex right now