#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import json


class Pck:
    def __init__(self, path, head, count, lang=None):
        self.path = path
        self.head = head
        self.count = count
        self.lang = lang

        self.files = []

    def add_file(self, path, hash, flag, ext):
        self.files.append(PckFile(path, hash, flag, ext, self.lang))

    def get_file(self, path=None, hash=None):
        for file in self.files:
            if file.path == path or file.hash.lower() == hash.lower():
                return file

    def get_files(self):
        return self.files

    def write_header(self):
        _header = {}
        for i, file in enumerate(self.files):
            _header[file.path[file.path.rfind("/")+1:]] = file.hash
        with open(self.path[:self.path.rfind(".")]+"/_header", "w") as output:
            output.write(json.dumps(_header, sort_keys=False, indent=4))


class PckFile:
    SPACE = 0
    EQUALS = 1
    EXT_STR = {109: "dat", 35: "mtn", 137: "png", 123: "json"}

    def __init__(self, path, hash, flag, ext, lang=None):
        self.path = path
        self.hash = hash
        self.flag = flag
        self.ext = ext
        self.lang = lang

        self.dict = {}
        self.line_type = None

    def read(self):
        with open(self.path, "r", encoding="utf-8-sig", errors="replace") as file:
            return file.read()

    def read_bin(self):
        with open(self.path, "rb") as file:
            return file.read()

    def to_json(self):
        if not self.dict:
            self.to_dict()
        json = {"hash": self.hash, "line_type": self.line_type, "dict": {}}
        for key in self.dict:
            json["dict"][key] = self.dict[key]
        return json

    def to_dict(self):
        self.dict = {}
        for line in self.read().split("\n"):
            if not line:
                continue
            if line.startswith("//"):
                continue
            entry = self.line(line)
            self.dict[entry[0]] = entry[1]
        return self.dict

    def line(self, line):
        index = -1
        for i in range(len(line)):
            if line[i].isspace() or line[i] == "=":
                index = i
                break
        if index == -1:
            raise Exception("wrong line format")

        key = line[:index].rstrip()
        value = line[index:].lstrip().replace("[value]", "{value}").replace("[value_1]", "{value_1}")

        if value.find("=") == 0:
            self.line_type = self.EQUALS
            value = value[value.find("="):].lstrip()
            value = value[value.find("\"")+1:value.rfind("\"")]
        else:
            self.line_type = self.SPACE

        return key, value

    def get_ext_string(self):
        if self.ext in PckFile.EXT_STR:
            return PckFile.EXT_STR[self.ext]
        return "unk"

    def __str__(self):
        return "<pck_struct._PckFile hash={} path={} ext={} flag={:02d} lang={}>"\
            .format(self.hash.upper(), self.path, self.ext, self.flag, self.lang)
