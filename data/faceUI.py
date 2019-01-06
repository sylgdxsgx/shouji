# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'face.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui,self).__init__()
        self.setObjectName("face")
        self.setWindowTitle("face")
        self.resize(1050,100)
        MainVLayout = QtWidgets.QVBoxLayout()
        MainVLayout.setContentsMargins(0,0,0,0) #设置四周边距
        MainVLayout.setSpacing(0)               #设置控件间的距离
        #顶部UpMainWidget
        self.UpMainWidget = QtWidgets.QWidget()
        self.UpMainWidget.setObjectName("UpMainWidget")
        self.UpMainWidget.setFixedHeight(70)
        self.UpMainWidget.setStyleSheet("background-color: rgb(230, 230, 230);")

        #该布局包含ShowWidget、line
        UpVLayout = QtWidgets.QVBoxLayout(self.UpMainWidget)
        UpVLayout.setSpacing(0)
        UpVLayout.setContentsMargins(4,0,4,30)      #布局高度为100-30=70
        #顶部ShowWidget
        self.ShowWidget = QtWidgets.QWidget()
        self.ShowWidget.setFixedHeight(40)          #ShowWidget高度为68

        showHLayout = QtWidgets.QHBoxLayout(self.ShowWidget)
        showHLayout.setSpacing(0)
        showHLayout.setContentsMargins(400,0,0,0)

        #时间
        self.timeLable = QtWidgets.QLabel()
        self.timeLable.setObjectName("timeLable")
        self.timeLable.setFixedSize(80,25)
        self.timeLable.setAlignment(QtCore.Qt.AlignCenter)
        self.timeLable.setStyleSheet("QLabel{background:white;}""QLabel{color:rgb(0,0,255);font-size:20px;font-weight:bold;font-family:Times New Roman;}")

        #百分比
        percentLable = QtWidgets.QLabel()
        percentLable.setFixedSize(270,25)
        class MyComboBox(QtWidgets.QComboBox):
            def __init__(self,parent=None):
                super().__init__(parent)

            def wheelEvent(self, QWheelEvent):
                pass
        self.pre_percent_comBox = MyComboBox(percentLable)
        self.pre_percent_comBox.setObjectName("pre_percent_comBox")
        self.pre_percent_comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""color:rgb(99, 49, 0);""font: 11pt \"Times New Roman\";")
        self.pre_percent_comBox.setGeometry(0,0,60,25)
        for i in range(10):
            self.pre_percent_comBox.addItem("-{}0%".format(i+1))
        # self.pre_percent_comBox.setCurrentIndex(4)


        self.aft_percent_comBox = MyComboBox(percentLable)
        self.aft_percent_comBox.setObjectName("aft_percent_comBox")
        self.aft_percent_comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""color:rgb(99, 49, 0);""font: 11pt \"Times New Roman\";")
        self.aft_percent_comBox.setGeometry(195,0,75,25)
        for i in range(5):
            self.aft_percent_comBox.addItem("{}0%".format(i+1))
        self.aft_percent_comBox.addItem("100%")
        self.aft_percent_comBox.addItem("200%")
        self.aft_percent_comBox.addItem("500%")
        # self.aft_percent_comBox.setCurrentIndex(1)

        #额度
        self.myPercent = QtWidgets.QLabel(percentLable)
        self.myPercent.setObjectName("myPercent")
        self.myPercent.setText("00.00(0.0%)")
        self.myPercent.setAlignment(QtCore.Qt.AlignCenter)
        self.myPercent.setStyleSheet("QLabel{color:rgb(0, 85, 255);font-size:11pt;font-weight:bold;font-family:等线 Light;}")
        self.myPercent.setGeometry(60,0,135,25)

        showHLayout.addStretch(1)
        showHLayout.addWidget(percentLable)
        showHLayout.addWidget(self.timeLable)

        #状态
        self.bet_status = QtWidgets.QLabel(self.ShowWidget)
        self.bet_status.setObjectName("bet_status")
        self.bet_status.setGeometry(2,5,1,25)
        self.bet_status.setAlignment(QtCore.Qt.AlignCenter)

        #期号
        self.winLable = QtWidgets.QLabel(self.ShowWidget)
        self.winLable.setObjectName("win_Lable")
        self.winLable.setFixedSize(200,35)
        self.winLable.setStyleSheet("color:rgb(0, 85, 255);""font: 14pt \"Times New Roman\";")
        self.winLable.move(80,2)

        #横线
        line = QtWidgets.QFrame()
        line.setFixedHeight(2)          #横线高度为2
        line.setStyleSheet("background-color: rgb(1, 1, 1);")

        UpVLayout.addWidget(self.ShowWidget)
        UpVLayout.addWidget(line)

        # self.setbtn = QtWidgets.QPushButton()
        # self.setbtn.setObjectName("set_btn")
        # self.setbtn.setText("set")
        # self.setbtn.setFixedSize(40,30)

        # optHLayout = QtWidgets.QHBoxLayout()
        # optHLayout.setContentsMargins(0,0,800,0)

        #plan按钮
        self.plan_btn = QtWidgets.QPushButton(self.UpMainWidget)
        self.plan_btn.setObjectName("plan_btn")
        self.plan_btn.setText("plan")
        self.plan_btn.setFixedSize(60,28)
        self.plan_btn.move(10,42)
        # optHLayout.addWidget(self.plan_btn)

        #award按钮
        self.award_btn = QtWidgets.QPushButton(self.UpMainWidget)
        self.award_btn.setObjectName("award_btn")
        self.award_btn.setText("award")
        self.award_btn.setFixedSize(60,28)
        self.award_btn.move(75,42)
        # optHLayout.addWidget(self.award_btn)

        #report按钮
        self.report_btn = QtWidgets.QPushButton(self.UpMainWidget)
        self.report_btn.setObjectName("report_btn")
        self.report_btn.setText("report")
        self.report_btn.setFixedSize(60,28)
        self.report_btn.move(140,42)
        # optHLayout.addWidget(self.report_btn)

        #log按钮
        self.log_btn = QtWidgets.QPushButton(self.UpMainWidget)
        self.log_btn.setObjectName("log_btn")
        self.log_btn.setText("log")
        self.log_btn.setFixedSize(60,28)
        self.log_btn.move(205,42)
        # optHLayout.addWidget(self.report_btn)


        #中间OpWidget
        self.MidWidget = QtWidgets.QWidget()
        self.MidWidget.setObjectName("MidWidget")
        self.MidWidget.setFixedHeight(30)
        self.MidWidget.setStyleSheet("background-color: rgb(230, 230, 230);")

        MidHLayout = QtWidgets.QHBoxLayout(self.MidWidget)
        MidHLayout.setContentsMargins(0,0,0,0)

        #装Award按钮
        self.OpAwardWidget = QtWidgets.QWidget()
        self.OpAwardWidget.setObjectName("OpAwardWidget")
        self.OpAwardWidget.setFixedHeight(30)
        # self.OpAwardWidget.setFixedSize(self.MidWidget.width(),self.MidWidget.height())
        MidHLayout.addWidget(self.OpAwardWidget)

        self.cqc_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.cqc_btn.setObjectName("cqc")
        self.cqc_btn.setText("cqc")
        self.cqc_btn.setFixedSize(40,24)
        self.cqc_btn.move(20,6)

        self.tx_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.tx_btn.setObjectName("tx")
        self.tx_btn.setText("tx")
        self.tx_btn.setFixedSize(40,24)
        self.tx_btn.move(65,6)

        self.myaward_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.myaward_btn.setObjectName("myaward")
        self.myaward_btn.setText("my")
        self.myaward_btn.setFixedSize(40,24)
        self.myaward_btn.move(110,6)

        self.three_three_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.three_three_btn.setObjectName("3-3")
        self.three_three_btn.setText('3-3')
        self.three_three_btn.setFixedSize(40,24)
        self.three_three_btn.move(200,6)

        self.one_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.one_btn.setObjectName("----1")
        self.one_btn.setText('----1')
        self.one_btn.setFixedSize(40,24)
        self.one_btn.move(250,6)

        self.twe_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.twe_btn.setObjectName("---1-")
        self.twe_btn.setText('---1-')
        self.twe_btn.setFixedSize(40,24)
        self.twe_btn.move(300,6)

        self.three_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.three_btn.setObjectName("--1--")
        self.three_btn.setText('--1--')
        self.three_btn.setFixedSize(40,24)
        self.three_btn.move(350,6)

        self.four_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.four_btn.setObjectName("-1---")
        self.four_btn.setText('-1---')
        self.four_btn.setFixedSize(40,24)
        self.four_btn.move(400,6)

        self.five_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.five_btn.setObjectName("1----")
        self.five_btn.setText('1----')
        self.five_btn.setFixedSize(40,24)
        self.five_btn.move(450,6)

        self.fivefive_btn = QtWidgets.QPushButton(self.OpAwardWidget)
        self.fivefive_btn.setObjectName("11111")
        self.fivefive_btn.setText('1111')
        self.fivefive_btn.setFixedSize(40,24)
        self.fivefive_btn.move(500,6)

        self.losecount_label = QtWidgets.QLabel(self.OpAwardWidget)
        self.losecount_label.setObjectName("losecount_label")
        self.losecount_label.setFixedSize(800,24)
        self.losecount_label.setStyleSheet("background-color: rgb(0, 230, 0);")
        self.losecount_label.move(600,6)


        #底部TableWidget
        self.ButtonWidget = QtWidgets.QWidget()
        self.ButtonWidget.setObjectName("ButtonWidget")
        # self.ButtonWidget.setStyleSheet("background-color: rgb(130, 230, 0);")
        # self.ButtonWidget.setMinimumHeight(500)
        TableHLayout= QtWidgets.QHBoxLayout(self.ButtonWidget)
        TableHLayout.setContentsMargins(0,0,0,0)
        self.Plan_TableWidget = QtWidgets.QWidget()
        self.Plan_TableWidget.setObjectName("PlanTableWidget")
        self.Plan_TableWidget.setMinimumHeight(600)
        self.Plan_TableWidget.setStyleSheet("background-color: rgb(230, 230, 230);")
        TableHLayout.addWidget(self.Plan_TableWidget)

        self.Award_TableWidget = QtWidgets.QWidget()
        self.Award_TableWidget.setObjectName("AwardTableWidget")
        self.Award_TableWidget.setMinimumHeight(600)
        self.Award_TableWidget.setStyleSheet("background-color: rgb(230, 230, 230);")
        TableHLayout.addWidget(self.Award_TableWidget)

        self.Report_TableWidget = QtWidgets.QWidget()
        self.Report_TableWidget.setObjectName("ReportTableWidget")
        self.Report_TableWidget.setMinimumHeight(600)
        self.Report_TableWidget.setStyleSheet("background-color: rgb(230, 230, 230);")
        TableHLayout.addWidget(self.Report_TableWidget)

        self.Log_TableWidget = QtWidgets.QWidget()
        self.Log_TableWidget.setObjectName("LogTableWidget")
        self.Log_TableWidget.setMinimumHeight(600)
        self.Log_TableWidget.setStyleSheet("background-color: rgb(230, 230, 230);")
        TableHLayout.addWidget(self.Log_TableWidget)

        self.ButtonWidget.setLayout(TableHLayout)

        # self.ButtonWidget.isEnabled()


        MainVLayout.addWidget(self.UpMainWidget)
        MainVLayout.addWidget(self.MidWidget)
        MainVLayout.addWidget(self.ButtonWidget)
        self.setLayout(MainVLayout)
        # self.show()

