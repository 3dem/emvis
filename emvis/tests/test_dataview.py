#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestDataView(dv.tests.TestView):
    __title = "DataView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "import", "refine3d", "extra",
                         "relion_it025_data.star")
        ]

    def createView(self):
        print("File: %s" % self._path)
        return dv.views.DataView(
            model=emv.models.ModelsFactory.createTableModel(self._path))


if __name__ == '__main__':
    TestDataView().runApp()

