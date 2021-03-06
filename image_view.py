# -*- coding:utf-8 -*-

import sys
from psd_tools import PSDImage
from PIL.ImageQt import ImageQt
from PIL import Image
from PyQt5 import QtSvg
from PyQt5.QtCore import QDir, Qt, QEvent
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap, QMovie, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QWidget)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter



class ImageViewer(QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setAlignment(Qt.AlignCenter)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Viewer")
        self.resize(500, 400)
        self.setWindowIcon(QIcon('./res/Sketch-Icon.png'))

    def open(self):
        # 打开图片后根据weight重新调整大小
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                QDir.currentPath())
        if fileName:
            # 如果是webp格式用PIL
            # 如果是psd用PSDtool
            # gif格式？
            fileType = fileName.split('.')[-1]
            if fileType == 'gif':
                #QMessageBox.information(self, "file type", "type:%s"%(fileType))
                self.movie = QMovie(fileName)
                self.movie.setCacheMode(QMovie.CacheAll)
                self.movie.setSpeed(100)
                self.imageLabel.setMovie(self.movie)
                self.movie.start()
                if not self.fitToWindowAct.isChecked():
                    self.imageLabel.adjustSize()

            elif fileType == 'psd':
                img = PSDImage.load(fileName)
                img = img.as_PIL()
                img.save('./res/temp.jpg')
                image = QImage('./res/temp.jpg')
                if image.isNull():
                    QMessageBox.information(self, "Image Viewer",
                            "Cannot load %s." % (fileName))
                    return
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.scaleFactor = 1.0

                self.printAct.setEnabled(True)
                self.fitToWindowAct.setEnabled(True)
                self.updateActions()

                if not self.fitToWindowAct.isChecked():
                    self.imageLabel.adjustSize()

            elif fileType == 'svg':
                svg = QtSvg.QSvgRenderer(fileName)
                img = QImage(svg.defaultSize().width(), svg.defaultSize().height(), QImage.Format_ARGB32)
                p = QPainter(img)
                svg.render(p)
                img.save('./res/temp.png')
                p.end()
                image = QImage('./res/temp.png')
                if image.isNull():
                    QMessageBox.information(self, "Image Viewer",
                            "Cannot load %s." % (fileName))
                    return

                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.scaleFactor = 1.0

                self.printAct.setEnabled(True)
                self.fitToWindowAct.setEnabled(True)
                self.updateActions()

                if not self.fitToWindowAct.isChecked():
                    self.imageLabel.adjustSize()

            else:
                image = QImage(fileName)
                if image.isNull():
                    QMessageBox.information(self, "Image Viewer",
                            "Cannot load %s." % (fileName))
                    return
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.scaleFactor = 1.0

                self.printAct.setEnabled(True)
                self.fitToWindowAct.setEnabled(True)
                self.updateActions()

                if not self.fitToWindowAct.isChecked():
                    self.imageLabel.adjustSize()


    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")


    def rgbColor(self):
        pass


    def hexColor(self):
        pass

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++",
                enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-",
                enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S",
                enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
                checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)

        self.rgbColor = QAction("&RGB Color", self, enabled=False,
                checkable=True, triggered=self.rgbColor)

        self.hexColor = QAction("&HEX Color", self, enabled=False,
                checkable=True, triggered=self.hexColor)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.pickColor = QMenu("&PickColor", self)
        self.pickColor.addAction(self.rgbColor)
        self.pickColor.addAction(self.hexColor)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.pickColor)
        self.menuBar().addMenu(self.helpMenu)


    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.show()
    app.installEventFilter(imageViewer)
    sys.exit(app.exec_())



# tool bar 上放一个取色的图标，点击后对图片取色，鼠标所指的地方tooltip一个rgb值
# 右键复制rgb到剪贴板
# 获取鼠标的坐标


       # if event.buttons() & Qt.LeftButton:
       #     pointX = event.globalX()
       #     pointY = event.globalY()
       #     # img is QImage type
       #     img = QPixmap.grabWindow(
       #             QApplication.desktop().winId()).toImage()
       #     rgb = img.pixel(pointX, pointY)
       #     #十进制
       #     red10 = QtGui.qRed(rgb)
       #     green10 =QtGui.qGreen(rgb)
       #     blue10 = QtGui.qBlue(rgb)
       #     color10="("+str(red10)+","+str(green10)+","+str(blue10)+")"
       #     #十六进制
       #     #print str(hex(red10))
       #     red16=str(hex(red10))[2:]
       #     green16=str(hex(green10))[2]
       #     blue16=str(hex(blue10))[2:]
       #     color16=red16+green16+blue16
       #     #print color16
       #     print "(%s,%s) = %s (%s,%s,%s)" % (pointX, pointY, color16,red10, green10, blue10)
       #     self.label.setText("(%s,%s) = %s (%s,%s,%s)" % (pointX, pointY, color16,red10, green10, blue10))

