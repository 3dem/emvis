
from PyQt5.QtGui import QImage

import datavis as dv

from ..models import ModelsFactory
from ._box import ImageBox


class ViewsFactory:
    """ Factory class to centralize the creation of Views, using the
    underlying classes from em-core.
    """

    @staticmethod
    def createImageView(path, **kwargs):
        """ Create an ImageView and load the image from the given path """
        imgModel = ModelsFactory.createImageModel(path)
        imgView = dv.views.ImageView(model=imgModel, **kwargs)
        return imgView

    @staticmethod
    def createImageBox(path):
        """
        Create an ImageBox and load the standard image from the given path """
        box = ImageBox()
        image = QImage(path)
        box.setImage(image)
        box.fitToSize()
        return box

    @staticmethod
    def createSlicesView(path, **kwargs):
        """ Create an SlicesView and load the slices from the given path """
        model = ModelsFactory.createStackModel(path)
        return dv.views.SlicesView(model, **kwargs)

    @staticmethod
    def createVolumeView(path, **kwargs):
        """ Create an VolumeView and load the volume from the given path """
        model = ModelsFactory.createVolumeModel(path)
        return dv.views.VolumeView(model, **kwargs)

    @staticmethod
    def createDataView(path, visible=[], render=[], **kwargs):
        """ Create an DataView and load the volume from the given path """
        model = ModelsFactory.createTableModel(path)
        if visible or render:
            cConfig = model.createDefaultConfig()
            gConfig = model.createDefaultConfig()
            iConfig = model.createDefaultConfig()
            views = {
                dv.views.COLUMNS: {dv.views.TABLE_CONFIG: cConfig},
                dv.views.GALLERY: {dv.views.TABLE_CONFIG: gConfig},
                dv.views.ITEMS: {dv.views.TABLE_CONFIG: iConfig}
            }
            for config in [cConfig, gConfig, iConfig]:
                for i, cc in config.iterColumns():
                    if visible:
                        cc[dv.models.VISIBLE] = cc.getName() in visible
                    if render:
                        cc[dv.models.RENDERABLE] = cc.getName() in render

            kwargs['views'] = views

        return dv.views.DataView(model, **kwargs)

    @staticmethod
    def createPickerView(micFiles, **kwargs):
        """
        Create an PickerView instance
        :param files: (list) Micrograph paths or None.
        :param kwargs:
           - boxSize:  (int) The box size. Default value is 100
           - sources: (dict) Each element is (mic-path, coord-path)
           - parseCoordFunc: The parser function for coordinates file
        """
        model = ModelsFactory.createPickerModel(
            files=micFiles, boxSize=kwargs.get('boxSize', 100),
            sources=kwargs.get('sources'),
            parseCoordFunc=kwargs.get('parseCoordFunc'))
        return dv.views.PickerView(model, **kwargs)
