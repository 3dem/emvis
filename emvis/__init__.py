

# FIXME: Improve documentation of the sub-module
"""
This sub-module contains functions and classes that use em-core Python binding
and provide utility functions to create views.
"""
__version__ = '0.0.3'

from ._empath import EmPath
from ._image_manager import ImageManager, ImageRef, VolImageManager
from ._models_factory import ModelsFactory
from ._views_factory import ViewsFactory
from .utils import ImageElemParser, MOVIE_SIZE, getHighlighterClass
from ._emtable_model import EmTableModel, EmStackModel, EmVolumeModel
from ._empicker import EmPickerModel
from ._embrowser import *
