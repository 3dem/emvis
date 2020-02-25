#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

import datavis as dv
import emcore as emc
import emvis as emv

from .models import RelionPickerModel


class TestPickerView(dv.tests.TestView):
    __title = "Relion picking viewer"

    def __init__(self, projectFolder, micStar, pickingFolder):
        self.projectFolder = projectFolder
        self.pickingFolder = pickingFolder
        self.micStar = micStar

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

        projectFolder = self.projectFolder  #'/Users/josem/work/data/relion30_tutorial_precalculated_results/'
        pickingFolder = self.pickingFolder  # 'AutoPick/LoG_based'
        pickingPath = os.path.join(projectFolder, pickingFolder)
        micsStar = self.micStar  # 'Select/job005/micrographs_selected.star'

        model = RelionPickerModel(projectFolder, pickingPath, micsStar)

        return dv.views.PickerView(model, **kwargs)


def main(argv=None):
    argv = argv or sys.argv[1:]
    n = len(argv)

    defaultMics = 'Select/job005/micrographs_selected.star'
    defaultMovs = 'AutoPick/LoG_based/Movies'

    if n < 1:
        raise Exception(
            "Expecting only one arguments: PICKING_FOLDER \n\n"
            "Where: \n"
            "   PICKING_FOLDER: Picking folder, including project path. \n"
            "Example: \n"
            "   python datavis/tests/test_picking_relion.py "
            "/Users/josem/work/data/relion30_tutorial_precalculated_results/ "
            "%s %s " % (defaultMics, defaultMovs))


        # For some reason Relion store input micrographs star filename
        # in the following star file, that is not a STAR file
        # suffixMicFn = os.path.join(pickingPath, 'coords_suffix_autopick.star')
        #
        # if not os.path.exists(suffixMicFn):
        #     raise Exception("Missing expected file: %s" % suffixMicFn)
        #
        # with open(suffixMicFn) as f:
        #     micsStar = f.readline().strip()

    pickingFolder = os.path.abspath(argv[0])

    # We expect project folder to be two levels up from picking folder
    projectFolder = os.path.dirname(os.path.dirname(pickingFolder))

    micStar = 'CtfFind/job003/micrographs_ctf.star'

    TestPickerView(projectFolder, micStar, pickingFolder).runApp()
