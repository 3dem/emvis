#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import random

import emvis as emv
import datavis as dv

from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtCore as qtc
from matplotlib.backends.qt_compat import QtWidgets as qtw
from matplotlib.backends.qt_compat import is_pyqt5

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg \
        import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg \
        import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)


class PlotWidget(qtw.QWidget):
    def __init__(self, plotData, **kwargs):
        qtw.QWidget.__init__(self)
        self._path = kwargs['path']
        self._plotData = plotData
        self._mainLayout = qtw.QHBoxLayout(self)
        self._leftContainer = qtw.QWidget(self)
        self._plotConfigWidget = dv.widgets.PlotConfigWidget(parent=self,
                                                             **kwargs)
        self._plotConfigWidget.setMaximumWidth(
            self._plotConfigWidget.sizeHint().width())
        self._leftContainer.setMaximumWidth(
            self._plotConfigWidget.maximumWidth())
        self._plotConfigWidget.setSizePolicy(qtw.QSizePolicy.Expanding,
                                             qtw.QSizePolicy.Expanding)
        self._plotConfigWidget.sigError.connect(self.__showMsgBox)
        layout = qtw.QBoxLayout(qtw.QBoxLayout.TopToBottom, self._leftContainer)
        layout.addWidget(self._plotConfigWidget)
        self._buttonPlot = qtw.QPushButton(self)
        self._buttonPlot.setText('Plot')
        self._buttonPlot.setSizePolicy(qtw.QSizePolicy.Fixed,
                                       qtw.QSizePolicy.Fixed)
        self._buttonPlot.clicked.connect(self.__onButtonPlotClicked)
        layout.addWidget(self._buttonPlot)
        splitter = qtw.QSplitter(qtc.Qt.Horizontal, self)
        #  The Canvas
        self.__canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.__canvas.setSizePolicy(qtw.QSizePolicy.Expanding,
                                    qtw.QSizePolicy.Expanding)
        self._rightContainer = qtw.QWidget(self)
        layout = qtw.QVBoxLayout(self._rightContainer)
        layout.addWidget(NavigationToolbar(self.__canvas, self))
        layout.addWidget(self.__canvas)

        splitter.addWidget(self._leftContainer)
        splitter.setCollapsible(0, False)
        splitter.addWidget(self._rightContainer)
        self._mainLayout.addWidget(splitter)

    def __showMsgBox(self, text):
        """
        Show a message box with the given text, icon and details.
        The icon of the message box can be specified with one of the Qt values:
            QMessageBox.NoIcon
            QMessageBox.Question
            QMessageBox.Information
            QMessageBox.Warning
            QMessageBox.Critical
        """
        msgBox = qtw.QMessageBox()
        msgBox.setText(text)
        msgBox.setStandardButtons(qtw.QMessageBox.Ok)
        msgBox.setDefaultButton(qtw.QMessageBox.Ok)
        msgBox.exec_()

    def __plot(self, **kwargs):
        ax = self.__canvas.figure.add_subplot(111)
        ax.plot(self._plotData, 'r-')
        ax.set_title(kwargs.get('title', ""))
        self.__canvas.draw()

    def __onButtonPlotClicked(self):
        """ Invoked when the plot button is clicked """
        config = self._plotConfigWidget.getConfiguration()
        print('Plot configuration: ', config)
        if config is not None:
            scipion = os.environ.get('SCIPION_HOME', 'scipion')
            pwplot = os.path.join(scipion, 'pyworkflow', 'apps',
                                  'pw_plot.py')
            fileName = self._path
            plotConfig = config['config']
            params = config['params']
            plotType = plotConfig['plot-type']
            labels = ""
            colors = ""
            styles = ""
            markers = ""
            sortColumn = None
            for key in params.keys():
                p = params[key]
                labels += ' %s' % key
                colors += ' %s' % p['color']
                styles += ' %s' % p['line-style']
                markers += ' %s' % p['marker']
                if sortColumn is None:  # take the first key as sortColumn
                    sortColumn = key

            # sorted column
            if sortColumn is not None:
                sOrder = 'ASC'

            cmd = '%s --file %s --type %s --columns %s ' \
                  '--colors %s --styles %s --markers %s ' % \
                  (pwplot, fileName, plotType, labels, colors, styles,
                   markers)
            if sOrder is not None:
                cmd += ' --orderColumn %s --orderDir %s ' % (sortColumn,
                                                             sOrder)
            xLabel = plotConfig.get('x-label')
            yLabel = plotConfig.get('y-label')
            title = plotConfig.get('title')
            xAxis = plotConfig.get('x-axis')
            block = 'table-name'  # use the table name

            if xAxis:
                cmd += ' --xcolumn %s ' % xAxis
            if len(block):
                cmd += ' --block %s ' % block
            if title:
                cmd += ' --title %s ' % title
            if xLabel:
                cmd += ' --xtitle %s ' % xLabel
            if yLabel:
                cmd += ' --ytitle %s ' % yLabel
            if plotType == 'Histogram':
                cmd += ' --bins %d ' % plotConfig.get('bins', 0)

            print('Plot command: ', cmd)
            self.__plot(title=title)
        else:
            print("Invalid plot configuration")

class TestMatPlotLib(dv.tests.TestView):
    __title = "MatPlotLib example"

    def getDataPaths(self):
        return [
            self.getPath("relion_tutorial", "import", "refine3d",
                        "extra", "relion_it025_data.star")
        ]

    def createView(self):
        path = self.getDataPaths()[0]
        data = [random.random() for i in range(25)]

        tableModel = emv.models.ModelsFactory.createTableModel(path)
        tableViewConfig = tableModel.createDefaultConfig()
        #  We could pass the table instead of random data, but this is a test app.
        #  Modify according to what you need
        view = PlotWidget(data, path=path,
                          params=[col.getName() for col in tableViewConfig])
        return view

    def test_TestMatPlotLib(self):
        print('test_TestMatPlotLib')


if __name__ == '__main__':
    TestMatPlotLib().runApp()
