#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from glob import glob

import datavis as dv
import emvis as emv


class TestPickerView(dv.tests.TestView):
    __title = "PickerView Example"

    def __parseFiles(self, values):
        """
        Try to matching a path pattern for micrographs
        and another for coordinates.

        Return a list of tuples [mic_path, pick_path].
        """
        length = len(values)
        result = dict()
        if length > 2:
            raise ValueError("Invalid number of arguments. Only 2 "
                             "arguments are supported.")

        if length > 0:
            mics = glob(values[0])
            for i in mics:
                basename = os.path.splitext(os.path.basename(i))[0]
                result[basename] = (i, None)

        if length > 1:
            coords = glob(values[1])
            for i in coords:
                basename = os.path.splitext(os.path.basename(i))[0]
                t = result.get(basename)
                if t:
                    result[basename] = (t[0], i)

        return result

    def getDataPaths(self):
        return [
            self.getPath("tmv_helix", "micrographs"),
            self.getPath("tmv_helix", "coords")
        ]

    def createView(self):
        kwargs = dict()
        kwargs['selectionMode'] = dv.views.PagingView.SINGLE_SELECTION
        kwargs['boxSize'] = 170
        kwargs['pickerMode'] = dv.views.FILAMENT_MODE
        kwargs['shape'] = dv.views.SHAPE_CIRCLE
        kwargs['removeRois'] = True
        kwargs['roiAspectLocked'] = True
        kwargs['roiCentered'] = True
        dataPaths = self.getDataPaths()

        model = emv.tests.TestPickFilModel(dataPaths[0], dataPaths[1])
        v = dv.views.PickerView(model, **kwargs)
        return v

    def test_PickingViewFilament(self):
        print('test_PickingViewFilament')


if __name__ == '__main__':
    TestPickerView().runApp()
