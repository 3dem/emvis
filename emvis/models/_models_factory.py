
import os
import numpy as np

import emcore as emc
import datavis.models as models

from ..utils import EmPath, EmType
from ._emtable_model import (EmTableModel, EmStackModel, EmVolumeModel,
                             EmListModel)
from ._empicker import EmPickerModel, RelionPickerModel


class ModelsFactory:
    """ Factory class to centralize the creation of Models using the
    underlying classes from em-core.
    """
    @classmethod
    def createImageModel(cls, path):
        """ Create an ImageModel reading path as an emc.Image. """
        image = emc.Image()
        loc = emc.ImageLocation(path)
        image.read(loc)
        return models.ImageModel(
            data=np.array(image, copy=False), location=(loc.index, loc.path))

    @classmethod
    def createTableModel(cls, path):
        """
        Creates an `TableModel <datavis.models.TableModel>` reading path as an
        emc.Table.

        Args:
            path: (str) The table path

        Returns:  `TableModel <datavis.models.TableModel>`
        """
        if EmPath.isTable(path):
            model = EmTableModel(path)
        elif EmPath.isStack(path):
            model = models.SlicesTableModel(EmStackModel(path), 'Index')
        elif EmPath.isVolume(path):
            slicesModel = EmVolumeModel(path).getSlicesModel(models.AXIS_Z)
            model = models.SlicesTableModel(slicesModel, 'Slice')
        else:
            raise Exception("Unknown file type: %s" % path)

        return model

    @classmethod
    def createPickerModel(cls, inputMics, inputCoords=None, **kwargs):
        """
        Guess the type of :class:`~datavis.models.PickerModel` (e.g Scipion, Relion, Xmipp, etc)
        that should be created based on the input directories.

        Args:
            inputMics:  main input path (folder or file), usually related to micrographs.
            inputCoords: input related to coordinates (either a file or folder path)

        Keyword Args:
            Extra parameters.

        Returns:
            A :class:`~datavis.models.PickerModel` subclass instance
        """
        model = None

        if os.path.exists(os.path.join(inputMics, 'note.txt')):
            model = RelionPickerModel(inputMics, inputCoords, **kwargs)

        #model = EmPickerModel()

        # if files and isinstance(files, list):
        #     for f in files:
        #         if not Path.exists(f):
        #             raise Exception("Input file '%s' does not exists. " % f)
        #         if not Path.isdir(f):
        #             model.addMicrograph(models.Micrograph(None, f))
        #         else:
        #             raise Exception('Directories are not supported for '
        #                             'picker model.')
        # elif sources is not None:
        #     for micPath, coordPath in sources.values():
        #         if parseCoordFunc and coordPath:
        #             coords = parseCoordFunc(coordPath)
        #         else:
        #             coords = None
        #
        #         mic = models.Micrograph(None, micPath)
        #         model.addMicrograph(mic)
        #         if coords:
        #             model.addCoordinates(mic.getId(), coords)
        #
        # model.setBoxSize(boxSize)
        return model

    @classmethod
    def createEmptyTableModel(cls, columns=[]):
        """
        Creates an TableModel instance, initializing the table header from the
        given ColumnInfo list

        Args:
            columns:  (list) List of ColumnInfo for table header initialization
        Returns:
            A :class:`TableModel <datavis.models.TableModel>` instance
        """
        Column = emc.Table.Column
        cols = []
        for i, info in enumerate(columns):
            if isinstance(info, models.ColumnInfo):
                cols.append(Column(i + 1, info.getName(),
                                   EmType.toModel(info.getType())))
            else:
                raise Exception("Invalid ColumnInfo.")

        return EmTableModel(emc.Table(cols))

    @classmethod
    def createStackModel(cls, path):
        """
        Creates an `TableModel <datavis.models.TableModel>` reading stack from
        the given path.

        Args:
            path: (str) The stack path
        """
        return EmStackModel(path)

    @classmethod
    def createVolumeModel(cls, path):
        """
        Creates an `VolumeModel <datavis.models.VolumeModel>` reading image data
        from the given path.

        Args:
            path: (str) The volume path
        """
        return EmVolumeModel(path)

    @classmethod
    def createListModel(cls, files):
        """ Creates an ListModel from the given file path list """
        return EmListModel(files)

    # FIXME: This method is duplicated with the one in TableModel
    # here seems a good place to have it
    @classmethod
    def createTableConfig(cls, table, *cols):
        """
        Create a TableModel instance from a given emc.Table input.
        This function allows users to specify the minimum of properties
        and create the config from that.
        :param table: input emc.Table that will be visualized
        :param cols: list of elements to specify the values for each
            ColumnConfig. Each element could be either
            a single string (the column name) or a tuple (column name and
            a dict with properties). If only the column name is provided,
            the property values will be inferred from the emc.Table.Column.
        :return: a new instance of TableModel
        """
        # TODO: Implement iterColumns in table
        # tableColNames = [col.getName() for col in table.iterColumns()]
        tableColNames = [table.getColumnByIndex(i).getName()
                         for i in range(table.getColumnsSize())]

        if cols is None:
            cols = tableColNames

        tableConfig = models.TableConfig()
        rest = list(tableColNames)
        for item in cols:
            if isinstance(item, str) or isinstance(item, unicode):
                name = item
                properties = {}
            elif isinstance(item, tuple):
                name, properties = item
            else:
                raise Exception("Invalid item type: %s" % type(item))

            # Only consider names that are present in the table ignore others
            if name in tableColNames and name in rest:
                col = table.getColumn(name)
                # Take the values from the 'properties' dict or infer from col
                cType = EmType.toModel(col.getType(),
                                       default=models.TYPE_STRING)
                if models.DESCRIPTION not in properties:
                    properties[models.DESCRIPTION] = col.getDescription()
                properties[models.EDITABLE] = False
                tableConfig.addColumnConfig(name, cType, **properties)
                rest.remove(name)
            else:
                raise Exception("Invalid column name: %s" % name)

        # Add the others with visible=False or True if tvConfig is empty
        visible = len(tableConfig) == 0
        for colName in rest:
            col = table.getColumn(colName)
            # Take the values from the 'properties' dict or infer from col
            cType = EmType.toModel(col.getType(),
                                   default=models.TYPE_STRING)
            properties = dict()
            properties[models.DESCRIPTION] = col.getDescription()
            properties[models.EDITABLE] = False
            properties[models.VISIBLE] = visible
            tableConfig.addColumnConfig(colName, cType, **properties)

        return tableConfig
