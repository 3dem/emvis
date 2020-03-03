
import os
from itertools import chain
    

import emcore as emc
import datavis as dv
import emvis as emv


class RelionPickerModel(emv.models.EmPickerModel):

    def __init__(self, projectFolder, pickingPath, micsStar=None, **kwargs):
        emv.models.EmPickerModel.__init__(self, **kwargs)

        self.isAuto = 'AutoPick' in pickingPath
        pickLabel = 'autopick' if self.isAuto else 'manualpick'
        self._runName = os.path.basename(pickingPath)

        # For some reason Relion store input micrographs star filename
        # in the following star file, that is not a STAR file
        suffixMicFn = os.path.join(pickingPath, 'coords_suffix_%s.star'
                                   % pickLabel)

        if not os.path.exists(suffixMicFn):
            raise Exception("Missing expected file: %s" % suffixMicFn)

        with open(suffixMicFn) as f:
            micsStar = f.readline().strip()

        micsStarPath = os.path.join(projectFolder, micsStar)

        if not os.path.exists(micsStarPath):
            raise Exception("Missing expected file %s" % micsStarPath)

        # FIXME: Read Table data from the constructor
        table = emc.Table()
        coordTable = emc.Table()
        print("Reading micrographs from: ", micsStarPath)
        table.read('micrographs', micsStarPath)

        self.setBoxSize(64)

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
                                                        "_%s.star" % pickLabel)
            micId = mic.getId()

            self.addMicrograph(mic)
            micCoordsFn = os.path.join(pickingPath, 'Movies', micBase)
            print("Coordinates: ", micCoordsFn, " exists: ", os.path.exists(micCoordsFn))
            if os.path.exists(micCoordsFn):
                coordTable.read(micCoordsFn)
                coords = [self.createCoordinate(
                    round(float(row['rlnCoordinateX'])),
                    round(float(row['rlnCoordinateY'])))
                    for row in coordTable]
                self.addCoordinates(micId, coords)

    def getRunName(self):
        return self._runName


class RelionPickerCmpModel(emv.models.EmPickerModel):
    def __init__(self, projectFolder, pickingPath1, pickingPath2,
                 micsStar=None, **kwargs):

        self._coordsToShow = 0  # all
        self._model1 = RelionPickerModel(projectFolder, pickingPath1, micsStar)
        self._model2 = RelionPickerModel(projectFolder, pickingPath2, micsStar)

        # Always keep as model 1 the largest one
        if self._model1.getRowsCount() < self._model2.getRowsCount():
            self._model1, self._model2 = self._model2, self._model1

        emv.models.EmPickerModel.__init__(self, **kwargs)

        self._labels['c1'] = self.Label(name="c1", color="#00ff00")
        self._labels['c2'] = self.Label(name="c2", color="#0000ff")

    def getParams(self):
        Param = dv.models.Param
        coords = Param('coords', dv.models.PARAM_TYPE_ENUM,
                       choices=['From both runs',
                                'Run: %s' % self._model1.getRunName(),
                                'Run: %s' % self._model2.getRunName()],
                       display=dv.models.PARAM_DISPLAY_VLIST,
                       label='Coordinates: ')

        return dv.models.Form([coords])

    def changeParam(self, micId, paramName, paramValue, getValuesFunc):
        # Most cases here will modify the current coordinates
        r = self.Result(currentCoordsChanged=True, tableModelChanged=True)
        print("value: ", paramValue, "type", type(paramValue))
        self._coordsToShow = paramValue
        return r

    def iterCoordinates(self, micId):
        # Re-implement this to show only these above the threshold
        # or with a different color (label)
        if self._coordsToShow == 0:
            showList = [(self._model1, 'c1'), (self._model2, 'c2')]
        elif self._coordsToShow == 1:
            showList = [(self._model1, 'c1')]
        elif self._coordsToShow == 2:
            showList = [(self._model2, 'c2')]
        else:
            raise Exception('Not supported ')

        for model, label in showList:
            mic = model.getMicrograph(micId)
            if mic is not None:
                for c in mic:
                    c.set(label=label)
                    yield c

    def getRowsCount(self):
        return self._model1.getRowsCount()

    def getData(self, micId):
        return self._model1.getData(micId)

    def getImageInfo(self, micId):
        return self._model1.getImageInfo(micId)

    def getMicrographByIndex(self, micIndex):
        """ Return the micrograph at this given index. """
        return self._model1._micList[micIndex]

    def getValue(self, row, col):
        mic = self.getMicrographByIndex(row)
        micId = mic.getId()

        if col == 0:  # Name
            return os.path.basename(mic.getPath())
        elif col == 1:  # 'A' coordinates
            mic1 = self._model1.getMicrograph(micId)
            return 0 if mic1 is None else len(mic1)
        elif col == 2:  # 'B' coordinates
            mic2 = self._model2.getMicrograph(micId)
            return 0 if mic2 is None else len(mic2)
        elif col == 3:  # 'AnB' coordinates
            return 0 #return dv.models.PickerCmpModel.getValue(self, row, col)
        else:
            raise Exception("Invalid column value '%s'" % col)

    def getColumns(self):
        return [
            dv.models.ColumnConfig('Micrograph',
                                   dataType=dv.models.TYPE_STRING),
            dv.models.ColumnConfig(self._model1.getRunName(),
                                   dataType=dv.models.TYPE_INT),
            dv.models.ColumnConfig(self._model2.getRunName(),
                                   dataType=dv.models.TYPE_INT),
            dv.models.ColumnConfig('AnB', dataType=dv.models.TYPE_INT, visible=False),
        ]