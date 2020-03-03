#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

import datavis as dv
import emcore as emc
import emvis as emv

from .models import RelionPickerModel, RelionPickerCmpModel


class TestPickerView(dv.tests.TestView):
    __title = "Relion picking viewer"

    def __init__(self, pickModel):
        self._model = pickModel

    def getDataPaths(self):
        return [
            self.getPath("tmv_helix", "micrographs", "TMV_Krios_Falcon")
        ]

    def createView(self):
        kwargs = dict()
        kwargs['selectionMode'] = dv.views.PagingView.SINGLE_SELECTION
        kwargs['boxSize'] = 300
        kwargs['pickerMode'] = dv.views.DEFAULT_MODE
        kwargs['shape'] = dv.views.SHAPE_CIRCLE
        kwargs['removeRois'] = True
        kwargs['roiAspectLocked'] = True
        kwargs['roiCentered'] = True

        return dv.views.PickerView(self._model, **kwargs)


def main(argv=None):
    argv = argv or sys.argv[1:]
    n = len(argv)

    defaultMics = 'Select/job005/micrographs_selected.star'
    defaultMovs = 'AutoPick/LoG_based/Movies'

    if n < 1 or n > 2:
        raise Exception(
            "Expecting 1 or 2 arguments: PICKING_FOLDER [PICKING_FOLDER2]\n\n"
            "Where: \n"
            "   PICKING_FOLDER: Picking folder, including project path. \n"
            "   PICKING_FOLDER2: Another picking folder, to compare results. \n"
            "Example: \n"
            "   em-relion-viewer ~/work/data/relion31_tutorial_precalculated_results/ "
            "%s %s " % (defaultMics, defaultMovs))

    pickingFolder = os.path.abspath(argv[0])
    # We expect project folder to be two levels up from picking folder
    projectFolder = os.path.dirname(os.path.dirname(pickingFolder))

    if n > 1:
        pickModel = RelionPickerCmpModel(projectFolder, pickingFolder, argv[1])
    else:
        pickModel = RelionPickerModel(projectFolder, pickingFolder)

    TestPickerView(pickModel).runApp()
