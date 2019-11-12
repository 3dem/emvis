#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestItemsView(dv.tests.TestView):
    __title = "ItemsView Example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "import", "refine3d", "extra",
                         "relion_it025_data.star")
        ]

    def createView(self):
        return dv.views.ItemsView(
            model=emv.models.ModelsFactory.createTableModel(self._path),
            selectionMode=dv.views.ItemsView.MULTI_SELECTION)


if __name__ == '__main__':
    TestItemsView().runApp()
