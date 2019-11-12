#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

import datavis as dv
import emvis as emv


class TestImageMaskVolumeListView(dv.tests.TestView):
    __title = "ImageMaskVolumeListView example"

    def getDataPaths(self):
        return [
            self.getPath("xmipp_programs", "gold",
                         "xmipp_ctf_correct_amplitude3d",
                         "wiener_ctffiltered_group000001.vol"),
            self.getPath("xmipp_programs", "gold",
                         "xmipp_ctf_correct_wiener3d_01",
                         "wiener_deconvolved.vol"),
            self.getPath("xmipp_programs", "gold",
                         "xmipp_ctf_correct_amplitude3d",
                         "wiener_deconvolved.vol")
        ]

    def createView(self):
        # creating the image mask
        mask = np.zeros(shape=(64, 64), dtype=np.int8)
        for i in range(20, 44):
            for j in range(20, 44):
                mask[i][j] = 1

        maskParams = {
            'type': dv.views.DATA,
            'color': '#334BBC23',
            'data': mask,
        }
        slicesKwargs = {
            dv.models.AXIS_X: {
                'imageViewKwargs': {'maskParams': maskParams}},
            dv.models.AXIS_Y: {
                'imageViewKwargs': {'maskParams': maskParams}},
            dv.models.AXIS_Z: {
                'imageViewKwargs': {'maskParams': maskParams}}
        }
        return dv.views.VolumeListView(
            emv.models.ModelsFactory.createListModel(self.getDataPaths()),
            slicesKwargs=slicesKwargs, slicesMode=dv.models.AXIS_XYZ)


if __name__ == '__main__':
    TestImageMaskVolumeListView().runApp()
