# -*- coding: utf-8 -*-

import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg

import pyqtgraph as pg


class ImageBox(qtw.QWidget):
    """ Box for QImage display. It allows internal image scaling/panning
    by mouse drag."""

    def __init__(self, parent=None):
        """
        Initialise an ViewBox instance
        Args:
             parent: The parent widget
        """
        qtw.QWidget.__init__(self, parent=parent)

        layout = qtw.QVBoxLayout(self)
        self._pixmapItem = qtw.QGraphicsPixmapItem()
        self._pgViewBox = pg.ViewBox()
        self._pgViewBox.addItem(self._pixmapItem)
        self._pgImageView = pg.ImageView(self, view=self._pgViewBox)
        self._pgImageView.ui.menuBtn.setVisible(False)
        self._pgImageView.ui.histogram.setVisible(False)
        self._pgImageView.ui.roiBtn.setVisible(False)
        self._pgViewBox.setMenuEnabled(False)

        layout.addWidget(self._pgImageView)

    def setImage(self, qimage):
        """
        Set a new image that will be displayed in the ImageBox.

        Args:
            qimage: QImage instance
        """
        self._pixmapItem.setPixmap(qtg.QPixmap.fromImage(qimage))

    def fitToSize(self):
        """ The image is fit to window """
        self._pgViewBox.autoRange()
