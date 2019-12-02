
import os
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QImage

import datavis as dv

from ._box import ImageBox
from ..utils import MOVIE_SIZE, getHighlighterClass, EmPath, ImageManager
from ..models import ModelsFactory

DATA_VIEW = 500
VOLUME_VIEW = 501
TEXT_VIEW = 502
IMAGE_VIEW = 503
IMAGE_BOX = 504


class EmBrowser(dv.widgets.FileBrowser):
    """ """
    def __init__(self, **kwargs):
        """
        Creates a EmBrowser instance
        Keyword Args:
            textLines: The first and last lines to be shown in text file preview
            :class:`FileBrowser <dv.widgets.FileBrowser>` params
        """
        self._lines = kwargs.get('textLines', 100)
        dv.widgets.FileBrowser.__init__(self, **kwargs)
        self._registerViews()
        self._dataView.sigCurrentTableChanged.connect(
            self.__onDataViewTableChanged)

        self.updateViewPanel()

    def __onDataViewTableChanged(self):
        model = self._dataView.getModel()
        if model is not None:
            info = dict()
            info["Type"] = "TABLE"
            dimTuple = (model.totalRowCount(), model.columnCount())
            info["Dimensions (Rows x Columns)"] = "%d x %d" % dimTuple
            self.__showInfo(info)

    def __showMsgBox(self, text, icon=None, details=None):
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

    def __showInfo(self, info):
        """
        Show the information in the corresponding widget.
        info is a dict
        """
        self.__clearInfoWidget()
        if isinstance(info, dict):
            for key in info.keys():
                self._infoWidget.addItem("%s: %s" % (str(key).capitalize(),
                                                     str(info[key])))

    def __clearInfoWidget(self):
        """ Clear the info widget """
        self._infoWidget.clear()

    def __showVolumeSlice(self):
        """Show the Volume Slicer component"""
        self._stackLayout.setCurrentWidget(self._volumeView)

    def __showDataView(self):
        """Show the Table View component"""
        self._stackLayout.setCurrentWidget(self._dataView)

    def __showImageView(self):
        """ Show the dv.views.ImageView component """
        self._stackLayout.setCurrentWidget(self._imageView)

    def __showSlicesView(self):
        """ Show the dv.views.SlicesView component """
        self._stackLayout.setCurrentWidget(self._slicesView)

    def __showTextView(self):
        """ Show the TextView component """
        self._stackLayout.setCurrentWidget(self._textView)

    def __showBoxWidget(self):
        """ Show the ImageBox component """
        self._stackLayout.setCurrentWidget(self._box)

    def __showEmptyWidget(self):
        """ Show an empty widget"""
        self._stackLayout.setCurrentWidget(self._emptyWidget)

    def __showStandardImage(self, path):
        """ Show a table file from the given path

        Returns:
            A dict with file info
        """
        image = QImage(path)
        self._box.setImage(image)
        self.__showBoxWidget()
        self._box.fitToSize()

        return {
            'dim': (image.width(), image.height()),
            'ext': EmPath.getExt(path),
            'Type': 'STANDARD-IMAGE'
        }

    def __showTableFile(self, path):
        """ Show a table file from the given path

        Returns:
            A dict with file info
        """
        model = ModelsFactory.createTableModel(path)
        self._dataView.setModel(model)
        if not model.getRowsCount() == 1:
            self._dataView.setView(dv.views.COLUMNS)
        else:
            self._dataView.setView(dv.views.ITEMS)

        self.__showDataView()
        # Show the Table dimensions
        info = {
            'Type': 'TABLE',
            'Dimensions (Rows x Columns)': "%d x %d" % (model.getRowsCount(),
                                                        model.getColumnsCount())
        }

        return info

    def __showDataFile(self, path):
        """ Show a data file from the given path

        Returns:
            A dict with file info
        """
        info = ImageManager().getInfo(path)
        d = info['dim']
        if d.n == 1:  # Single image or volume
            if d.z == 1:  # Single image
                model = ModelsFactory.createImageModel(path)
                self._imageView.setModel(model)
                self._imageView.setImageInfo(
                    path=path, format=info['ext'],
                    data_type=str(info['data_type']))
                info['Type'] = 'SINGLE-IMAGE'
                self.__showImageView()
            else:  # Volume
                # The image has a volume. The data is a numpy 3D array.
                # In this case, display the Top, Front and the Right
                # View planes.
                info['type'] = "VOLUME"
                model = ModelsFactory.createVolumeModel(path)
                self._volumeView.setModel(model)
                self.__showVolumeSlice()
        else:
            # Image stack
            if d.z > 1:  # Volume stack
                raise Exception("Volume stack is not supported")
            elif d.x <= MOVIE_SIZE:
                info['type'] = 'IMAGES STACK'
                model = ModelsFactory.createTableModel(path)
                self._dataView.setModel(model)
                self._dataView.setView(dv.views.GALLERY)
                self.__showDataView()
            else:
                info['type'] = 'MOVIE'
                model = ModelsFactory.createStackModel(path)
                self._slicesView.setModel(model)
                self.__showSlicesView()
        # TODO Show the image type
        return info

    def __showTextFile(self, path):
        """ Show a text file from the given path

        Returns:
            A dict with file info
        """
        extType = EmPath.getExtType(path)
        cl = getHighlighterClass(extType)
        h = cl(None) if cl is not None else None
        self._textView.setHighlighter(h)
        self._textView.clear()
        with open(path) as f:
            self._textView.readText(f, self._lines, self._lines, '...')

        self.__showTextView()
        return {'Type': 'TEXT FILE'}

    def _createViewPanel(self, **kwargs):
        viewPanel = qtw.QWidget(self)
        kwargs['parent'] = viewPanel
        self._dataView = dv.views.DataView(dv.models.EmptyTableModel(),
                                           **kwargs)
        self._dataView.showLeftToolBar(False)

        self._imageView = dv.views.ImageView(**kwargs)

        self._slicesView = dv.views.SlicesView(dv.models.EmptySlicesModel(),
                                               **kwargs)

        self._volumeView = dv.views.VolumeView(dv.models.EmptyVolumeModel(),
                                               **kwargs)

        self._textView = dv.widgets.TextView(viewPanel, True)
        self._textView.setReadOnly(True)

        self._box = ImageBox(parent=viewPanel)

        self._emptyWidget = qtw.QWidget(parent=viewPanel)

        layout = qtw.QHBoxLayout(viewPanel)
        self._stackLayout = qtw.QStackedLayout(layout)
        self._stackLayout.addWidget(self._volumeView)
        self._stackLayout.addWidget(self._dataView)
        self._stackLayout.addWidget(self._imageView)
        self._stackLayout.addWidget(self._slicesView)
        self._stackLayout.addWidget(self._textView)
        self._stackLayout.addWidget(self._emptyWidget)
        self._stackLayout.addWidget(self._box)

        return viewPanel

    def _createInfoPanel(self, **kwargs):
        self._infoWidget = qtw.QListWidget(self)
        return self._infoWidget

    def _registerViews(self):
        """ Register the views associated with the supported file extensions.
        Inherited classes can reimplement this method to register other views
        and file extensions.
        """
        self.registerView('.star', DATA_VIEW, 'fa5s.table', True)
        self.registerView('.star', TEXT_VIEW, 'fa5s.file-alt', False)
        self.registerView('.xmd', DATA_VIEW, 'fa5s.table', True)
        self.registerView('.xmd', TEXT_VIEW, 'fa5s.file-alt', False)

    def _getShowFileFunction(self, path):
        """
        Return the function that should be used to display the file specified by
        path. Inherited classes can reimplement this method to provide other
        functions that display the data specified by path.

        Args:
            path:  (str) The file path

        Returns:
              A function with the following signature: funcName(path:str)
              The function must return a dict with file information
        """

        view = self.getCurrentView(EmPath.getExt(path))

        if view is None:
            return None

        if view == DATA_VIEW:
            func = self.__showTableFile
        elif view in [IMAGE_VIEW, VOLUME_VIEW]:
            func = self.__showDataFile
        elif view == IMAGE_BOX:
            func = self.__showStandardImage
        elif view == TEXT_VIEW:
            func = self.__showTextFile
        else:
            func = None

        return func

    def _showFile(self, path):
        """
        This method show the content of the file specified by the given path.
        Depending on the file type, the corresponding view will be used.

        Args:
            path: (str) The image path
        """
        try:
            info = {'Type': 'UNKNOWN'}

            func = self._getShowFileFunction(path)

            if func is not None:
                info = func(path)
            #  Show the default view
            elif EmPath.isTable(path):
                info = self.__showTableFile(path)
            elif EmPath.isStandardImage(path):
                info = self.__showStandardImage(path)
            elif EmPath.isData(path):
                info = self.__showDataFile(path)
            elif EmPath.isTextFile(path):
                info = self.__showTextFile(path)
            else:
                self.__showEmptyWidget()
                info.clear()

            self.__showInfo(info)
        except Exception as ex:
            self.__showMsgBox("Error opening the file",
                              qtw.QMessageBox.Critical,
                              str(ex))
            self.__showEmptyWidget()
            self.__clearInfoWidget()
        except RuntimeError as ex:
            self.__showMsgBox("Error opening the file",
                              qtw.QMessageBox.Critical,
                              str(ex))
            self.__showEmptyWidget()
            self.__clearInfoWidget()

    def updateViewPanel(self):
        """
        Update the information of the view panel.
        """
        index = self._treeModelView.currentIndex()
        model = self._treeModelView.model()
        path = model.filePath(index)
        self._showFile(path)
