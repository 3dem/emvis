
import os

import emcore as emc
import datavis as dv
import emvis as emv


class RelionPickerModel(emv.models.EmPickerModel):

    def __init__(self, projectFolder, pickingPath, micsStar, **kwargs):
        emv.models.EmPickerModel.__init__(self, **kwargs)

        micsStarPath = os.path.join(projectFolder, micsStar)
        if not os.path.exists(micsStarPath):
            raise Exception("Missing expected file %s" % micsStarPath)

        self.isAuto = 'AutoPick' in pickingPath
        pickLabel = 'autopick' if self.isAuto else 'manualpick'

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


class RelionPickerCmpModel(dv.models.PickerCmpModel):
    def __init__(self, projectFolder, pickingPath1, pickingPath2, micsStar,
                 **kwargs):
        dv.models.PickerCmpModel.__init__(self, **kwargs)

        self._scoreThreshold = 0.5
        # Modify 'Auto' label to set red color
        self._labels['B'] = self.Label(name='B', color='#FF0000')
        self._showBelow = True

    def getParams(self):
        Param = dv.models.Param
        clear = Param('clear', 'button', label='Clear coordinates')
        pick = Param('pick', 'button', label='Pick Again')

        return dv.models.Form([pick, clear])

    def changeParam(self, micId, paramName, paramValue, getValuesFunc):
        # Most cases here will modify the current coordinates
        r = self.Result(currentCoordsChanged=True, tableModelChanged=True)

        if paramName == 'clear':
            self.clearMicrograph(micId)
        elif paramName == 'showBelow':
            self._showBelow = getValuesFunc()['showBelow']
        else:
            r = dv.models.PickerCmpModel.changeParam(self, micId, paramName,
                                                     paramValue, getValuesFunc)
        return r

    def iterCoordinates(self, micId):
        # Re-implement this to show only these above the threshold
        # or with a different color (label)
        for coord in self._getCoordsList(micId):
            good = coord.score > self._scoreThreshold
            if good or self._showBelow:
                yield coord

    def getRowsCount(self):
        return self._models[0].getRowsCount()

    def getData(self, micId):
        return self._models[0].getData(micId)

    def getImageInfo(self, micId):
        return self._models[0].getImageInfo(micId)

    def getValue(self, row, col):
        mic = self.getMicrographByIndex(row)
        micId = mic.getId()

        if col == 0:  # Name
            return mic.getPath()
        elif col == 1:  # 'A' coordinates
            return len(self._models[0].getMicrograph(micId))
        elif col == 2:  # 'B' coordinates
            return len(self._models[1].getMicrograph(micId))
        elif col == 3:  # 'AnB' coordinates
            return dv.models.PickerCmpModel.getValue(self, row, col)
        elif col == 4:  # Coordinates
            mic2 = self._models[1].getMicrographByIndex(row)
            return len(mic2) + len(mic) - self.__coordsBelow(micId)
        else:
            raise Exception("Invalid column value '%s'" % col)

    def getColumns(self):
        return [
            ColumnConfig('Micrograph', dataType=TYPE_STRING, editable=False),
            ColumnConfig('A', dataType=TYPE_INT, editable=False),
            ColumnConfig('B', dataType=TYPE_INT, editable=False),
            ColumnConfig('AnB', dataType=TYPE_INT, editable=False),
            ColumnConfig('Coords < Threshold', dataType=TYPE_INT,
                         editable=False)
        ]