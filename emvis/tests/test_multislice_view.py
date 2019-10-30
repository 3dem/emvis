#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestMultiSliceView(dv.tests.TestView):
    __title = "MultiSliceView example"

    def getDataPaths(self):
        return [
            self.getPath('resmap', 'betaGal.mrc'),
            self.getPath("xmipp_tutorial", "volumes",
                         "BPV_scale_filtered_windowed_110.vol")
        ]

    def createView(self):
        print("File: %s" % self._path)
        volModel = emv.models.ModelsFactory.createVolumeModel(self._path)
        msv = dv.views.MultiSliceView(
            None, {axis: {'model': volModel.getSlicesModel(axis),
                          'normalize': True}
                   for axis in [dv.models.AXIS_X, dv.models.AXIS_Y,
                                dv.models.AXIS_Z]})
        return msv


if __name__ == '__main__':
    TestMultiSliceView().runApp()

