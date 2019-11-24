
import os

import emcore as emc
import datavis as dv

from ..utils import ImageManager


class EmPickerModel(dv.models.PickerModel):
    """ Em picker data model with direct access to ImageManager """

    def __init__(self, imageManager=None):
        dv.models.PickerModel.__init__(self)
        self._imageManager = imageManager or ImageManager()
        self._cache = {}

    def getData(self, micId):
        """
        Return the micrograph image data
        :param micId: (int) The micrograph id
        :return: The micrograph image data
        """
        print("Loading data...micId=%s" % micId)
        if micId in self._cache:
            data = self._cache[micId]
        else:
            print("  Computing....")
            mic = self.getMicrograph(micId)
            from scipy.ndimage import gaussian_filter
            import numpy as np
            data = self._imageManager.getData(mic.getPath())
            gaussian_filter(data, sigma=2, output=data)
            mean = np.mean(data)
            std = 5 * np.std(data)
            print("mean: %s, std: %s" % (mean, std))
            np.clip(data, mean - std, mean + std, out=data)
            self._cache[micId] = data

        return data

    def getImageInfo(self, micId):
        """
        Return some specified info from the given image path.
        dim : Image dimensions
        ext : File extension
        data_type: Image data type

        :param micId:  (int) The micrograph Id
        :return: dict
        """
        mic = self.getMicrograph(micId)
        return self._imageManager.getInfo(mic.getPath())


class RelionPickerModel(EmPickerModel):
    """ Em picker data model with direct access to ImageManager """

    def __init__(self, inputDir, imageManager=None):
        """
        Create a new instance of :class:`~RelionPickerModel`.

        Args:
            inputDir: Directory with the resulting picking dir
            imageManager: optional :class:`~emvis.utils.ImageManager` class to
                read micrographs from disk.
        """
        EmPickerModel.__init__(self, imageManager=imageManager)
        self._inputDir = inputDir
        self._scoreThreshold = 0.0
        self._useColor = False

        self._loadData()

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

    def _loadData(self):
        notes = self._input('note.txt')
        summary = self._input('summary.star')

        if not os.path.exists(notes):
            raise Exception("Expecting file '%s'" % notes)

        if not os.path.exists(summary):
            raise Exception("Expecting summary file '%s'" % summary)

        self._summaryTable = emc.Table()
        self._summaryTable.read(summary)

        projectRoot = None
        for row in self._summaryTable:
            micFn = str(row['rlnMicrographName'])
            if projectRoot is None:
                projectRoot = self._imageManager.findImagePrefix(
                    micFn, os.path.abspath(self._inputDir))

            mic = dv.models.Micrograph(path=os.path.join(projectRoot, micFn))
            self.addMicrograph(mic)

        self._loadedMics = set()

    def _coordFromRow(self, row):
        return dv.models.Coordinate(
            float(row['rlnCoordinateX']), float(row['rlnCoordinateY']),
            fom=float(row['rlnAutopickFigureOfMerit']))

    def _getCoordsList(self, micId):
        """ Return the coordinates list of a given micrograph. """
        mic = self.getMicrograph(micId)

        if micId not in self._loadedMics:
            baseFn = dv.utils.removeBaseExt(mic.getPath())
            coordsFn = self._input('Movies/%s_autopick.star' % baseFn)
            coordsTable = emc.Table()
            coordsTable.read(coordsFn)
            mic._coordinates.extend(self._coordFromRow(row) for row in coordsTable)
            self._loadedMics.add(micId)

        return mic._coordinates

    def iterCoordinates(self, micId):
        # Re-implement this to show only these above the threshold
        # or with a different color (label)
        for coord in self._getCoordsList(micId):
            good = coord.fom > self._scoreThreshold
            coord.label = '0' if good else '1'
            if good or self._useColor:
                yield coord

    def getColumns(self):
        """ Return a Column list that will be used to display micrographs. """
        return [
            dv.models.ColumnConfig('Micrograph', dataType=dv.models.TYPE_STRING,
                                   editable=False),
            dv.models.ColumnConfig('FOM', dataType=dv.models.TYPE_FLOAT,
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
        elif col == 1:
            return self._summaryTable[row]['rlnAutopickFigureOfMerit']
        elif col == 2:  # Coordinates
            # Use real coordinates number for already loaded micrographs
            # Otherwise the number read from the summary table
            if mic.getId() in self._loadedMics:
                return len(mic)
            else:
                return self._summaryTable[row]['rlnGroupNrParticles']
        elif col == 3:  # Id
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
                         label='Color coordinates by FOM?')

        return dv.models.Form([
            [scoreThreshold, useColor]
        ])

    def changeParam(self, micId, paramName, paramValue, getValuesFunc):
        # Most cases here will modify the current coordinates
        r = self.Result(currentCoordsChanged=True, tableModelChanged=True)

        if paramName == 'scoreThreshold':
            self._scoreThreshold = getValuesFunc()['scoreThreshold']
        elif paramName == 'useColor':
            self._useColor = getValuesFunc()['useColor']
        else:
            r = self.Result()  # No modification

        return r