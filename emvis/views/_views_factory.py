
import datavis as dv

from ..models import ModelsFactory


class ViewsFactory:
    """ Factory class to centralize the creation of Views, using the
    underlying classes from em-core.
    """

    @staticmethod
    def createImageView(path, **kwargs):
        """ Create an ImageView and load the image from the given path """
        imgView = dv.views.ImageView(**kwargs)
        imgModel = ModelsFactory.createImageModel(path)
        imgView.setModel(imgModel)
        return imgView

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
    def createDataView(path, **kwargs):
        """ Create an DataView and load the volume from the given path """
        model = ModelsFactory.createTableModel(path)
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
