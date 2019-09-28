#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestRoiMaskListView(dv.tests.TestView):
    __title = "ImageMaskListView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "micrographs", "006.mrc"),
            self.getPath("relion_tutorial", "micrographs", "008.mrc"),
            self.getPath("relion_tutorial", "micrographs", "016.mrc")
        ]

    def createView(self):
        return dv.views.ImageMaskListView(
            None, emv.ModelsFactory.createListModel(self.getDataPaths()),
            maskColor='#154BBC23', mask=dv.views.CIRCLE_ROI, maskSize=500)


if __name__ == '__main__':
    TestRoiMaskListView().runApp()
