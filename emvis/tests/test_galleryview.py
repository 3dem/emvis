#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestGalleryView(dv.tests.TestView):
    __title = "GalleryView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "import", "classify2d", "extra",
                         "relion_it015_classes.mrcs"),
            self.getPath("relion_tutorial", "import", "refine3d",
                         "input_particles.mrcs")
        ]

    def createView(self):
        return dv.views.GalleryView(
            model=emv.models.ModelsFactory.createTableModel(self._path))


if __name__ == '__main__':
    TestGalleryView().runApp()
