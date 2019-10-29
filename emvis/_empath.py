
import os


class EmPath:
    """
    Helper class to group functions related to path handling in EM.
    """
    EXT_IMAGE = 0
    EXT_VOLUME = 1
    EXT_STACK = 2
    EXT_TABLE = 3
    EXT_STD_IMAGE = 4  # Standard image extensions
    EXT_TEXT = 5
    EXT_PY = 6
    EXT_JSON = 7

    EXTESIONS_MAP = {
        EXT_IMAGE: ['.mrc', '.spi', '.xmp', '.hed', '.img', '.dm3', '.dm4',
                    '.dat'],
        EXT_VOLUME: ['.mrc', '.vol', '.map'],
        EXT_STACK: ['.mrc', '.mrcs', '.stk', '.dm3', '.dm4', '.dat'],
        EXT_TABLE: ['.star', '.xmd', '.sqlite'],
        EXT_STD_IMAGE: ['.png', '.jpg', '.jpeg', '.tif', '.bmp'],
        EXT_PY: ['.py'],
        EXT_JSON: ['.json'],
        EXT_TEXT: ['.txt', '.pos', '.bild', '.log', '.rst', '.py', '.json']
    }

    @classmethod
    def __isFile(cls, path, extType):
        if not path:
            return False
        _, ext = os.path.splitext(path)
        return ext in cls.EXTESIONS_MAP[extType]

    @classmethod
    def getExt(cls, path):
        if not path:
            return None
        _, ext = os.path.splitext(path)
        return ext

    @classmethod
    def isImage(cls, path):
        """ Return True if imagePath has an extension recognized as supported
        EM-image """
        return cls.__isFile(path, cls.EXT_IMAGE)

    @classmethod
    def isVolume(cls, path):
        return cls.__isFile(path, cls.EXT_VOLUME)

    @classmethod
    def isStack(cls, path):
        return cls.__isFile(path, cls.EXT_STACK)

    @classmethod
    def isData(cls, path):
        return cls.isImage(path) or cls.isVolume(path) or cls.isStack(path)

    @classmethod
    def isTable(cls, path):
        return cls.__isFile(path, cls.EXT_TABLE)

    @classmethod
    def isStandardImage(cls, path):
        return cls.__isFile(path, cls.EXT_STD_IMAGE)

    @classmethod
    def isTextFile(cls, path):
        return cls.__isFile(path, cls.EXT_TEXT)

    @classmethod
    def isJsonFile(cls, path):
        return cls.__isFile(path, cls.EXT_JSON)

    @classmethod
    def isPyFile(cls, path):
        return cls.__isFile(path, cls.EXT_PY)

    @classmethod
    def getExtType(cls, path):
        ext = cls.getExt(path)
        for k in cls.EXTESIONS_MAP:
            if any(ext == e for e in cls.EXTESIONS_MAP.get(k)):
                return k
        return None

    @classmethod
    def exists(cls, path):
        """ Return True if the path exists, after removing special characters.

        Special characters are:

        * @ that is used to name a table in a file, e.g particles@file.star
        * : that is used to specify format, e.g estimated_psd.ctf:mrc
        """
        if '@' in path:
            path = path.split('@')[1]

        if ':' in path:
            path = path.split(':')[0]

        return os.path.exists(path)

