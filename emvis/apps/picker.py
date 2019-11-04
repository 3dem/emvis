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


def main(argv):
    argv = argv or sys.argv

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
        '--box', action=ArgDictAction, default=BoxArgsDict(),
        argsDictClass=BoxArgsDict,
        help=textwrap.dedent("""
            Provide options specific for the box.
            Options:
               size:   (int) Width of the box (it will be also the height if not in Filament mode)
               shape:  (string) Shape of the box: rect, circle or center, when not in Filament mode.
                       For filaments valid shapes are: segment and segment_line.
            """))

    # pickerDict = {
    #     'default': dv.views.DEFAULT_MODE,
    #     'filament': dv.views.FILAMENT_MODE
    # }
    # picker_params = capitalizeStrList(pickerDict.keys())
    # argParser.add_argument('--picker-mode', type=str,
    #                        default=dv.views.DEFAULT_MODE, required=False,
    #                        choices=picker_params, valuesDict=pickerDict,
    #                        action=ValidateValues,
    #                        help=' the picker type [default or filament]')

    # argParser.add_argument('--remove-rois', type=str, default=True,
    #                        required=False, choices=on_off,
    #                        action=ValidateValues,
    #                        valuesDict=on_off_dict,
    #                        help=' Enable/disable the option. '
    #                             'The user will be able to eliminate rois')
    # argParser.add_argument('--roi-aspect-locked', type=str, default=True,
    #                        required=False, choices=on_off,
    #                        action=ValidateValues,
    #                        valuesDict=on_off_dict,
    #                        help=' Enable/disable the option. '
    #                             'The rois will retain the aspect ratio')
    # argParser.add_argument('--roi-centered', type=str, default=True,
    #                        required=False, choices=on_off,
    #                        action=ValidateValues,
    #                        valuesDict=on_off_dict,
    #                        help=' Enable/disable the option. '
    #                             'The rois will work accordance with its center')

    args = argParser.parse_args()

    # # ARGS
    # files = []
    # for f in args.files:
    #     files.append(qtc.QDir.toNativeSeparators(f))
    #
    # if not files and not args.picker:
    #     files = [str(os.getcwd())]  # if not files use the current dir

    kwargs['files'] = files

    kwargs['histogram'] = args.histogram
    kwargs['toolBar'] = args.tool_bar

    kwargs['img_desc'] = False
    kwargs['fit'] = args.fit
    kwargs['axis'] = args.axis
    kwargs['zoom_units'] = dv.views.PIXEL_UNITS

    # Picker params
    kwargs['boxSize'] = args.box['size']
    kwargs['pickerMode'] = args.picker_mode
    kwargs['shape'] = args.box['shape']

    # kwargs['removeRois'] = args.remove_rois
    # kwargs['roiAspectLocked'] = args.roi_aspect_locked
    # kwargs['roiCentered'] = args.roi_centered

    from datavis.views import showView

    def _createView():
        return emv.views.ViewsFactory.createPickerView(
            files, sources=args.picker,
            **kwargs)

    showView()

    view.setWindowTitle("EM-PICKER")
    print(traceback.format_exc())

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()