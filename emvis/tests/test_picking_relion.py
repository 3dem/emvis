#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

import datavis as dv
import emcore as emc
import emvis as emv


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

        # For some reason Relion store input micrographs star filename
        # in the following star file, that is not a STAR file
        # suffixMicFn = os.path.join(pickingPath, 'coords_suffix_autopick.star')
        #
        # if not os.path.exists(suffixMicFn):
        #     raise Exception("Missing expected file: %s" % suffixMicFn)
        #
        # with open(suffixMicFn) as f:
        #     micsStar = f.readline().strip()

        micsStarPath = os.path.join(projectFolder, micsStar)
        if not os.path.exists(micsStarPath):
            raise Exception("Missing expected file %s" % micsStarPath)

        print("Relion Project: %s" % projectFolder)
        print("   Micrographs: %s" % micsStar)
        print("       Picking: %s" % pickingFolder)

        # FIXME: Read Table data from the constructor
        table = emc.Table()
        coordTable = emc.Table()
        table.read(micsStarPath)

        model = emv.models.EmPickerModel()
        model.setBoxSize(64)

        def _getMicPath(micName):
            micPath = os.path.join(projectFolder, micName)
            if os.path.exists(micPath):
                return micPath
            micPath = os.path.join(pickingPath, micName)
            if os.path.exists(micPath):
                return micPath

            raise Exception("Can not find root path for mic: %s" % micName)

        for i, row in enumerate(table):
            micPath = _getMicPath(str(row['rlnMicrographName']))
            mic = dv.models.Micrograph(i + 1, micPath)
            micBase = os.path.basename(micPath).replace(".mrc",
                                                        "_autopick.star")
            micCoordsFn = os.path.join(pickingPath, micBase)
            model.addMicrograph(mic)
            if os.path.exists(micCoordsFn):
                coordTable.read(micCoordsFn)
                for coordRow in coordTable:
                    coord = model.createCoordinate(
                        round(float(coordRow['rlnCoordinateX'])),
                        round(float(coordRow['rlnCoordinateY'])), '')
                    model.addCoordinates(mic.getId(), [coord])

        return dv.views.PickerView(model, **kwargs)


if __name__ == '__main__':
    n = len(sys.argv)

    defaultMics = 'Select/job005/micrographs_selected.star'
    defaultMovs = 'AutoPick/LoG_based/Movies'

    if n < 2:
        raise Exception(
            "Expecting only two arguments: PROJECT_PATH [MICROGRAPHS_STAR COORDINATES_PATH] \n\n"
            "Where: \n"
            "   PROJECT_PATH: Project path, root of all other inputs are found. \n"
            "   MICROGRAPHS_STAR: Star file with micrographs. \n"
            "   COORDINATES_PATH: Where the coordinates star files are. \n"
            "Example: \n"
            "   python datavis/tests/test_picking_relion.py "
            "/Users/josem/work/data/relion30_tutorial_precalculated_results/ "
            "%s %s " % (defaultMics, defaultMovs))

    projectFolder = sys.argv[1]
    micStar = sys.argv[2] if n > 2 else defaultMics
    pickingFolder = sys.argv[3] if n > 3 else defaultMovs

    TestPickerView(projectFolder, micStar, pickingFolder).runApp()
