
import os
import argparse
from glob import glob


class ValidateValues(argparse.Action):
    """ Class that allows the validation of mapped arguments values to the user
    valuesDict. The valuesDict keys most be specified in lower case.
    Example of use with argparse:
    on_off = {'on': True, 'off': False}
    argParser.add_argument('--zoom', type=str, default='on', required=False,
                           choices=on_off.keys(), action=ValidateValues,
                           valuesDict=on_off,
                           help=' Enable/disable the option to zoom in/out in '
                                'the image(s)')
    """
    def __init__(self, option_strings, dest, valuesDict, **kwargs):
        """ Creates a ValidateValues object
         - kwargs: The argparse.Action arguments and
            - valuesDict:  (dict) a dictionary for maps the values
        """
        argparse.Action.__init__(self, option_strings, dest, **kwargs)
        self._valuesDict = valuesDict or dict()

    def __call__(self, parser, namespace, values, option_string=None):
        values = str(values).lower()
        value = self._valuesDict.get(values, self._valuesDict.get(
            values.upper()))
        if value is None:
            raise ValueError("Invalid argument for %s" % option_string)
        setattr(namespace, self.dest, value)


class ValidateMics(argparse.Action):
    """
    Class that allows the validation of the values corresponding to
    the "picker" parameter
    """
    def __init__(self, option_strings, dest, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Validate the maximum number of values corresponding to the
        picker parameter. Try to matching a path pattern for micrographs
        and another for coordinates.

        Return a list of tuples [mic_path, pick_path].
        """
        length = len(values)
        result = dict()
        if length > 2:
            raise ValueError("Invalid number of arguments for %s. Only 2 "
                             "arguments are supported." % option_string)

        if length > 0:
            mics = self.__ls(values[0])
            for i in mics:
                basename = os.path.splitext(os.path.basename(i))[0]
                result[basename] = (i, None)

        if length > 1:
            coords = self.__ls(values[1])
            for i in coords:
                basename = os.path.splitext(os.path.basename(i))[0]
                t = result.get(basename)
                if t:
                    result[basename] = (t[0], i)

        setattr(namespace, self.dest, result)

    def __ls(self, pattern):
        return glob(pattern)


class ValidateStrList(argparse.Action):
    """
    Class that allows the validation of the values corresponding to
    the "picker" parameter
    """

    def __init__(self, option_strings, dest, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Build a list with parameters separated by spaces.
        """
        setattr(namespace, self.dest, values.split())


def capitalizeStrList(strIterable):
    """
    Returns a capitalized str list from the given strIterable object
    :param strIterable: Iterable object
    """
    ret = []

    for v in strIterable:
        ret.append(v)
        ret.append(v.capitalize())
    return ret


def parsePickCoordinates(path):
    """ Parse (x, y) coordinates from a text file assuming
     that the first two columns on each line are x and y.
    """
    with open(path) as f:
        for line in f:
            li = line.strip()
            if li:
                parts = li.strip().split()
                size = len(parts)
                if size == 2:  # (x, y)
                    yield int(parts[0]), int(parts[1]), ""
                elif size == 3:  # (x, y, label)
                    yield int(parts[0]), int(parts[1]), str(parts[2])
                elif size == 4:  # (x1, y1, x2, y2)
                    yield int(parts[0]), int(parts[1]), \
                          int(parts[2]), int(parts[3]), ""
                elif size == 5:  # (x1, y1, x2, y2, label):
                    yield int(parts[0]), int(parts[1]), \
                          int(parts[2]), int(parts[3]), str(parts[4])
                else:
                    yield ""
