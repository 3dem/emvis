#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
import textwrap

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw

import datavis as dv
import emvis as emv

from ._utils import *


class BoxArgsDict(dict):
    SHAPE_DICT = {
        'rect': dv.views.SHAPE_RECT,
        'circle': dv.views.SHAPE_CIRCLE,
        'center': dv.views.SHAPE_CENTER,
        'segment': dv.views.SHAPE_SEGMENT,
        'segment_line': dv.views.SHAPE_SEGMENT_LINE
    }

    def __init__(self):
        dict.__init__(self, [('size', 100),
                             ('shape', dv.views.SHAPE_CIRCLE)])

    def __setitem__(self, key, value):
        if key == 'shape':
            v = value.lower()
            if v not in self.SHAPE_DICT:
                raise Exception("Incorrect shape value '%s'" % value)
            value = self.SHAPE_DICT[v]
        dict.__setitem__(key, value)

    def getMode(self):
        # Filament shape constants are greater than SHAPE_CENTER
        return (dv.views.FILAMENT_MODE
                if self['shape'] > dv.views.SHAPE_CENTER
                else dv.views.DEFAULT_MODE)


def main(argv=None):
    argv = argv or sys.argv[1:]

    app = qtw.QApplication(argv)
    paramCount = 0

    argParser = argparse.ArgumentParser(
        usage='em-picker',
        description='Tool for visualizing particle picking results',
        prefix_chars='--',
        formatter_class=argparse.RawTextHelpFormatter)

    # Picker arguments
    argParser.add_argument(
        'input', nargs='+',
        help='Provide input Micrographs and, optionally, Coordinates.')

    argParser.add_argument(
        '--box', action=ArgDictAction, default=BoxArgsDict(), nargs='+',
        argsDictClass=BoxArgsDict,
        help=textwrap.dedent("""
            Provide options specific for the box.
            Options:
               size:   (int) Width of the box (it will be also the height if not in Filament mode)
               shape:  (string) Shape of the box: rect, circle or center, when not in Filament mode.
                       For filaments valid shapes are: segment and segment_line.
            """))

    args = argParser.parse_args()

    kwargs = {
        #'scale': args.display['scale'],
        #'histogram': args.display['histogram'],
        #'toolBar': args.display['toolbar'],
        #'fit': args.display['fit'],
        'boxSize': args.box['size'],
        'pickerMode': args.box.getMode(),
        'shape': args.box['shape']
    }

    micsFolder = args.input[0]

    def _createView():
        model = emv.models.ModelsFactory.createPickerModel(micsFolder)
        return dv.views.PickerView(model, **kwargs)

    dv.views.showView(_createView, title="EM-PICKER")


if __name__ == '__main__':
    main()