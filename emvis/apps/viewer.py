#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
import textwrap

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw

import datavis as dv
import emvis as emv
from emvis.views import ViewsFactory

from ._utils import *


class DisplayArgsDict(dict):
    def __init__(self):
        dict.__init__(self, [('axis', True),
                             ('toolbar', True),
                             ('histogram', False),
                             ('fit', True),
                             ('scale', 1.0),
                             ('view', 'default')])


def main(argv=None):
    argv = argv or sys.argv[1:]

    argParser = argparse.ArgumentParser(
        usage='Tool for Viewer Apps',
        description='Display the selected '
                    'viewer app',
        prefix_chars='--',
        argument_default=None,
        formatter_class=argparse.RawTextHelpFormatter)

    # GLOBAL PARAMETERS
    argParser.add_argument(
        'path', nargs='?', help=textwrap.dedent("""
        Provide a path to be visualized.
        Path can be:
           directory: the browser will be shown at that path.
           image:     an ImageView will be shown with that image.
           volume:    a VolumeView will be used to show the volume.
        """))

    argParser.add_argument(
        '--display', nargs='+', action=ArgDictAction,
        default=DisplayArgsDict(),
        argsDictClass=DisplayArgsDict,
        help=textwrap.dedent("""
        Provide one or many key=value pairs with extra visualization options.
        Bool values support on/off, 0/1, true/false, yes/no
        Options:
           axis:      (bool) if false, axis will not be shown (default true)
           toolbar:   (bool) if false, toolbar will not be shown (default true)
           histogram: (bool) if false, histogram will not shown (default true)
           fit:       (bool) if false, the image will not be adjusted to widget size (default true)
           view:      (string) Select the initial view. Options: gallery, columns, items, slices
           scale:     (string) Select initial scale (use %% for percentage)
        """))


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

    args = argParser.parse_args(argv)
    app = qtw.QApplication([])

    # ARGS
    path = args.path or os.getcwd()
    print("argv: ", argv)
    print("path: ", path)


    kwargs = {
        'files': path,
        'scale': args.display['scale'],
        'histogram': args.display['histogram'],
        'toolBar': args.display['toolbar'],
        'fit': args.display['fit'],
        'axis': args.display['axis'],
        'img_desc': False,
        'maxCellSize': 300,
        'minCellSize': 25,
        'selection': dv.views.PagingView.MULTI_SELECTION,
        'views': {dv.views.GALLERY: {},
                  dv.views.COLUMNS: {},
                  dv.views.ITEMS: {}}
    }

    viewKey = args.display['view'].lower()
    viewsDict = {
        'gallery': dv.views.GALLERY,
        'columns': dv.views.COLUMNS,
        'items': dv.views.ITEMS,
        'slices': dv.views.SLICES,
        'default': None  # Just choose the default view for the widget
    }

    if not viewKey in viewsDict:
        raise Exception("Invalid view '%s' for --display. "
                        % args.display['view'])
    view = viewsDict[viewKey]

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
        if viewWidget is None:
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

    d = None
    viewWidget = None

    if not emv.utils.EmPath.exists(path):
        raise Exception("Input file '%s' does not exists. " % path)



    if os.path.isdir(path):
        kwargs['rootPath'] = path
        kwargs['mode'] = dv.widgets.TreeModelView.DIR_MODE

        viewWidget = emv.views.EmBrowser(**kwargs)

    elif emv.utils.EmPath.isTable(path):  # Display the file as a Table
        if view == dv.views.SLICES:
            raise Exception("Invalid display mode for table: '%s'" % view)

        if args.visible or args.render:
            # FIXME[phv] create the TableConfig
            pass
        else:
            tableViewConfig = None
        if args.sort:
            # FIXME[phv] sort by the given column
            pass
        kwargs['view'] = view or dv.views.COLUMNS
        viewWidget = ViewsFactory.createDataView(path, **kwargs)

    elif emv.utils.EmPath.isData(path):
        print("Data case")
        # *.mrc may be image, stack or volume. Ask for dim.n
        x, y, z, n = emv.utils.ImageManager().getDim(path)
        if n == 1:  # Single image or volume
            if z == 1:  # Single image
                viewWidget = ViewsFactory.createImageView(
                    path, **kwargs)
            else:  # Volume
                view = view or dv.views.SLICES
                if not view in [dv.views.SLICES, dv.views.GALLERY]:
                    raise Exception("Invalid display mode for volume")

                # kwargs['toolBar'] = False
                # kwargs['axis'] = False
                kwargs['view'] = view
                kwargs['selection'] = dv.views.PagingView.SINGLE_SELECTION
                viewWidget = ViewsFactory.createVolumeView(path, **kwargs)
        else:  # Stack
            print("Is stack")
            if z > 1:  # volume stack
                view = view or dv.views.SLICES
                if not view in [dv.views.SLICES, dv.views.GALLERY]:
                    raise Exception("Invalid display mode for Stack")

                viewWidget = ViewsFactory.createVolumeView(
                    path, view=view,
                    selection=dv.views.PagingView.SINGLE_SELECTION,
                    **kwargs)
                    #if view == dv.views.SLICES:
                    # kwargs['toolBar'] = False
                    # kwargs['axis'] = False
                    # else:
                    #     kwargs['view'] = dv.views.GALLERY
                    #     view = ViewsFactory.createDataView(
                    #         path, **kwargs)
            else:
                print("non-vol stack")
                if x > dv.views.MOVIE_SIZE:
                    defaultView = dv.views.SLICES
                else:
                    defaultView = dv.views.GALLERY

                kwargs['view'] = view = view or defaultView

                if view == dv.views.SLICES:
                    viewWidget = ViewsFactory.createSlicesView(path, **kwargs)
                else:
                    viewWidget = ViewsFactory.createDataView(path, **kwargs)
    elif emv.utils.EmPath.isStandardImage(path):
        viewWidget = ViewsFactory.createImageView(path, **kwargs)

    if viewWidget is None:
        raise Exception("Can't create a view for this file.")

    fitViewSize(viewWidget, d)
    viewWidget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()