# -*- coding: utf-8 -*-

"""
Module implementing ImageBox.
"""

import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg


class ImageBox(qtw.QWidget):
    """
    This Class display an image in a QWidget and implement several methods
    to perform some transformation in this image. Taking into account some
    widget events, the images can be rotated, scaled, fit to window, etc.s
    """
    sigMousePressed = qtc.pyqtSignal()
    sigMouseReleased = qtc.pyqtSignal()
    sigMouseMoved = qtc.pyqtSignal()
    sigMouseLeave = qtc.pyqtSignal()
    sigMouseEnter = qtc.pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialise an ImageBox instance

        Args:
            parent: reference to the parent widget
        """
        qtw.QWidget.__init__(self, parent)
        self.setupProperties()
        self.__setupUi()
        self.horizontalScrollBar.setVisible(False)
        self.verticalScrollBar.setVisible(False)
        self.lastPos = qtc.QPointF()
        self.up = 1
        self.down = 2
        self.mouseBtnState = self.up
        self.isVerticalFlip = False
        self.isHorizontalFlip = False
        self.autoFit = True

        self.setMouseTracking(True)

    def __setupUi(self):
        """
        Create the GUI of ImageBox
        """
        self.resize(205, 121)
        self.gridLayout = qtw.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalScrollBar = qtw.QScrollBar(self)
        self.verticalScrollBar.setOrientation(qtc.Qt.Vertical)
        self.verticalScrollBar.setObjectName("verticalScrollBar")
        self.gridLayout.addWidget(self.verticalScrollBar, 0, 1, 1, 1)
        self.horizontalScrollBar = qtw.QScrollBar(self)
        self.horizontalScrollBar.setOrientation(qtc.Qt.Horizontal)
        self.horizontalScrollBar.setObjectName("horizontalScrollBar")
        self.gridLayout.addWidget(self.horizontalScrollBar, 1, 0, 1, 1)

        qtc.QMetaObject.connectSlotsByName(self)

    def getScale(self):
        """ Get the value of scale """
        return self.imageTransform.getScale()

    def setImage(self, qimage):
        """
        Set a new image that will be displayed in the ImageBox.

        Args:
            qimage: QImage instance
        """
        self.setupProperties()
        self.image = qimage
        if self.image:
            self.imageTransform = ImageTransform(self.image.width(),
                                                 self.image.height())

        self.update()

    def rotationAngle(self):
        """ Get the actual rotation angle """
        return self.rotation

    def setAutoFit(self, autoFit):
        """ Set the value of auto fit. If True, fit image to the widget size

        Args:
            autoFit: new value of auto fit
        """
        self.autoFit = autoFit

    def isAutoFit(self):
        """ Return True if ImageBox is configured as auto fit """
        return self.autoFit

    def setupProperties(self):
        """ Setup all properties """
        self.image = None  # The image
        self.imgPos = qtc.QPointF()  # Initial image position
        self.transformation = qtg.QTransform()
        self.painter = qtg.QPainter()
        self.zoomStep = 0.15  # zoom step for mouse wheel

    def paintEvent(self, event):
        """
        PyQt method to implement the paint logic.

        Args:
            event: paint event
        """

        if self.image:  # Paint image
            self.painter.begin(self)
            self.painter.setTransform(self.imageTransform.transformation())
            self.painter.drawImage(0, 0, self.image)
            self.painter.end()

    @qtc.pyqtSlot()
    def rotate(self, angle):
        """
        Rotate the image by the given angle

        Args:
            angle: The angle, specified in degrees.
        """
        if self.image:
            self.imageTransform.rotate(angle)
            self.update()

    @qtc.pyqtSlot()
    def scale(self, factor):
        """ Scale the image

        Args:
            factor: The aspect ratio.
        """
        if self.image:
            self.imageTransform.setScale(factor)
            self.update()

    @qtc.pyqtSlot()
    def horizontalFlip(self):
        """ Flip horizontally the image """
        if self.image:
            self.imageTransform.horizontalFlip()
            self.update()

    def mousePressEvent(self, event):
        """ This method receive mouse press events for the widget

        Args:
            event: Mouse press event
        """
        if event.buttons() & qtc.Qt.LeftButton:
            self.mouseBtnState = self.down

        self.lastPos = event.pos()
        self.mouseBtnState = self.down

        self.sigMousePressed.emit()

    def mouseMoveEvent(self, e):
        """
        This method receive mouse move events for the widget

        Args:
            e: Mouse move event
        """
        if ((e.buttons() & qtc.Qt.LeftButton) and
                self.mouseBtnState == self.down):
            if self.mouseBtnState == self.down:
                self.moveImage(e.pos(), self.lastPos)

        self.lastPos = e.pos()
        self.sigMouseMoved.emit()

    def mouseReleaseEvent(self, event):
        """ This method receive mouse release events for the widget

        Args:
            event: Mouse Release event
        """
        self.mouseBtnState = self.up
        self.lastPos = event.pos()

        self.sigMouseReleased.emit()

    def leaveEvent(self, event):
        """ This method receive widget leave events which are passed in
        the event parameter. A leave event is sent to the widget when the mouse
        cursor leaves the widget.

        Args:
            event: leave event
        """
        self.sigMouseLeave.emit()

    def enterEvent(self, event):
        """
        This methods receive widget enter events which are passed in the event
        parameter. An event is sent to the widget when the mouse cursor enters
        the widget

        Ags:
            event: enter event
        """
        self.sigMouseEnter.emit()

    def wheelEvent(self, event):
        """
        Handle the mouse wheel event.
        From Qt Help: Returns the distance that the wheel is rotated, in eighths
                      of a degree. A positive value indicates that the wheel was
                      rotated forwards away from the user; a negative value
                      indicates that the wheel was rotated backwards toward
                      the user. Most mouse types work in steps of 15 degrees,
                      in which case the delta value is a multiple of 120; i.e.,
                      120 units * 1/8 = 15 degrees. However, some mice have
                      finer-resolution wheels and send delta values that are
                      less than 120 units (less than 15 degrees).
        Args:
            event: enter event
        """
        if self.image:
            numPixels = event.pixelDelta()
            numDegrees = event.angleDelta() / 8

            if not numDegrees.isNull():
                numSteps = numDegrees / 15
                self.changeZoom(self.imageTransform.getScale() +
                                self.zoomStep * numSteps.y(),
                                self.lastPos)
            elif not numPixels.isNull():
                # handle with pixel calc. May be in the future
                pass

        event.accept()

    def verticalFlip(self):
        """
        Flip vertically the image
        """
        if self.image:
            self.imageTransform.verticalFlip()
            self.update()

    def moveImage(self, point1, point2):
        """ Move the image from point1 to point2

        Args:
            point1: actual image location point
            point2: future image location point
        """
        if self.image:
            origDragPoint = self.imageTransform.mapInverse(point1)
            origLastPoint = self.imageTransform.mapInverse(point2)
            dx1 = origDragPoint.x() - origLastPoint.x()
            dy1 = origDragPoint.y() - origLastPoint.y()

            self.imageTransform.translate(dx1, dy1)

            self.update()

    def preferedImageSize(self):
        """ Get the preferred image size """
        if self.image:
            compW = self.width()
            compH = self.height()
            origW = self.image.width()
            origH = self.image.height()

            if compW <= 0 or compH <= 0:
                return None

            rw = compW / (origW * 1.0)
            rh = compH / (origH * 1.0)
            if rw < rh:
                r = rw
            else:
                r = rh

            wscaled = ((origW * r) - 1)  # hacer casting a int
            hscaled = ((origH * r) - 1)

        return qtc.QRect((compW - wscaled) / 2, (compH - hscaled) / 2, wscaled,
                         hscaled)

    def preferedScale(self):
        """ Get the preferred scale """
        if not self.image:
            return 1.0

        rect = self.preferedImageSize()
        if rect:
            return rect.width() / (self.image.width() * 1.0)
        else:
            return 1.0

    def clipRegion(self):
        w = self.width()
        h = self.height()

        if self.verticalScrollBar.isVisible():
            w -= self.horizontalScrollBar.height()
        if self.horizontalScrollBar.isVisible():
            h -= self.horizontalScrollBar.height()

        return qtc.QRect(0, 0, w, h)

    def centerImage(self):
        """ This method center the image """
        if not self.image:
            return

        origImgCenterX = self.imageTransform.getImgWidth() / 2
        origImgCenterY = self.imageTransform.getImgHeigth() / 2

        cRegion = self.clipRegion()
        compCenter = qtc.QPointF(cRegion.width() / 2, cRegion.height() / 2)

        compCenter = self.imageTransform.mapInverse(compCenter)

        dx1 = compCenter.x() - origImgCenterX
        dy1 = compCenter.y() - origImgCenterY

        self.imageTransform.translate(dx1, dy1)
        self.update()

    def changeZoom(self, sFact, point=None):
        """
        The image is resized taking into account the value of sFact
        Args:
            sFact: resize factor
            point: center of image
        """

        if not self.image or sFact <= 0:
            return

        if not point:  # zoom respect to image center
            point = qtc.QPoint(self.width() / 2, self.height() / 2)

        origMagPoint = self.imageTransform.mapInverse(point)
        self.imageTransform.setScale(sFact)
        newMagPoint = self.imageTransform.mapInverse(point)

        dx1 = (newMagPoint.x() - origMagPoint.x())
        dy1 = (newMagPoint.y() - origMagPoint.y())

        self.imageTransform.translate(dx1, dy1)
        self.update()

    def fitToWindow(self):
        """ The image is fit to window """
        if self.image:
            if self.preferedScale():
                self.imageTransform.setScale(self.preferedScale())
                self.centerImage()

    def resizeEvent(self, resizeEvent):
        """
        This method receive widget resize events which are passed in the event
        parameter. When resizeEvent is called, the widget already has its new
        geometry and the image is automatically fit to window.

        Args:
            resizeEvent: resize event
        """
        qtw.QWidget.resizeEvent(self, resizeEvent)
        if self.autoFit:
            self.fitToWindow()


class ImageTransform:
    """
    This class is used to specifies 2D images transformations. These
    transformations specifies how to translate, scale, rotate, etc. 2D images
    """

    def __init__(self, imgWidth, imgHeigth):
        self._oddFlips = False
        self._oddRotations = False
        self._transform = qtg.QTransform()
        self._imageWidth = imgWidth
        self._imageHeight = imgHeigth
        self._scale = 1.0
        self._rotationAngle = 0.0
        self._isVerticalFlip = False
        self._isHorizontalFlip = False

    def getOddFlips(self):
        """ Get the value of oddFlips """
        return self._oddFlips

    def setOddFlips(self, oddFlips):
        """ Set the value of oddFlips """
        self._oddFlips = oddFlips

    def getOddRotations(self):
        """ Get the value of oddRotations """
        return self._oddRotations

    def setOddRotations(self, oddRotations):
        """ Set the value of oddRotations """
        self._oddRotations = oddRotations

    def transformation(self):
        """ Get the value of transform """
        return self._transform

    def setImageWidth(self, imgWidth):
        """ Set the value of the image width

        Args:
            imgWidth: new value of the image width
        """
        self._imageWidth = imgWidth

    def getImgWidth(self):
        """ Get the value of the image width """
        return self._imageWidth

    def setImageHeigth(self, imageHeight):
        """
        Set the value of image heigth

        Args:
            imageHeight: new value of image Height
        """
        self._imageHeight = imageHeight

    def getImgHeigth(self):
        """ Get the value of image heigth """
        return self._imageHeight

    def getScale(self):
        """ Get the value of the image scale """
        return self._scale

    def setScale(self, imgScale):
        """
        Transform the image with the new scale value

        Args:
            imgScale: new value of image scale
        """
        if imgScale <= 0:
            return
        self._transform.scale(1 / self._scale, 1 / self._scale)
        self._scale = imgScale
        self._transform.scale(imgScale, imgScale)

    def getRotationAngle(self):
        """ Get the rotation angle """
        return self._rotationAngle

    def setRotationAngle(self, newRotationAngle):
        """ Set the value of Rotation Angle """
        self._rotationAngle = newRotationAngle

    def setIsHorizontalFlips(self, isHorizFlips):
        """ Set the value of isHorizontalFlip """
        self._isHorizontalFlip = isHorizFlips

    def setIsVerticalFlips(self, isVertFlips):
        """ Set the value of isVerticalFlip """
        self._isVerticalFlip = isVertFlips

    def isVerticalFlips(self):
        """ Get True if vertical flips has done to 2D image,
         otherwise return False """
        return self.isVerticalFlips

    def isHorizontalFlips(self):
        """ Get True if horizontal flips has done to 2D image,
         otherwise return False """
        return self._isHorizontalFlip

    def reset(self):
        """
        Reset the class parameters to original values(default constructor class)
        """
        self._oddFlips = False
        self._oddRotations = False;
        self._scale = 1.0;
        self._transform = qtg.QTransform();
        self._rotationAngle = 0.0

    def rotate(self, angle):
        """ This methods rotate 2D images in degrees

        Args:
            angle: value of the angles (in degrees)
        """
        self._oddRotations = not self._oddRotations

        # When only one of the flip is activated, we need to change
        # the rotation angle (XOR)
        if ((self._isHorizontalFlip and not self._isVerticalFlip) or
                (not self._isHorizontalFlip and self._isVerticalFlip)):
            angle *= -1

        center = qtc.QPointF(self._imageWidth / 2.0, self._imageHeight / 2.0)
        self._transform.translate(center.x(), center.y())
        self._transform.rotate(angle - self._rotationAngle)
        self._transform.translate(-center.x(), -center.y())
        self._rotationAngle = angle

    def horizontalFlip(self):
        """
        This methods realize a horizontally transformation-flip to 2D image
        """
        self._oddFlips = not self._oddFlips;
        self._isHorizontalFlip = not self._isHorizontalFlip
        if not self._oddRotations:
            self._transform.scale(-1.0, 1.0)
            self._transform.translate(-self._imageWidth, 0.0)
        else:
            self._transform.scale(1.0, -1.0)
            self._transform.translate(0.0, -self._imageHeight)

    def verticalFlip(self):
        """
        This methods realize a vertically transformation-flip to 2D image
        """
        self._oddFlips = not self._oddFlips
        self._isVerticalFlip = not self._isVerticalFlip
        if not self._oddRotations:
            self._transform.scale(1.0, -1.0)
            self._transform.translate(0.0, -self._imageHeight)
        else:
            self._transform.scale(-1.0, 1.0);
            self._transform.translate(-self._imageWidth, 0.0);

    def translate(self, dx, dy):
        """
        This methods moves the coordinate system dx along the x axis and dy
        along the y axis

        Args:
            dx: variation in the x axis
            dy: variation in the y axis
        """
        self._transform.translate(dx, dy)

    def mapInverse(self, point):
        """ Get an inverted copy of the map in any point

        Args:
            point: value of the point
        """
        return self._transform.inverted()[0].map(point)

    def map(self, point):
        """
        Creates and returns a point that is a copy of the given point, mapped
        into the coordinate system defined by this trasformation

        Args
            point: value of the point

        Returns: mapped point
        """
        return self._transform.map(point)