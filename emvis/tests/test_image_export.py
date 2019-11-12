#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import PyQt5.QtWidgets as qtw
import pyqtgraph as pg

from datavis.views import ImageView

import datavis as dv
import emvis as emv


class TestImageView(dv.tests.TestView):
    __title = "ImageView explort example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "micrographs", "068.mrc")
        ]

    def createView(self):
        imageView = ImageView(parent=None, border_color='#FFAA33', axis=True,
                              toolBar=False, maskColor='#224BBC23',
                              mask=dv.views.CIRCLE_ROI, maskSize=500)
        imgModel = emv.models.ModelsFactory.createImageModel(self._path)
        imageView.setModel(imgModel)
        dim_x, dim_y = imgModel.getDim()
        index, path = imgModel.getLocation()
        desc = ("<html><head/><body><p>"
                "<span style=\" color:#0055ff;\">Dimensions: </span>"
                "<span style=\" color:#000000;\">(%d,%d)</span></p>"
                "<p><strong>Path: </strong>%s</p></body>" 
                "</html>" % (dim_x, dim_y, path))
        imageView.setImageInfo(text=desc)
        imageView.getViewBox().addItem(pg.CircleROI((-40, -40), 200))
        view = qtw.QWidget()
        layout = qtw.QVBoxLayout(view)
        toolbar = qtw.QToolBar(view)
        layout.addWidget(toolbar)
        toolbar.addAction(
            dv.widgets.TriggerAction(toolbar, actionName='SaveAll',
                                     tooltip='Export all view',
                                     faIconName='fa.save',
                                     slot=self.__exportView))
        toolbar.addSeparator()
        toolbar.addAction(
            dv.widgets.TriggerAction(toolbar, actionName='SaveImage',
                                     tooltip='Export image and content',
                                     faIconName='fa5s.save',
                                     slot=self.__export))
        layout.addWidget(imageView)
        self._imageView = imageView
        return view

    def __exportView(self):
        self._imageView.export(None)

    def __export(self):
        self._imageView.export(None, exportView=False)


if __name__ == '__main__':
    TestImageView().runApp()
