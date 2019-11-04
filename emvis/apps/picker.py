#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw

import datavis as dv
import emvis as emv

from ._utils import *



def main(argv):
    argv = argv or sys.argv

    app = qtw.QApplication(argv)
    paramCount = 0

    kwargs = {}

    argParser = argparse.ArgumentParser(usage='Tool for Viewer Apps',
                                        description='Display the selected '
                                                    'viewer app',
                                        prefix_chars='--',
                                        argument_default=None)

    # GLOBAL PARAMETERS
    argParser.add_argument('files', type=str, nargs='*', default=[],
                           help='3D image path or a list of image files or'
                           ' specific directory')

    # EM-BROWSER PARAMETERS
    on_off_dict = {'on': True, 'off': False}
    on_off = capitalizeStrList(on_off_dict.keys())
    argParser.add_argument('--zoom', type=str, default=True, required=False,
                           choices=on_off, action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Enable/disable the option to zoom in/out in '
                                'the image(s)')
    argParser.add_argument('--axis', type=str, default=True, required=False,
                           choices=on_off, action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Show/hide the image axis (ImageView)')
    argParser.add_argument('--tool-bar', type=str, default=True, required=False,
                           choices=on_off, action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Show or hide the toolbar for ImageView')
    argParser.add_argument('--histogram', type=str, default=False,
                           required=False, choices=on_off,
                           action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Show or hide the histogram for ImageView')
    argParser.add_argument('--fit', type=str, default=True,
                           required=False, choices=on_off,
                           action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Enables fit to size for ImageView')
    viewsDict = {
        'gallery': dv.views.GALLERY,
        'columns': dv.views.COLUMNS,
        'items': dv.views.ITEMS,
        'slices': dv.views.SLICES
    }
    views_params = capitalizeStrList(viewsDict.keys())

    argParser.add_argument('--view', type=str, default='', required=False,
                           choices=views_params, action=ValidateValues,
                           valuesDict=viewsDict,
                           help=' The default view. Default will depend on the '
                                'input')
    argParser.add_argument('--size', type=int, default=64,
                           required=False,
                           help=' The default size of the displayed image, '
                                'either in pixels or in percentage')

    # Picker arguments
    argParser.add_argument('--picker', type=str, nargs='*', default=[],
                           required=False, action=ValidateMics,
                           help='Show the Picker tool. '
                                '2 path pattern for micrograph and coordinates '
                                'files.')
    argParser.add_argument('--boxsize', type=int, default=100,
                           required=False,
                           help=' an integer for pick size(Default=100).')
    shapeDict = {
        'RECT': dv.views.SHAPE_RECT,
        'CIRCLE': dv.views.SHAPE_CIRCLE,
        'CENTER': dv.views.SHAPE_CENTER,
        'SEGMENT': dv.views.SHAPE_SEGMENT
    }
    shape_params = capitalizeStrList(shapeDict.keys())
    argParser.add_argument('--shape', default=dv.views.SHAPE_CIRCLE,
                           required=False, choices=shape_params,
                           valuesDict=shapeDict,
                           action=ValidateValues,
                           help=' the shape type '
                                '[CIRCLE, RECT, CENTER or SEGMENT]')
    pickerDict = {
        'default': dv.views.DEFAULT_MODE,
        'filament': dv.views.FILAMENT_MODE
    }
    picker_params = capitalizeStrList(pickerDict.keys())
    argParser.add_argument('--picker-mode', type=str,
                           default=dv.views.DEFAULT_MODE, required=False,
                           choices=picker_params, valuesDict=pickerDict,
                           action=ValidateValues,
                           help=' the picker type [default or filament]')
    argParser.add_argument('--remove-rois', type=str, default=True,
                           required=False, choices=on_off,
                           action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Enable/disable the option. '
                                'The user will be able to eliminate rois')
    argParser.add_argument('--roi-aspect-locked', type=str, default=True,
                           required=False, choices=on_off,
                           action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Enable/disable the option. '
                                'The rois will retain the aspect ratio')
    argParser.add_argument('--roi-centered', type=str, default=True,
                           required=False, choices=on_off,
                           action=ValidateValues,
                           valuesDict=on_off_dict,
                           help=' Enable/disable the option. '
                                'The rois will work accordance with its center')
    # COLUMNS PARAMS
    argParser.add_argument('--visible', type=str, nargs='?', default='',
                           required=False, action=ValidateStrList,
                           help=' Columns to be shown (and their order).')
    argParser.add_argument('--render', type=str, nargs='?', default='',
                           required=False, action=ValidateStrList,
                           help=' Columns to be rendered.')
    argParser.add_argument('--sort', type=str, nargs='?', default='',
                           required=False, action=ValidateStrList,
                           help=' Sort command.')

    args = argParser.parse_args()

    models = None
    delegates = None

    # ARGS
    files = []
    for f in args.files:
        files.append(qtc.QDir.toNativeSeparators(f))

    if not files and not args.picker:
        files = [str(os.getcwd())]  # if not files use the current dir

    kwargs['files'] = files
    kwargs['zoom'] = args.zoom
    kwargs['histogram'] = args.histogram
    kwargs['roi'] = False
    kwargs['menu'] = False
    kwargs['popup'] = False
    kwargs['toolBar'] = args.tool_bar
    kwargs['img_desc'] = False
    kwargs['fit'] = args.fit
    kwargs['axis'] = args.axis
    kwargs['size'] = args.size
    kwargs['maxCellSize'] = 300
    kwargs['minCellSize'] = 25
    kwargs['zoom_units'] = dv.views.PIXEL_UNITS
    kwargs['views'] = {dv.views.GALLERY: {}, dv.views.COLUMNS: {},
                       dv.views.ITEMS: {}}

    kwargs['view'] = args.view
    kwargs['selectionMode'] = dv.views.PagingView.MULTI_SELECTION

    # Picker params
    kwargs['boxSize'] = args.boxsize
    kwargs['pickerMode'] = args.picker_mode
    kwargs['shape'] = args.shape
    kwargs['removeRois'] = args.remove_rois
    kwargs['roiAspectLocked'] = args.roi_aspect_locked
    kwargs['roiCentered'] = args.roi_centered

    def getPreferedBounds(width=None, height=None):
        size = qtw.QApplication.desktop().size()
        p = 0.8
        (w, h) = (int(p * size.width()), int(p * size.height()))
        width = width or w
        height = height or h
        w = min(width, w)
        h = min(height, h)
        return (size.width() - w) / 2, (size.height() - h) / 2, w, h

    def fitViewSize(viewWidget, imageDim=None):
        """
        Fit the view size according to the desktop size.
        imageDim is the image dimensions if viewWidget is ImageView
         """
        if view is None:
            return

        if isinstance(viewWidget, dv.views.DataView):
            size = viewWidget.getPreferredSize()
            x, y, w, h = getPreferedBounds(size[0], size[1])
        elif (isinstance(viewWidget, dv.views.ImageView) or
                isinstance(viewWidget, dv.views.SlicesView) or
                isinstance(viewWidget, dv.views.PickerView)) and \
                imageDim is not None:
            dx, dy = imageDim[0], imageDim[1]
            x, y, w, h = getPreferedBounds(max(viewWidget.width(), dx),
                                           max(viewWidget.height(), dy))
            size = qtc.QSize(dx, dy).scaled(w, h, qtc.Qt.KeepAspectRatio)
            dw, dh = w - size.width(), h - size.height()
            x, y, w, h = x + dw/2, y + dh/2, size.width(), size.height()
        else:
            x, y, w, h = getPreferedBounds(100000,
                                           100000)
        viewWidget.setGeometry(x, y, w, h)

    def showMsgBox(text, icon=None, details=None):
        """
        Show a message box with the given text, icon and details.
        The icon of the message box can be specified with one of the Qt values:
            QMessageBox.NoIcon
            QMessageBox.Question
            QMessageBox.Information
            QMessageBox.Warning
            QMessageBox.Critical
        """
        msgBox = qtw.QMessageBox()
        msgBox.setText(text)
        msgBox.setStandardButtons(qtw.QMessageBox.Ok)
        msgBox.setDefaultButton(qtw.QMessageBox.Ok)
        if icon is not None:
            msgBox.setIcon(icon)
        if details is not None:
            msgBox.setDetailedText(details)

        msgBox.exec_()

    try:
        d = None
        if args.picker in ['on', 'On'] or isinstance(args.picker, dict):
            if files and files[0] == str(os.getcwd()):
                files = None
            kwargs['selectionMode'] = dv.views.PagingView.SINGLE_SELECTION
            view = emv.views.ViewsFactory.createPickerView(
                files, sources=args.picker, parseCoordFunc=parsePickCoordinates,
                **kwargs)
            view.setWindowTitle("EM-PICKER")
            d = view.getPreferredSize()
        else:
            # If the input is a directory, display the BrowserWindow
            if len(files) > 1:
                raise Exception("Multiple files are not supported")
            else:
                files = files[0]

            if not emv.utils.EmPath.exists(files):
                raise Exception("Input file '%s' does not exists. " % files)

            if os.path.isdir(files):
                kwargs['rootPath'] = files
                kwargs['mode'] = dv.widgets.TreeModelView.DIR_MODE

                view = emv.views.EmBrowser(**kwargs)
            elif emv.utils.EmPath.isTable(files):  # Display the file as a Table
                if not args.view == dv.views.SLICES:
                    if args.visible or args.render:
                        # FIXME[phv] create the TableConfig
                        pass
                    else:
                        tableViewConfig = None
                    if args.sort:
                        # FIXME[phv] sort by the given column
                        pass
                    kwargs['view'] = args.view or dv.views.COLUMNS
                    view = emv.views.ViewsFactory.createDataView(files,
                                                                 **kwargs)
                    fitViewSize(view, d)
                else:
                    raise Exception("Invalid display mode for table: '%s'"
                                    % args.view)
            elif emv.utils.EmPath.isData(files):
                # *.mrc may be image, stack or volume. Ask for dim.n
                x, y, z, n = emv.utils.ImageManager().getDim(files)
                if n == 1:  # Single image or volume
                    if z == 1:  # Single image
                        view = emv.views.ViewsFactory.createImageView(files,
                                                                      **kwargs)
                    else:  # Volume
                        mode = args.view or dv.views.SLICES
                        if mode == dv.views.SLICES or mode == dv.views.GALLERY:
                            kwargs['toolBar'] = False
                            kwargs['axis'] = False
                            sm = dv.views.PagingView.SINGLE_SELECTION
                            kwargs['selectionMode'] = sm
                            view = emv.views.ViewsFactory.createVolumeView(
                                files, **kwargs)
                        else:
                            raise Exception("Invalid display mode for volume")
                else:  # Stack
                    m = dv.views.PagingView.SINGLE_SELECTION
                    kwargs['selectionMode'] = m
                    if z > 1:  # volume stack
                        mode = args.view or dv.views.SLICES
                        if mode == dv.views.SLICES:
                            kwargs['toolBar'] = False
                            kwargs['axis'] = False
                            view = emv.views.ViewsFactory.createVolumeView(
                                files, **kwargs)
                        else:
                            kwargs['view'] = dv.views.GALLERY
                            view = emv.views.ViewsFactory.createDataView(
                                files, **kwargs)
                    else:
                        ms = dv.views.MOVIE_SIZE
                        mode = args.view or (dv.views.SLICES if x > ms
                                             else dv.views.GALLERY)
                        if mode == dv.views.SLICES:
                            view = emv.views.ViewsFactory.createSlicesView(
                                files, **kwargs)
                        else:
                            kwargs['view'] = mode
                            view = emv.views.ViewsFactory.createDataView(
                                files, **kwargs)
            elif emv.utils.EmPath.isStandardImage(files):
                view = emv.views.ViewsFactory.createImageView(files, **kwargs)
            else:
                view = None
                raise Exception("Can't perform a view for this file.")

        if view:
            fitViewSize(view, d)
            view.show()

    except Exception as ex:
        showMsgBox("Can't perform the action", qtw.QMessageBox.Critical,
                   str(ex))
        print(traceback.format_exc())
        sys.exit(0)
    except RuntimeError as ex:
        showMsgBox("Can't perform the action", qtw.QMessageBox.Critical,
                   str(ex))
        print(traceback.format_exc())
        sys.exit(0)
    except ValueError as ex:
        showMsgBox("Can't perform the action", qtw.QMessageBox.Critical,
                   str(ex))
        print(traceback.format_exc())
        sys.exit(0)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()