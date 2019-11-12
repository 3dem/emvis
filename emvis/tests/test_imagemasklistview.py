#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestImageMaskListView(dv.tests.TestView):
    __title = "ImageMaskListView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "micrographs", "006.mrc"),
            self.getPath("relion_tutorial", "micrographs", "008.mrc"),
            self.getPath("relion_tutorial", "micrographs", "016.mrc")
        ]

    def createView(self):
        import numpy as np
        # creating the image mask
        mask = np.zeros(shape=(1024, 1024), dtype=np.int8)
        for i in range(300, 600):
            for j in range(300, 600):
                mask[i][j] = 1
        maskParams = {
            'type': dv.views.DATA,
            'color': '#334BBC23',
            'data': mask
        }
        return dv.views.ImageMaskListView(
            emv.models.ModelsFactory.createListModel(self.getDataPaths()),
            maskParams=maskParams)


if __name__ == '__main__':
    TestImageMaskListView().runApp()
