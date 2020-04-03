#!/usr/bin/python
# -*- coding: utf-8 -*-

import datavis as dv
import emvis as emv


class TestDualImageListView(dv.tests.TestView):
    __title = "DualImageListView example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "micrographs", "006.mrc"),
            self.getPath("relion_tutorial", "micrographs", "008.mrc"),
            self.getPath("relion_tutorial", "micrographs", "016.mrc")
        ]

    def createView(self):
        Param = dv.models.Param
        brightness = Param('brightness', 'int', value=50, display='slider',
                           range=(1, 100), label='Brightness',
                           help='Adjust image brightness.')

        threshold = Param('threshold', 'float', value=0.55,
                          label='Quality threshold',
                          help='If this is...bla bla bla')
        thresholdBool = Param('threshold', 'bool', value=True,
                              label='Quality checked',
                              help='If this is a boolean param')

        threshold5 = Param('threshold5', 'string', value='Another text',
                           label='Another text example',
                           help='Showing more text')

        threshold6 = Param('threshold6', 'float', value=1.5,
                           label='Another float',
                           help='Just another float example')

        apply = Param('apply', 'button', label='Operation1')

        form = dv.models.Form([
            brightness,
            [threshold, thresholdBool],
            threshold5,
            threshold6,
            [apply]
        ])

        return dv.views.DualImageListView(
            emv.models.ModelsFactory.createListModel(self.getDataPaths()),
            form=form, method=printFunc)


def printFunc(*args):
    print('Example function. Print the arguments:')
    print(args)


if __name__ == '__main__':
    TestDualImageListView().runApp()