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
            self.getPath("tmv_helix", "coords", "TMV_Krios_Falcon"),
            self.getPath("tmv_helix", "micrographs", "TMV_Krios_Falcon")
        ]

    def createView(self):
        kwargs = dict()
        kwargs['selectionMode'] = dv.views.PagingView.SINGLE_SELECTION
        kwargs['boxSize'] = 300
        kwargs['pickerMode'] = dv.views.FILAMENT_MODE
        kwargs['shape'] = dv.views.SHAPE_CIRCLE
        kwargs['removeRois'] = True
        kwargs['roiAspectLocked'] = True
        kwargs['roiCentered'] = True
        dataPaths = self.getDataPaths()
        kwargs['sources'] = self.__parseFiles(["%s*" % dataPaths[1],
                                               "%s*" % dataPaths[0]])
        files = [micPath for (micPath, _) in kwargs['sources'].values()]
        return emv.views.ViewsFactory.createPickerView(files, **kwargs)


if __name__ == '__main__':
    TestPickerView().runApp()
