
import os
from random import randint

import datavis as dv
import emvis.models as em_models

class TestPickerModel(em_models.EmPickerModel):
    """ Em picker data model with direct access to ImageManager """

    def __init__(self, inputDir, coordDir, imageManager=None):
        """
        Create a new instance of :class:`~TestPickerModel`.

        Args:
            inputDir: Directory with the resulting picking dir
            imageManager: optional :class:`~emvis.utils.ImageManager` class to
                read micrographs from disk.
        """
        em_models.EmPickerModel.__init__(self, imageManager=imageManager)
        self._inputDir = inputDir
        self._coordDir = coordDir
        self._scoreThreshold = 0.0
        self._useColor = False

        self._loadData()

    def _parseEmPickCoordinates(self, path):
        """ Parse (x, y) coordinates from a text file assuming
         that the first two columns on each line are x and y.
         Other specifications can be:
          - x  y  label
          - x1  y1  width  height
          - x1  y1  width  height label
        """
        with open(path) as f:
            Coord = dv.models.Coordinate
            index = 0
            for line in f:
                li = line.strip()
                index += 1
                t = randint(0, 10) #  FIXME[hv] use random threshold
                if li:
                    parts = li.strip().split()
                    size = len(parts)
                    if size == 2 or size == 4:  # (x, y) or (x1,y1,width,height)
                        yield Coord(int(parts[0]), int(parts[1]), "",
                                    threshold=t)
                    elif size == 3:  # (x, y, label)
                        yield Coord(int(parts[0]), int(parts[1]), str(parts[2]),
                                    threshold=t)
                    elif size == 5:  # (x1, y1, width, height, label):
                        yield Coord(int(parts[0]), int(parts[1]), str(parts[4]),
                                    threshold=t)
                    else:
                        raise Exception(
                            "Unsupported coordinate specification:\n"
                            "path: %s" % path % "line: %d" % index)

    def _initLabels(self):
        """ Initialize the labels for this PickerModel. """
        colors = [
            "#1EFF00",
            "#DD0014"
        ]
        for i, c in enumerate(colors):
            name = str(i)
            self._labels[name] = self.Label(name=name, color=c)
        self._labels['D'] = self._labels['0']

    def _input(self, filename):
        return os.path.join(self._inputDir, filename)

    def _coord(self, filename):
        return os.path.join(self._coordDir, filename)

    def _loadData(self):
        self._loadedMics = set()

        if not os.path.exists(self._inputDir):
            raise Exception("Expecting directory '%s'" % self._inputDir)

        if not os.path.exists(self._coordDir):
            raise Exception("Expecting directory '%s'" % self._coordDir)

        micId = 0
        for micName in os.listdir(self._inputDir):
            micId += 1
            mic = dv.models.Micrograph(micId=micId, path=self._input(micName))
            self.addMicrograph(mic)
            self.beginReadCoordinates(micId)

    def readCoordinates(self, micId):
        if not micId in self._loadedMics:
            self._loadedMics.add(micId)
            mic = self.getMicrograph(micId)
            micName = os.path.split(mic.getPath())[-1]
            coordPath = self._coord(os.path.splitext(micName)[0] + '.box')

            if os.path.exists(coordPath):
                return self._parseEmPickCoordinates(coordPath)
        return []

    def createCoordinate(self, x, y, label, **kwargs):
        """
        Return a Coordinate object. This is the preferred way to create
        Coordinates objects, ensuring that the object contains all
        the additional properties related to the model.
        Subclasses should implement this method
        """
        return dv.models.Coordinate(x, y, 'M', threshold=1, **kwargs)

    def iterCoordinates(self, micId):
        # Re-implement this to show only these above the threshold
        # or with a different color (label)
        for coord in self._getCoordsList(micId):
            good = coord.threshold > self._scoreThreshold
            coord.label = '0' if good else '1'
            if good or self._useColor:
                yield coord

    def getColumns(self):
        """ Return a Column list that will be used to display micrographs. """
        return [
            dv.models.ColumnConfig('Micrograph', dataType=dv.models.TYPE_STRING,
                                   editable=False),
            dv.models.ColumnConfig('Coordinates', dataType=dv.models.TYPE_INT,
                                   editable=False),
            dv.models.ColumnConfig('Id', dataType=dv.models.TYPE_INT,
                                   editable=False, visible=False),
        ]

    def getValue(self, row, col):
        """ Return the value in this (row, column) from the micrographs table.
        """
        mic = self.getMicrographByIndex(row)

        if col == 0:  # Name
            return os.path.basename(mic.getPath())
        elif col == 1:  # Coordinates
            # Use real coordinates number for already loaded micrographs
            return len(mic)
        elif col == 2:  # Id
            return mic.getId()
        else:
            raise Exception("Invalid column value '%s'" % col)

    def getParams(self):
        Param = dv.models.Param
        scoreThreshold = Param('scoreThreshold', 'int', value=5,
                               display='slider', range=(0, 10),
                               label='Score threshold',
                               help='Display coordinates with score above '
                                    'this value.')

        useColor = Param('useColor', 'bool', value=self._useColor,
                         label='Color coordinates \nwith score above?')

        return dv.models.Form([
            [scoreThreshold, useColor]
        ])

    def onParamChanged(self, micId, paramName, paramValues):
        # Most cases here will modify the current coordinates
        d = {'micId': micId,
             'currentCoordsChanged': True,
             'tableModelChanged': True}
        n = True

        if paramName == 'scoreThreshold':
            self._scoreThreshold = paramValues['scoreThreshold']
        elif paramName == 'useColor':
            self._useColor = paramValues['useColor']
        else:
            n = False  # No modification

        if n:
            self.notifyEvent(type=dv.models.PICK_EVT_DATA_CHANGED, info=d)


class TestPickFilModel(TestPickerModel):

    def _parseEmPickCoordinates(self, path):
        """ Parse (x1, y1, x2, y2) coordinates from a text file assuming
         that the first four columns on each line are x1, y1, x2, y2.
         Other specifications can be:
          - x1  y1  x2  y2 label
        """
        with open(path) as f:
            Coord = dv.models.Coordinate
            index = 0
            for line in f:
                li = line.strip()
                index += 1
                t = randint(0, 10) #  FIXME[hv] use random threshold
                if li:
                    parts = li.strip().split()
                    size = len(parts)
                    if size == 4:  # (x1, y1, x2, y2)
                        yield Coord(int(parts[0]), int(parts[1]), "",
                                    threshold=t, x2=parts[2], y2=parts[3])
                    elif size == 5:  # (x1, y1, x2, y2, label):
                        yield Coord(int(parts[0]), int(parts[1]), str(parts[4]),
                                    threshold=t, x2=parts[2], y2=parts[3])
                    else:
                        raise Exception(
                            "Unsupported coordinate specification:\n"
                            "path: %s" % path % "line: %d" % index)
