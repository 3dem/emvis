import datavis as dv

from ._emtype import EmType
from ._empath import EmPath
from ._image_manager import ImageManager, ImageRef


MOVIE_SIZE = 1000

HIGHLIGHTER = {
    EmPath.EXT_PY: dv.widgets.PythonHighlighter,
    EmPath.EXT_JSON: dv.widgets.JsonSyntaxHighlighter
}


def getHighlighterClass(extType):
    return HIGHLIGHTER.get(extType, None)