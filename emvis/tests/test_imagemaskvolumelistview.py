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
        maskColor = '#334BBC23'
        slicesKwargs = {dv.models.AXIS_X: {'imageViewKwargs': {'mask': mask,
                                                     'maskColor': maskColor
                                                     }
                                 },
                        dv.models.AXIS_Y: {'imageViewKwargs': {'mask': mask,
                                                     'maskColor': maskColor
                                                     }
                                 },
                        dv.models.AXIS_Z: {'imageViewKwargs': {'mask': mask,
                                                     'maskColor': maskColor
                                                     }
                                 }
                        }
        return dv.views.VolumeListView(
            None, emv.ModelsFactory.createListModel(self.getDataPaths()),
            slicesKwargs=slicesKwargs, slicesMode=dv.models.AXIS_XYZ)


if __name__ == '__main__':
    TestImageMaskVolumeListView().runApp()
