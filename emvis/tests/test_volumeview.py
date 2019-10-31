#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestVolumeView(dv.tests.TestView):
    __title = "Volume View example"

    def getDataPaths(self):
        return [
            self.getPath('resmap', 'betaGal.mrc'),
            self.getPath("xmipp_tutorial", "volumes",
                         "BPV_scale_filtered_windowed_110.vol")
        ]

    def createView(self):
        print("File: %s" % self._path)
        self._path = self.getDataPaths()[0]
        volModel = emv.models.ModelsFactory.createVolumeModel(self._path)
        return dv.views.VolumeView(volModel, toolBar=True,
                                   slicesMode=dv.models.AXIS_XYZ)


if __name__ == '__main__':
    TestVolumeView().runApp()

