#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestRoiMaskListView(dv.tests.TestView):
    __title = "RoiMaskListView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "micrographs", "006.mrc"),
            self.getPath("relion_tutorial", "micrographs", "008.mrc"),
            self.getPath("relion_tutorial", "micrographs", "016.mrc")
        ]

    def createView(self):
        maskParams = {
            'type': dv.views.CIRCLE_ROI,
            'color': '#154BBC23',
            'data': 500,
            'showHandles': True
        }
        return dv.views.ImageMaskListView(
            emv.models.ModelsFactory.createListModel(self.getDataPaths()),
            maskParams=maskParams)


if __name__ == '__main__':
    TestRoiMaskListView().runApp()
