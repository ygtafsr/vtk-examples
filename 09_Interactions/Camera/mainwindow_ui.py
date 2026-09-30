# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QMainWindow, QSizePolicy, QSlider,
    QSpacerItem, QVBoxLayout, QWidget)

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(884, 652)
        self.central = QWidget(MainWindow)
        self.central.setObjectName(u"central")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.central.sizePolicy().hasHeightForWidth())
        self.central.setSizePolicy(sizePolicy)
        self.central.setMinimumSize(QSize(884, 652))
        self.central.setMaximumSize(QSize(884, 652))
        self.gridLayout = QGridLayout(self.central)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label = QLabel(self.central)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMinimumSize(QSize(200, 0))
        self.label.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout.addWidget(self.label)

        self.horizontalSlider = QSlider(self.central)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.horizontalSlider.sizePolicy().hasHeightForWidth())
        self.horizontalSlider.setSizePolicy(sizePolicy2)
        self.horizontalSlider.setMaximumSize(QSize(200, 16777215))
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.horizontalSlider)

        self.label_2 = QLabel(self.central)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(200, 0))
        self.label_2.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout.addWidget(self.label_2)

        self.horizontalSlider_2 = QSlider(self.central)
        self.horizontalSlider_2.setObjectName(u"horizontalSlider_2")
        sizePolicy2.setHeightForWidth(self.horizontalSlider_2.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_2.setSizePolicy(sizePolicy2)
        self.horizontalSlider_2.setMaximumSize(QSize(200, 16777215))
        self.horizontalSlider_2.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.horizontalSlider_2)

        self.label_3 = QLabel(self.central)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout.addWidget(self.label_3)

        self.horizontalSlider_3 = QSlider(self.central)
        self.horizontalSlider_3.setObjectName(u"horizontalSlider_3")
        sizePolicy2.setHeightForWidth(self.horizontalSlider_3.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_3.setSizePolicy(sizePolicy2)
        self.horizontalSlider_3.setMaximumSize(QSize(200, 16777215))
        self.horizontalSlider_3.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.horizontalSlider_3)

        self.label_4 = QLabel(self.central)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout.addWidget(self.label_4)

        self.horizontalSlider_4 = QSlider(self.central)
        self.horizontalSlider_4.setObjectName(u"horizontalSlider_4")
        sizePolicy2.setHeightForWidth(self.horizontalSlider_4.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_4.setSizePolicy(sizePolicy2)
        self.horizontalSlider_4.setMaximumSize(QSize(200, 16777215))
        self.horizontalSlider_4.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.horizontalSlider_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_5 = QLabel(self.central)
        self.label_5.setObjectName(u"label_5")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy3)
        self.label_5.setMinimumSize(QSize(300, 400))
        self.label_5.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout.addWidget(self.label_5)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.vtk_widget = QVTKRenderWindowInteractor(self.central)
        self.vtk_widget.setObjectName(u"vtk_widget")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.vtk_widget.sizePolicy().hasHeightForWidth())
        self.vtk_widget.setSizePolicy(sizePolicy4)

        self.gridLayout.addWidget(self.vtk_widget, 0, 1, 1, 1)

        MainWindow.setCentralWidget(self.central)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Azimuth", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Elevation", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Zoom", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Roll", None))
        self.label_5.setText("")
    # retranslateUi

