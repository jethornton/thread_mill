from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow

# Setup logging
#from qtpyvcp.utilities import logger
#LOG = logger.getLogger('qtpyvcp.' + __name__)

import os
current_path = os.path.dirname(os.path.realpath(__file__)) + '/'

from math import sqrt as sqrt

from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PyQt5.QtWidgets import QDataWidgetMapper
from PyQt5.Qt import QClipboard

class MyMainWindow(VCPMainWindow):
    """Main window class for the VCP."""
    def __init__(self, *args, **kwargs):
        super(MyMainWindow, self).__init__(*args, **kwargs)

        self.threadFormFwdBtn.clicked.connect(self.threadFormFwd)
        self.threadFormBackBtn.clicked.connect(self.threadFormBack)
        self.threadClassFwdBtn.clicked.connect(self.threadClassFwd)
        self.threadClassBackBtn.clicked.connect(self.threadClassBack)
        self.threadSizeFwdBtn.clicked.connect(self.threadSizeFwd)
        self.threadSizeBackBtn.clicked.connect(self.threadSizeBack)
        self.sptmSizeFwdBtn.clicked.connect(self.sptmSizeFwd)
        self.sptmSizeBackBtn.clicked.connect(self.sptmSizeBack)
        self.drillSizeFwdBtn.clicked.connect(self.drillSizeFwd)
        self.drillSizeBackBtn.clicked.connect(self.drillSizeBack)
        self.numPassesSP.valueChanged.connect(self.numPassesCalc)
        self.holeDiaSb.valueChanged.connect(self.holeDiaCalc)
        self.linearFeedSb.valueChanged.connect(self.linearFeedCalc)
        self.genGcodeBtn.clicked.connect(self.genGcode)

        self.testFwdBtn.clicked.connect(self.testFwd)
        self.testBackBtn.clicked.connect(self.testBack)
        self.saveFilePb.clicked.connect(self.saveFile)


        if not self.open_db():
            print('Failed to Open Database')

        self.sptmSizeInit()
        self.threadFormInit()
        self.numPassesCalc()

    def open_db(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(current_path + 'threads.db')
        db.open()
        return db

    def threadFormInit(self):
        self.formMapper = QDataWidgetMapper(self)
        self.formModel = QSqlQueryModel(self)
        self.formModel.setQuery('SELECT DISTINCT form FROM internal_threads')
        self.formMapper.setModel(self.formModel)
        self.formMapper.addMapping(self.threadFormLbl, 0, b'text')
        self.formMapper.toLast()
        self.formsLast = self.formMapper.currentIndex()
        self.formMapper.toFirst()
        self.threadClassInit()

    def threadFormFwd(self):
        if self.formMapper.currentIndex() != self.formsLast:
            self.formMapper.toNext()
        else:
            self.formMapper.toFirst()
        self.threadClassInit()

    def threadFormBack(self):
        if self.formMapper.currentIndex() != 0:
            self.formMapper.toPrevious()
        else:
            self.formMapper.toLast()
        self.threadClassInit()

    def threadClassInit(self):
        self.classMapper = QDataWidgetMapper(self)
        self.classModel = QSqlQueryModel(self)
        form = self.threadFormLbl.text()
        classSelect = "SELECT DISTINCT class FROM internal_threads \
            WHERE form = '{}'".format(form)
        self.classModel.setQuery(classSelect)
        self.classMapper.setModel(self.classModel)
        self.classMapper.addMapping(self.threadClassLbl, 0, b'text')
        self.classMapper.toLast()
        self.classLast = self.classMapper.currentIndex()
        self.classMapper.toFirst()
        self.threadSizeInit()

    def threadClassFwd(self):
        if self.classMapper.currentIndex() != self.classLast:
            self.classMapper.toNext()
        else:
            self.classMapper.toFirst()
        self.threadSizeInit(self.sizeMapper.currentIndex())

    def threadClassBack(self):
        if self.classMapper.currentIndex() != 0:
            self.classMapper.toPrevious()
        else:
            self.classMapper.toLast()
        self.threadSizeInit(self.sizeMapper.currentIndex())

    def threadSizeInit(self, index = 0):
        self.sizeMapper = QDataWidgetMapper(self)
        self.sizeModel = QSqlQueryModel(self)
        form = self.threadFormLbl.text()
        threadClass = self.threadClassLbl.text()
        sizeSelect = "SELECT size, pitch, major_dia, \
            min_major_dia, max_minor_dia, min_minor_dia, \
            max_pitch_dia, min_pitch_dia FROM internal_threads WHERE form \
            = '{}' AND class = '{}'".format(form, threadClass)
        self.sizeModel.setQuery(sizeSelect)
        self.sizeMapper.setModel(self.sizeModel)
        self.sizeMapper.addMapping(self.threadSizeLbl, 0, b'text')
        self.sizeMapper.addMapping(self.threadTPILbl, 1, b'text')
        self.sizeMapper.addMapping(self.threadMajorDiaLbl, 2, b'text')
        self.sizeMapper.addMapping(self.minMajorDiaLbl, 3, b'text')
        self.sizeMapper.addMapping(self.maxMinorDiaLbl, 4, b'text')
        self.sizeMapper.addMapping(self.minMinorDiaLbl, 5, b'text')
        self.sizeMapper.addMapping(self.maxPitchDiaLbl, 6, b'text')
        self.sizeMapper.addMapping(self.minPitchDiaLbl, 7, b'text')
        self.sizeMapper.toLast()
        self.sizeLast = self.sizeMapper.currentIndex()
        self.sizeMapper.setCurrentIndex(index)
        self.drillSizeInit()
        self.threadSizeCalc()
        self.numPassesCalc()

    def threadSizeFwd(self):
        if self.sizeMapper.currentIndex() != self.sizeLast:
            self.sizeMapper.toNext()
        else:
            self.sizeMapper.toFirst()
        self.drillSizeInit()
        self.threadSizeCalc()
        self.numPassesCalc()

    def threadSizeBack(self):
        if self.sizeMapper.currentIndex() != 0:
            self.sizeMapper.toPrevious()
        else:
            self.sizeMapper.toLast()
        self.drillSizeInit()
        self.threadSizeCalc()
        self.numPassesCalc()

    def threadSizeCalc(self):
        # PDO calculations
        threadMajorDia = float(self.threadMajorDiaLbl.text())
        drillDia = float(self.holeDiaSb.value())
        standardPDO = threadMajorDia - drillDia
        self.sptmThreadingPDOLbl.setText('{:.04f}'.format(standardPDO))
        # Actual thread height = 1/2 PDO
        threadHeightStandard = standardPDO / 2
        self.threadHeightStdLbl.setText('{:.04f}'.format(threadHeightStandard))
        threadTrangleHeight = threadHeightStandard / 0.625
        self.threadTriangleHeightLbl.setText('{:.04f}'.format(threadTrangleHeight))
        threadPushOutAdj = threadTrangleHeight * 0.125
        self.threadPushOutAdjLbl.setText('{:.04f}'.format(threadPushOutAdj))
        threadPDOAdjustOut = threadPushOutAdj * 2
        self.threadPDOAdjustOutLbl.setText('{:.04f}'.format(threadPDOAdjustOut))
        # -2*(Crest*(SQRT(3)/2))
        sptmCrest = float(self.sptmCrestLbl.text())
        threadPDOCrestAdj = -2 * (sptmCrest * (sqrt(3)/2))
        self.threadPDOCrestAdjLbl.setText('{:.04f}'.format(threadPDOCrestAdj))
        finalPDO = standardPDO + threadPDOAdjustOut + threadPDOCrestAdj
        self.threadFinalPDOLbl.setText('{:.04f}'.format(finalPDO))
        # if final PDO is greater than tip height check
        if self.sptmTipHeight > finalPDO:
            self.sptmTipOkLbl.setText('OK')
        else:
            self.sptmTipOkLbl.setText('Tip Too Small')



    def sptmSizeInit(self):
        self.sptmMapper = QDataWidgetMapper(self)
        self.sptmModel = QSqlQueryModel(self)
        self.sptmModel.setQuery('SELECT * FROM sptm')
        self.sptmMapper.setModel(self.sptmModel)
        self.sptmMapper.addMapping(self.sptmSizeLbl, 0, b'text')
        self.sptmMapper.addMapping(self.sptmDiaLbl, 1, b'text')
        self.sptmMapper.addMapping(self.sptmCrestLbl, 2, b'text')
        self.sptmMapper.addMapping(self.sptmMaxDepthLbl, 3, b'text')
        self.sptmMapper.addMapping(self.sptmFlutesLbl, 4, b'text')
        self.sptmMapper.addMapping(self.sptmNeckDiaLbl, 5, b'text')
        self.sptmMapper.toLast()
        self.sptmLast = self.sptmMapper.currentIndex()
        self.sptmMapper.toFirst()
        #self.sptmCalc()

    def sptmSizeFwd(self):
        if self.sptmMapper.currentIndex() != self.sptmLast:
            self.sptmMapper.toNext()
        else:
            self.sptmMapper.toFirst()
        self.sptmCalc()

    def sptmSizeBack(self):
        if self.sptmMapper.currentIndex() != 0:
            self.sptmMapper.toPrevious()
        else:
            self.sptmMapper.toLast()
        self.sptmCalc()

    def sptmCalc(self):
        drillDiameter = float(self.holeDiaSb.value())
        sptmCutterDia = float(self.sptmDiaLbl.text())
        if sptmCutterDia < drillDiameter:
            self.sptmDiaOkLbl.setText('Ok')
        else:
            self.sptmDiaOkLbl.setText('TOO BIG!')
        sptmNeckDia = float(self.sptmNeckDiaLbl.text())
        self.sptmTipHeight = sptmCutterDia - sptmNeckDia
        self.sptmTipHeightLbl.setText('{:.4f}'.format(self.sptmTipHeight))

    def drillSizeInit(self):
        self.drillMapper = QDataWidgetMapper(self)
        self.drillQueryModel = QSqlQueryModel(self)
        minMinorDia = str(self.minMinorDiaLbl.text())
        maxMinorDia = str(self.maxMinorDiaLbl.text())
        drillSelect = "SELECT * FROM drills WHERE dia >= '{}' \
            AND dia <= '{}'".format(minMinorDia, maxMinorDia)
        self.drillQueryModel.setQuery(drillSelect)
        self.drillMapper.setModel(self.drillQueryModel)
        self.drillMapper.addMapping(self.drillTypeLbl, 0, b'text')
        self.drillMapper.addMapping(self.drillSizeLbl, 1, b'text')
        self.drillMapper.addMapping(self.drillDiaLbl, 2, b'text')
        self.drillMapper.toLast()
        self.drillLast = self.drillMapper.currentIndex()
        self.drillMapper.toFirst()
        # setup hole dia spinbox
        self.holeDiaSb.setMinimum(float(self.minMinorDiaLbl.text()))
        self.holeDiaSb.setMaximum(float(self.maxMinorDiaLbl.text()))
        # setup pitch dia spinbox
        self.pitchDiaSb.setMinimum(float(self.minPitchDiaLbl.text()))
        self.pitchDiaSb.setMaximum(float(self.maxPitchDiaLbl.text()))

        self.sptmCalc()
        self.threadPercent()

    def drillSizeFwd(self):
        if self.drillMapper.currentIndex() != self.drillLast:
            self.drillMapper.toNext()
        else:
            self.drillMapper.toFirst()
        self.sptmCalc()
        self.threadPercent()
        self.threadSizeCalc()

    def drillSizeBack(self):
        if self.drillMapper.currentIndex() != 0:
            self.drillMapper.toPrevious()
        else:
            self.drillMapper.toLast()
        self.sptmCalc()
        self.threadPercent()
        self.threadSizeCalc()

    def threadPercent(self):
        majorDia = float(self.threadMajorDiaLbl.text())
        minorDia = float(self.drillDiaLbl.text())
        # note for metric convert to TPI
        threadPitch = float(self.threadTPILbl.text())
        threadEngagement = ((majorDia - minorDia) * threadPitch) / 0.01299
        self.threadPercentLbl.setText('{:.0f}%'.format(threadEngagement))

    def numPassesCalc(self):
        majorDia = float(self.threadMajorDiaLbl.text())
        minorDia = float(self.holeDiaSb.value())
        threadDepth = (majorDia - minorDia)
        if self.numPassesSP.value() == 1:
            self.passDiaLbl_0.setText('{:.4f}'.format(majorDia))
            self.passDiaLbl_1.setText('')
            self.passDiaLbl_2.setText('')
            self.passDiaLbl_3.setText('')

            self.passPercentLbl_1.setText('100%')
            self.passPercentLbl_2.setText('')
            self.passPercentLbl_3.setText('')
            self.passPercentLbl_4.setText('')

        if self.numPassesSP.value() == 2:

            self.passDiaLbl_0.setText('{:.4f}'.format(minorDia \
                + (threadDepth * 0.65)))
            self.passDiaLbl_1.setText('{:.4f}'.format(majorDia))
            self.passDiaLbl_2.setText('')
            self.passDiaLbl_3.setText('')

            self.passPercentLbl_1.setText('65%')
            self.passPercentLbl_2.setText('35%')
            self.passPercentLbl_3.setText('')
            self.passPercentLbl_4.setText('')

        if self.numPassesSP.value() == 3:
            self.passDiaLbl_0.setText('{:.4f}'.format(minorDia \
                + (threadDepth * 0.50)))
            self.passDiaLbl_1.setText('{:.4f}'.format(minorDia \
                + (threadDepth * 0.80)))
            self.passDiaLbl_2.setText('{:.4f}'.format(majorDia))
            self.passDiaLbl_3.setText('')

            self.passPercentLbl_1.setText('50%')
            self.passPercentLbl_2.setText('30%')
            self.passPercentLbl_3.setText('20%')
            self.passPercentLbl_4.setText('')

        if self.numPassesSP.value() == 4:
            self.passDiaLbl_0.setText('{:.4f}'.format(minorDia \
                + (threadDepth * 0.40)))
            self.passDiaLbl_1.setText('{:.4f}'.format(minorDia \
                + (threadDepth * 0.67)))
            self.passDiaLbl_2.setText('{:.4f}'.format(minorDia \
                + (threadDepth * 0.87)))
            self.passDiaLbl_3.setText('{:.4f}'.format(majorDia))

            self.passPercentLbl_1.setText('40%')
            self.passPercentLbl_2.setText('27%')
            self.passPercentLbl_3.setText('20%')
            self.passPercentLbl_4.setText('13%')

    def holeDiaCalc(self):
        majorDia = float(self.threadMajorDiaLbl.text())
        minorDia = self.holeDiaSb.value()
        # note for metric convert to TPI
        threadPitch = float(self.threadTPILbl.text())
        threadEngagement = ((majorDia - minorDia) * threadPitch) / 0.01299
        self.threadPerLbl.setText('{:.1f}%'.format(threadEngagement))


    def genGcode(self):
        # make sure your using the hole size as the starting point
        self.gcodeText.setPlainText("; JT's Thread Mill Wizard")
        self.gcodeText.append('F25')
        self.gcodeText.append('G0 X2 Y2 Z0')
        self.gcodeText.append('G91')
        self.gcodeText.append('; Number of thread passes {}' \
            .format(self.numPassesSP.value()))
        for i in range(self.numPassesSP.value()):
            passDiameter = float(getattr(self, 'passDiaLbl_' + str(i)).text())
            # go to hole bottom
            threadTPI = float(self.threadTPILbl.text())
            threadPitch = 1.0 / threadTPI
            threadBottom = -(threadPitch * (self.threadCountSb.value() + 1))
            self.gcodeText.append('G0 Z{}'.format(threadBottom))
            # go to start of lead in arc
            cutterClearance = 0.020
            minorDia = float(self.holeDiaSb.value())
            toolDia = float(self.sptmDiaLbl.text())
            yStartLeadIn = -((minorDia - (cutterClearance * 2)) - toolDia) / 2
            self.gcodeText.append('G1 Y{:.4f}'.format(yStartLeadIn))
            # lead in arc
            sptmCutterDia = float(self.sptmDiaLbl.text())
            leadInYEnd = ((passDiameter - sptmCutterDia) / 2) + abs(yStartLeadIn)
            leadInZEnd = threadPitch / 2
            leadInJOffset = leadInYEnd / 2
            self.gcodeText.append('G3 X0.0 Y{:.4f} Z{:.4f} J{:.4f}' \
                .format(leadInYEnd, leadInZEnd, leadInJOffset))
            # spiral up
            threadCount = int(self.threadCountSb.text())
            finalZ = threadPitch * threadCount
            jOffset = -(passDiameter - sptmCutterDia) / 2
            self.gcodeText.append('G3 J{} Z{} P{}'. \
                format(jOffset, finalZ, threadCount))
            # lead out arc
            leadOutYEnd = -((passDiameter - sptmCutterDia) / 2) - abs(yStartLeadIn)
            leadOutZEnd = threadPitch / 2
            leadOutJOffset = -(leadInYEnd / 2)
            self.gcodeText.append('G3 X0.0 Y{:.4f} Z{:.4f} J{:.4f}' \
                .format(leadOutYEnd, leadOutZEnd, leadOutJOffset))
            # go to center
            yCenter = ((minorDia - (cutterClearance * 2)) - toolDia) / 2
            self.gcodeText.append('G1 Y{:.4f}'.format(yCenter))

        self.gcodeText.append('G90')
        #self.gcodeText.append('G0 X2 Y2')
        self.gcodeText.append('M2')

    def linearFeedCalc(self):
        # Internal Threads
        # Linear feed * ((Major thread dia - Tool dia) / Major thread dia)
        minorDia = float(self.holeDiaSb.value())
        majorDia = float(self.threadMajorDiaLbl.text())
        cutterDia = float(self.sptmDiaLbl.text())
        linearFeed = self.linearFeedSb.value()
        circularFeed = ((majorDia - cutterDia) / majorDia) * linearFeed
        self.circularFeedLbl.setText('{:.1f}'.format(circularFeed))

    def testFwd(self):
        self.gcodeText.append('line du')

    def testBack(self):
        pass

    def saveFile(self):
        ngcFile = os.path.join(os.getenv("HOME"), 'linuxcnc/nc_files', 'jt.ngc')
        with open(ngcFile, 'w') as f:
           f.write(str(self.gcodeText.toPlainText()))

    """ 
    def appendSPTM(parent):
        query = QSqlQuery()
        query.prepare("INSERT INTO sptm (size, diameter, crest, max_depth) \
        VALUES (:size, :diameter, :crest, :max_depth)")
        query.bindValue(":size", parent.sptmSizeEntry.text())
        query.bindValue(":diameter", parent.sptmDiameterEntry.text())
        query.bindValue(":crest", parent.sptmCrestEntry.text())
        query.bindValue(":max_depth", parent.sptmMaxDepthEntry.text())
        if query.exec_():
            print("Successful")
            parent.sptmSizeEntry.setText('')
            parent.sptmDiameterEntry.setText('')
            parent.sptmCrestEntry.setText('')
            parent.sptmMaxDepthEntry.setText('')
            parent.statusBar.showMessage("Database Insert Successful",5000)
        else:
            print("Error: ", query.lastError().text())
        """





