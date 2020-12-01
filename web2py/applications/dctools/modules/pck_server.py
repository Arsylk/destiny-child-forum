#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import pck_tools
import os
import time
import shutil


# TODO change hard-coded path
idxx = (round(time.time()) % 86400)
model_base_path = "/home/Arsylk/web2py/applications/dctools/static/models/%s"
model_base_file = "/home/Arsylk/web2py/applications/dctools/static/models/%s.pck"


def pck_to_model(name, content):
    # format paths
    model_path = model_base_path % name
    model_file = model_base_file % name

    # fail-safe
    try:
        # remove model if already exists
        try:
            os.mkdir(model_path)
        except:
            pass

        # save model file
        with open(model_file, 'wb') as fs:
            fs.write(content)

        # unpack model pck
        pck = pck_tools.unpack_pck(model_file)
        pck_tools.pck_to_model(pck)
        pck_universal = pck_tools.pack_pck(pck)

        # try get model id
        idx = None
        model_json = pck_tools.read_json(os.path.join(model_path, 'model.json'))
        if 'motions' in model_json:
            first_motion = next(iter(model_json['motions']))
            motion_name = model_json['motions'][first_motion][0]['file']
            idx = motion_name[:motion_name.find('_', motion_name.find('_') + 1)]

        # if could not determine idx
        if not idx:
            raise TypeError

        # move to proper directory
        shutil.move(model_path, model_base_path % (idx + '-' + name))

        # remove old file
        os.remove(model_file)

        # create new file
        pck_tools.save_file(pck_universal, model_base_path % (idx + '-' + name), idx + ".pck")

        return idx, pck_universal
    except:
        # fully fail-safe clean up
        if model_path != model_base_path and len(name) > 0:
            for file in os.listdir(model_path):
                file_path = os.path.join(model_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            os.rmdir(model_path)
        os.remove(model_file)

        return None, None


def model_to_pck(path, name):
    # format paths
    model_path = (model_base_path % path) + '/_header'

    # fail safe
    try:
        pck = pck_tools.from_header(model_path)
        return pck_tools.save_file(pck_tools.pack_pck(pck), pck.path, name + ".pck")
    except:
        pass
    return None


def pck_restore(path, content):
    # format paths
    model_path = model_base_path % path
    model_file = model_base_file % path
    try:
        os.mkdir(model_path)
    except:
        pass

    # save model file
    with open(model_file, 'wb') as fs:
        fs.write(content)

    # unpack model pck
    pck = pck_tools.unpack_pck(model_file)
    pck_tools.pck_to_model(pck)

    # remove old file
    os.remove(model_file)
