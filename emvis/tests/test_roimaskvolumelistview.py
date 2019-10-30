#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import datavis as dv
import emvis as emv


class TestRoiMaskVolumeListView(dv.tests.TestView):
    __title = "RoiMaskVolumeListView example"

    def __init__(self, singleAxis):
        self._mode = dv.models.AXIS_Z if singleAxis else dv.models.AXIS_XYZ

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "volumes", "reference_rotated.vol"),
            self.getPath("xmipp_programs", "gold", "xmipp_ctf_correct_wiener3d",
                         "wiener_deconvolved.vol"),
            self.getPath("emx", "reconstRotandShiftFlip_Gold_output.vol"),
            self.getPath("emx", "reconstRotandShift_Gold_output.vol"),
            self.getPath("xmipp_programs", "gold", "xmipp_image_resize_02",
                         "volume_64.vol")
        ]

    def createView(self):
        maskParams = {
            'type': dv.views.CIRCLE_ROI,
            'color': '#154BBC23',
            'data': 20,
            'operation': None,
            'showHandles': True
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
            slicesKwargs=slicesKwargs, slicesMode=self._mode)


if __name__ == '__main__':
    if 'single' in sys.argv:
        singleAxis = True
    else:
        print("TIP: Use 'single' argument to show a single axis. ")
        singleAxis = False

    TestRoiMaskVolumeListView(singleAxis).runApp()