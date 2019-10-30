#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestImageListView(dv.tests.TestView):
    __title = "ImageListView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "import", "classify2d", "extra",
                         "relion_it015_classes.mrcs")
        ]

    def createView(self):
        return dv.views.ImageListView(
            emv.models.ModelsFactory.createTableModel(self.getDataPaths()[0]))


if __name__ == '__main__':
    TestImageListView().runApp()
