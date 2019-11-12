#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestColumnsView(dv.tests.TestView):
    __title = "ColumnsView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "import", "refine3d", "extra",
                         "relion_it025_data.star")
        ]

    def createView(self):
        return dv.views.ColumnsView(
            model=emv.models.ModelsFactory.createTableModel(self._path))


if __name__ == '__main__':
    TestColumnsView().runApp()
