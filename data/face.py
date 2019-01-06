import sys, re, webbrowser, os, json, requests, time, threading,signal
import queue
from PyQt5.QtWidgets import (QApplication, QWidget,QCalendarWidget, QLabel, QListView, QSystemTrayIcon, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QDesktopWidget, QDialog, QAction, QMenu, QCompleter, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, pyqtSlot,QThread
from PyQt5.QtGui import QFont, QPixmap, QPalette
from PyQt5.QtCore import * 
from PyQt5.Qt import *
from time import sleep
from atexit import register

from faceUI import Ui

import sqlite3
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from atexit import register
from Plan import Plan
from Award import Award
from Bet import Bet
from Eml import Eml



def log_out(logFilename):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)-10s: [%(levelname)s]  %(message)s',
        datefmt='%Y-%m-%d %A %H:%M:%S',
        filename=logFilename,
        filemode='a'
    )
    #输出到console
    # console = logging.StreamHandler()   #定义console handler
    # console.setLevel(logging.INFO)      #定义该handler级别
    # formatter = logging.Formatter('%(asctime)s %(filename)s : %(levelname)s %(message)s')   #定义该handler格式
    # console.setFormatter(formatter)
    # #create an instance
    # logging.getLogger().addHandler(console) #实例化添加handler

    # console = QPlainTextEditLogger(face.ui.Report_TableWidget)
    # logging.getLogger().addHandler(console)
    #输出到界面
    # console = logging.StreamHandler(face.logView)   #定义console handler
    # console.setLevel(logging.INFO)      #定义该handler级别
    # formatter = logging.Formatter('%(asctime)s %(filename)s : %(levelname)s %(message)s')   #定义该handler格式
    # console.setFormatter(formatter)
    # logging.getLogger().addHandler(console) #实例化添加handler

    """
    # logging.config.dictConfig(codecs.open("logger.yml", 'r', 'utf-8').read())
    with open("logger.yml",'r') as f:
        logging.config.dictConfig(f.read())
    logger = logging.getLogger("billingcodeowner")
    """

@register
def _out():
    logging.info('The program is going to quit (KeyboardInterrupt or SystemExit) ...')
    logging.info('Jobs: %s'%TimerRunner().scheduler.get_jobs())
    logging.info('clear jobs ...')
    TimerRunner().scheduler.remove_all_jobs()
    logging.info('Jobs: %s'%TimerRunner().scheduler.get_jobs())
    logging.info('DOWN')

class face(QWidget):

    def __init__(self):

        #UI初始化
        super(face,self).__init__()
        self.ui = Ui()
        self.center()
        #显示时间
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start()
        #Plan列表初始化
        p_layout = QHBoxLayout(self.ui.Plan_TableWidget)
        self.planTable = MyPlanTable()
        p_layout.addWidget(self.planTable)
        #Award列表初始化
        p_layout = QHBoxLayout(self.ui.Award_TableWidget)
        self.awardTable = MyAwardTable()
        self.awardTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.awardTable.customContextMenuRequested.connect(self.awardMenu)
        p_layout.addWidget(self.awardTable)
        #Report列表初始化
        p_layout = QHBoxLayout(self.ui.Report_TableWidget)
        self.reportTable = MyReportTable()
        p_layout.addWidget(self.reportTable)
        #Log列表初始化
        p_layout = QHBoxLayout(self.ui.Log_TableWidget)
        #设置日志
        # self.logView = QPlainTextEditLogger()
        # self.logView.setFormatter(logging.Formatter('%(asctime)s %(filename)-10s: [%(levelname)s]  %(message)s'))
        # logging.getLogger().addHandler(self.logView)
        # logging.getLogger().setLevel(logging.INFO)

        # p_layout.addWidget(self.logView.widget)

        #变量初始化
        self.award_play = PLAN.play[0]
        self.award_ptype = PLAN.btype[6]
        self.ui.pre_percent_comBox.setCurrentText("{}%".format(int(tr.percent_span[0]*100)))
        self.ui.aft_percent_comBox.setCurrentText("{}%".format(int(tr.percent_span[1]*100)))
        #信号初始化
        self.ui.plan_btn.clicked.connect(lambda:self.renew_data('plan'))
        self.ui.award_btn.clicked.connect(lambda:self.renew_data('award'))
        self.ui.report_btn.clicked.connect(lambda:self.renew_data('report'))
        self.ui.log_btn.clicked.connect(lambda:self.renew_data('log'))

        self.ui.cqc_btn.clicked.connect(self.renew_award)
        self.ui.tx_btn.clicked.connect(self.renew_award)
        self.ui.myaward_btn.clicked.connect(self.renew_award)
        self.ui.three_three_btn.clicked.connect(self.renew_award)
        self.ui.one_btn.clicked.connect(self.renew_award)
        self.ui.twe_btn.clicked.connect(self.renew_award)
        self.ui.three_btn.clicked.connect(self.renew_award)
        self.ui.four_btn.clicked.connect(self.renew_award)
        self.ui.five_btn.clicked.connect(self.renew_award)
        self.ui.fivefive_btn.clicked.connect(self.renew_award)

        self.ui.pre_percent_comBox.currentIndexChanged.connect(self.renew_percent)
        self.ui.aft_percent_comBox.currentIndexChanged.connect(self.renew_percent)

        #losecount信号
        self.awardTable.lose_count.connect(self.renew_loseCount)

        tr.issue_win_data.connect(self.renew_issue_win)
        tr.amount_percent_data.connect(self.renew_amount)
        tr.bet_status.connect(self.renew_bet_status)

        self.start_main()

    def awardMenu(self,pos):
        '''设置右击菜单'''
        sender = self.sender()
        index = sender.indexAt(pos)
        menu = QMenu()
        action1 = menu.addAction("activate for 1")
        action2 = menu.addAction("activate for 2")
        action3 = menu.addAction("activate for 5")
        action4 = menu.addAction("activate for 10")
        action5 = menu.addAction("activate 2 high for 1")
        action6 = menu.addAction("activate 3 high for 1")
        action = menu.exec_(self.awardTable.mapToGlobal(pos))
        if action == action1:
            activate,high,stop_in_wn = (1,1,1)
        elif action == action2:
            activate,high,stop_in_wn = (1,1,2)
        elif action == action3:
            activate,high,stop_in_wn = (1,1,5)
        elif action == action4:
            activate,high,stop_in_wn = (1,1,10)
        elif action == action5:
            activate,high,stop_in_wn = (1,2,1)
        elif action == action6:
            activate,high,stop_in_wn = (1,3,1)
        else:
            return
        bet_number = self.awardTable.horizontalHeaderItem(index.column()).text()
        '''从award添加计划'''
        PLAN.add_plan_from_award(self.award_play,self.award_ptype,bet_number,tr.current_issue,activate,high,stop_in_wn)


        # print(pos.row(),pos.column())
        # print(self.awardTable.selectionMode().selection().indexes())

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.ui.geometry()
        self.ui.move((screen.width()-size.width())/2, (screen.height()-size.height())/2-300)

    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.m_drag=True
            self.m_DragPosition=event.globalPos()-self.pos()  #记录点击坐标
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos()-self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag=False

    def renew_award(self):
        sender = self.sender()
        text = sender.objectName()
        award_list = None
        if text in ('cqc','tx'):
            self.award_play = text
            play = self.award_play
        elif text == "myaward":
            #更新数据
            # award_list=['8-2']
            award_list = PLAN.get_active_betnumber()
            # print(award_list)
            play = text

        else:
            self.award_ptype = text
            play = self.award_play
        #更新数据
        self.awardTable.setTableData(self.award_play,self.award_ptype,award_list=award_list)
        self.renew_btn(play,self.award_ptype)

    def renew_amount(self,list):
        # print(list)
        self.ui.myPercent.setText("%s(%.2f)"%(list[0],float(list[1])))

    def renew_bet_status(self,n):
        pass
        if not tr.login_status: #如果登入失败
            self.ui.bet_status.resize(70,25)
            self.ui.bet_status.setStyleSheet("background-color:rgb(0, 0, 255);""color:black;""color:white;""font: 14pt \"Times New Roman\";")
            return
        # print('bet_status=',n)
        if n==0:    #刚启动时、任务开始时
            self.ui.bet_status.resize(70,25)
            self.ui.bet_status.setStyleSheet("background-color:rgb(0, 0, 255);""color:white;""font: 14pt \"Times New Roman\";")
        if n==1:    #获取开奖期号成功
            self.ui.bet_status.resize(23,25)
            self.ui.bet_status.setStyleSheet("background-color:rgb(0, 255, 0);""color:black;""font: 14pt \"Times New Roman\";")
        if n==3:    #获取投注任务成功
            self.ui.bet_status.resize(46,25)
            self.ui.bet_status.setStyleSheet("background-color:rgb(0, 255, 0);""color:black;""font: 14pt \"Times New Roman\";")
        if n==5:    #投注成功
            self.ui.bet_status.resize(70,25)
            self.ui.bet_status.setStyleSheet("background-color:rgb(0, 255, 0);""color:black;""font: 14pt \"Times New Roman\";")
        else:
            self.ui.bet_status.resize(70,25)
            self.ui.bet_status.setStyleSheet("background-color:rgb(0, 0, 255);""color:black;""color:white;""font: 14pt \"Times New Roman\";")

    def renew_btn(self,play=None,ptype=None):
        if play == 'cqc':
            self.ui.cqc_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.tx_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.myaward_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif play == 'tx':
            self.ui.tx_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.cqc_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.myaward_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif play == 'myaward':
            self.ui.cqc_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.tx_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.myaward_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
        else:
            self.ui.cqc_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.tx_btn.setStyleSheet("background-color: rgb(230, 230, 230);")

        if ptype == '3-3':
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif ptype == '----1':
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif ptype == '---1-':
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif ptype == '--1--':
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif ptype == '-1---':
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif ptype == '1----':
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
        elif ptype == '11111':
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(130, 230, 0);")
        else:
            self.ui.three_three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.one_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.twe_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.three_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.four_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.five_btn.setStyleSheet("background-color: rgb(230, 230, 230);")
            self.ui.fivefive_btn.setStyleSheet("background-color: rgb(230, 230, 230);")


     #重写三个方法使我们的Example窗口支持拖动,上面参数window就是拖动对象

    def renew_data(self,text):
        sender = self.sender()

        if text == "show_btn":
            if self.ui.OpWidget.isVisible():
                self.ui.resize(self.ui.width(),self.ui.UpMainWidget.height())
                self.ui.OpWidget.hide()
                self.ui.ButtonWidget.hide()
            else:
                if self.ui.Plan_TableWidget.isVisible() or self.ui.Award_TableWidget.isVisible() or self.ui.Report_TableWidget.isVisible():
                    self.ui.resize(self.ui.width(),self.ui.UpMainWidget.height()+self.ui.OpWidget.height()+self.ui.ButtonWidget.height())
                    self.ui.ButtonWidget.show()
                else:
                    self.ui.resize(self.ui.width(),self.ui.UpMainWidget.height()+self.ui.OpWidget.height())
                self.ui.OpWidget.show()

        if text == "plan":
            #更新数据
            self.planTable.setTableInitData()
            if not self.ui.Plan_TableWidget.isVisible():
                self.ui.Award_TableWidget.hide()
                self.ui.OpAwardWidget.hide()
                self.ui.Report_TableWidget.hide()
                self.ui.Log_TableWidget.hide()
                self.ui.Plan_TableWidget.show()

        if text == "award":
            #更新数据
            self.awardTable.setTableData(self.award_play,self.award_ptype)
            if not self.ui.Award_TableWidget.isVisible():
                self.ui.Plan_TableWidget.hide()
                self.ui.Report_TableWidget.hide()
                self.ui.Log_TableWidget.hide()
                self.ui.Award_TableWidget.show()
                self.ui.OpAwardWidget.show()
            self.renew_btn(self.award_play,self.award_ptype)    #更新按钮颜色

        if text == "report":
            #更新数据
            self.reportTable.setTableData()
            if not self.ui.Report_TableWidget.isVisible():
                self.ui.Plan_TableWidget.hide()
                self.ui.Award_TableWidget.hide()
                self.ui.OpAwardWidget.hide()
                self.ui.Log_TableWidget.hide()
                self.ui.Report_TableWidget.show()

        if text == 'log':
            if not self.ui.Log_TableWidget.isVisible():
                self.ui.Plan_TableWidget.hide()
                self.ui.Award_TableWidget.hide()
                self.ui.OpAwardWidget.hide()
                self.ui.Report_TableWidget.hide()
                self.ui.Log_TableWidget.show()

    def renew_issue_win(self,list):
        # print(list)
        # tr.current_issue = list[0]
        # tr.current_win = list[1]
        self.ui.winLable.setText("%s 【%s】"%(list[0],list[1]))

    def renew_loseCount(self,text):
        self.ui.losecount_label.setText(text)

    def renew_percent(self):
        sender = self.sender()
        name = sender.objectName()
        if name == "pre_percent_comBox":
            tr.percent_span[0] = int(sender.currentText()[:-1])/100
        else:
            tr.percent_span[1] = int(sender.currentText()[:-1])/100

    def showTime(self):
        datetime = QDateTime.currentDateTime()
        time = QTime.currentTime()
        # text = datetime.toString()
        text = time.toString()
        self.ui.timeLable.setText(text)
        
        seconde = time.second()
        
        if tr.time_count == 0:
            tr.time_count = seconde
            
        seconde1 = seconde - tr.time_count if seconde>=tr.time_count else 60-tr.time_count+seconde
        self.ui.bet_status.setText(str(seconde1)+'/%d'%tr.cycle_time)
        # seconde1 = 90-seconde if seconde>30 else 30-seconde
        # self.ui.bet_status.setText(str(seconde1))
        

    def start_main(self):
        if not self.isVisible():
            self.ui.show()
            self.ui.UpMainWidget.show()
            self.ui.MidWidget.show()
            self.ui.OpAwardWidget.hide()
            self.ui.ButtonWidget.show()
            self.ui.Plan_TableWidget.show()
            self.ui.Award_TableWidget.hide()
            self.ui.Report_TableWidget.hide()
            self.ui.Log_TableWidget.hide()
            # self.ui.resize(self.ui.UpMainWidget.width(),self.ui.UpMainWidget.height())
        # tr.run()
        tr.begin = True
        tr.start()


class MyPlanTable(QTableWidget):
    def __init__(self,parent=None):
        self.table_ok = False   #初始化时，屏蔽信号
        super(MyPlanTable,self).__init__(parent)
        self.setColumnCount(15)
        self.setRowCount(0)
        self.setShowGrid(True)

        self.setTableHeader()
        self.setTableSize()
        self.setCellFontSize()
        self.setTableEditTrigger()
        self.setTableSelectMode()
        self.setTableInitData()

        #信号初始化
        self.cellChanged.connect(self.cell_Changed)
        self.cellDoubleClicked.connect(self.cell_Clicked)

        self.table_ok = True

    class MyComboBox(QComboBox):
        def __init__(self,parent=None):
            super().__init__(parent)

        def wheelEvent(self, QWheelEvent):
            pass

    def cell_Clicked(self,row,column):
        if column == 0:
            planname = self.item(row,column).text()
            index = '1'
            text = 0
            self.modify_plan([planname,index,text])

    def cell_Changed(self,row,column):
        ''''''
        # print(row,column,self.currentItem().text())
        if self.table_ok:
            plan_name = self.item(int(row),0).text()
            index = str(int(column)+1)
            text = self.currentItem().text()
            self.modify_plan([plan_name,index,text])

    def comBoxData(self):
        ''''''
        if self.table_ok:
            sender = self.sender()
            row,column = sender.objectName().split(' ')

            plan_name = self.item(int(row),0).text()
            index = str(int(column)+1)
            text = sender.currentText()
            self.modify_plan([plan_name,index,text])

    def modify_plan(self,list):
        '''修改计划'''
        rlt = PLAN.modifyPlan(list)


    def setTableSize(self):
        """设置表格单元格尺寸"""
        """
        首先，可以指定某个行或者列的大小
        self.MyTable.setColumnWidth(2,50)  #将第2列的单元格，设置成50宽度
        self.MyTable.setRowHeight(2,60)      #将第2行的单元格，设置成60的高度
        还可以将行和列的大小设为与内容相匹配
        self.MyTable.resizeColumnsToContents()   #将列调整到跟内容大小相匹配
        self.MyTable.resizeRowsToContents()      #将行大小调整到跟内容的大学相匹配
        :return:
        """
        # self.setColumnWidth(0,60)
        # self.setColumnWidth(1,60)
        # self.setColumnWidth(2,60)
        # self.setColumnWidth(3,60)
        # self.setColumnWidth(4,50)
        # self.setColumnWidth(5,50)
        # self.setColumnWidth(6,50)
        # self.setColumnWidth(7,90)
        # self.setColumnWidth(8,90)
        # self.setColumnWidth(9,70)
        # self.setColumnWidth(10,70)
        # self.setColumnWidth(11,90)
        # self.setColumnWidth(12,60)
        # self.setColumnWidth(13,58)
        # self.setColumnWidth(14,70)
        # self.setMinimumWidth(50)
        #设置默认行高
        self.verticalHeader().setDefaultSectionSize(30)
        #设置默认列宽
        # self.horizontalHeader().setDefaultSectionSize(100)

        #设置列宽均分
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)   #先设置列宽均分
        self.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)    #再设置根据内容调整宽度
        self.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(6,QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(7,QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(8,QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(9,QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(11,QHeaderView.ResizeToContents)



        #1.2 设置表格的行和列的大小与输入内容相匹配
        # self.resizeColumnsToContents()
        # self.resizeRowsToContents()

        #设置背景色交替
        self.setAlternatingRowColors(True)

    def setTableHeader(self):
        '''设置表格的表头'''
        #设置表头名称
        columnname = ["name","act","play","type","plan","status","lose","lose_issue","bet_issue",
                    "bet_num","unit","steps","mult","high","stop-win"]
        self.setHorizontalHeaderLabels(columnname)
        #rowname = ['a','b','c','d','e']
        #self.setVerticalHeaderLabels(rowname)

        # 4.3 隐藏表头
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(True)

        #设置表头字体颜色
        """
        PyQt5中没有如下设置背景颜色和字体颜色函数
        headItem.setBackgroundColor(QColor(c))  # 设置单元格背景颜色
        headItem.setTextColor(QColor(200, 111, 30))  # 设置文字颜色
        :return:
        有（设置字体颜色）：
        headItem.setForeground(QBrush(Qt.red))
        headItem.setForeground(QBrush(QColor(128,255,0)))
        """
        # f, ok = QFontDialog.getFont()

        for x in range(self.columnCount()):
            headItem = self.horizontalHeaderItem(x)  # 获得水平方向表头的Item对象
            # headItem.setFont(QFont("Times New Roman",10,QFont.Bold))
            headItem.setFont(QFont("Times New Roman",10))
            # if ok:
            #     headItem.setFont(f)  # 设置字体
            #设置表头字体颜色
            headItem.setForeground(QBrush(Qt.blue))
            # headItem.setForeground(QBrush(QColor(128,255,0)))
            #设置单元格背景色
            # headItem.setBackgroundColor(QColor(240,240,240,250))
            headItem.setTextAlignment(Qt.AlignLeft)

    def setTableInitData(self):
        '''plan列表中输入数据'''
        self.table_ok = False
        #先清空表
        self.setRowCount(0)
        self.clearContents()
        # for i in range(self.rowCount()):
        #     self.removeRow(0)
        #读取数据库
        plan_list = PLAN.read_all_plan()
        for i in range(len(plan_list)):
            plan1 = plan_list[i]
            self.setRowsInitData(i,plan1)
        self.table_ok = True

    def setRowsInitData(self,rows,plan):
        '''plan列表一行的数据,输入行号和数据数组'''
        if plan:
            rowcount = self.rowCount()
            self.insertRow(rowcount) #插入一行
            for i in range(len(plan)):
                if i == 0:  #plan_name
                    self.setItem(rows,i,QTableWidgetItem(str(plan[i])))
                    self.item(rows,i).setFlags(Qt.ItemIsEnabled)    #设置不可编辑
                    # self.cellDoubleClicked.connect(self.cell_clicked) #设置触发,不能放这里(会导致重复设置）

                    #判断是否为新计划
                    if int(plan[1]) == 1:
                        self.item(rows,i).setForeground(QBrush(QColor(230,0,0)))
                elif i == 1:
                    pass
                elif i == 2:    #activate
                    # comBox = QComboBox()
                    comBox = self.MyComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.activated.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    comBox.addItem("0")
                    comBox.addItem("1")
                    comBox.setCurrentText(str(plan[i]))
                    self.setCellWidget(rows,i-1,comBox)
                elif i == 3:    #play
                    # comBox = QComboBox()
                    comBox = self.MyComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.currentIndexChanged.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    comBox.addItem("cqc")
                    comBox.addItem("tx")
                    comBox.setCurrentText(plan[i])
                    self.setCellWidget(rows,i-1,comBox)
                elif i == 4:    #plan_type
                    # comBox = QComboBox()
                    comBox = self.MyComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.currentIndexChanged.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    comBox.addItem("3-3")
                    comBox.addItem("----1")
                    comBox.addItem("---1-")
                    comBox.addItem("--1--")
                    comBox.addItem("-1---")
                    comBox.addItem("1----")
                    comBox.addItem("11111")
                    comBox.setCurrentText(plan[i])
                    self.setCellWidget(rows,i-1,comBox)
                elif i == 5:    #handup_plan
                    # comBox = QComboBox()
                    comBox = self.MyComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.currentIndexChanged.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    comBox.addItem("A")
                    comBox.addItem("B")
                    comBox.addItem("C")
                    comBox.addItem("D")
                    comBox.addItem("E")
                    comBox.setCurrentText(plan[i])
                    self.setCellWidget(rows,i-1,comBox)
                elif i == 11:   #bet_unit
                    # comBox = QComboBox()
                    comBox = self.MyComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.currentIndexChanged.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    comBox.addItem("0.010") #2分
                    comBox.addItem("0.050") #1角
                    comBox.addItem("0.100") #2角
                    comBox.addItem("0.500") #1元
                    comBox.addItem("1.000") #2元
                    comBox.setCurrentText(plan[i])
                    self.setCellWidget(rows,i-1,comBox)
                elif i ==13:    #bet_mult
                    # comBox = QComboBox()
                    comBox = self.MyComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.currentIndexChanged.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    comBox.addItem("1")
                    comBox.addItem("2")
                    comBox.addItem("3")
                    comBox.addItem("4")
                    comBox.addItem("5")
                    comBox.setCurrentText(str(plan[i]))
                    self.setCellWidget(rows,i-1,comBox)
                elif i ==14:    #high_bet
                    # comBox = QComboBox()
                    comBox = self.MyComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.currentIndexChanged.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    comBox.addItem("1")
                    comBox.addItem("2")
                    comBox.addItem("3")
                    comBox.addItem("4")
                    comBox.addItem("5")
                    comBox.setCurrentText(str(plan[i]))
                    self.setCellWidget(rows,i-1,comBox)
                elif i ==15:    #stop_in_wn
                    comBox = QComboBox()
                    comBox.setObjectName(str("%d %d")%(rows,i-1))
                    comBox.currentIndexChanged.connect(self.comBoxData)
                    comBox.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
                    for j in range(10):
                        comBox.addItem(str(j))
                    for j in range(10):
                        comBox.addItem(str((j+1)*10))
                    comBox.setCurrentText(str(plan[i]))
                    self.setCellWidget(rows,i-1,comBox)
                else:
                    self.setItem(rows,i-1,QTableWidgetItem(str(plan[i])))



    def setTableEditTrigger(self):
        """设置表格是否可编辑"""
        """使用格式说明：
                在默认情况下，表格里的字符是可以更改的，
                比如双击一个单元格，就可以修改原来的内容，
                如果想禁止用户的这种操作，让这个表格对用户只读，可以这样：
           QAbstractItemView.NoEditTriggers和QAbstractItemView.EditTrigger枚举中的一个，
           都是触发修改单元格内容的条件：
            QAbstractItemView.NoEditTriggers    0   No editing possible. 不能对表格内容进行修改
            QAbstractItemView.CurrentChanged    1   Editing start whenever current item changes.任何时候都能对单元格修改
            QAbstractItemView.DoubleClicked     2   Editing starts when an item is double clicked.双击单元格
            QAbstractItemView.SelectedClicked   4   Editing starts when clicking on an already selected item.单击已选中的内容
            QAbstractItemView.EditKeyPressed    8   Editing starts when the platform edit key has been pressed over an item.
            QAbstractItemView.AnyKeyPressed     16  Editing starts when any key is pressed over an item.按下任意键就能修改
            QAbstractItemView.AllEditTriggers   31  Editing starts for all above actions.以上条件全包括
        """
        self.setEditTriggers(QAbstractItemView.DoubleClicked)


    def setTableSelectMode(self):
        """设置表格为整行选择"""
        """
        QAbstractItemView.SelectionBehavior枚举还有如下类型
        Constant                      Value        Description
        QAbstractItemView.SelectItems   0   Selecting single items.选中单个单元格
        QAbstractItemView.SelectRows    1   Selecting only rows.选中一行
        QAbstractItemView.SelectColumns 2   Selecting only columns.选中一列
        """
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        """
        setSelectionMode(QAbstractItemView.ExtendedSelection)  #设置为可以选中多个目标
        该函数的参数还可以是：
        QAbstractItemView.NoSelection      不能选择
        QAbstractItemView.SingleSelection  选中单个目标
        QAbstractItemView.MultiSelection    选中多个目标
        QAbstractItemView.ExtendedSelection 和 ContiguousSelection
        的区别不明显，要功能是正常情况下是单选，但按下Ctrl或Shift键后，可以多选
        :return:
        """
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def addRowColumn(self):
        """动态插入行列 """
        """当初始的行数或者列数不能满足需要的时候，
        我们需要动态的调整表格的大小，如入动态的插入行：
        insertColumn()动态插入列。
        insertRow(int)、
        insertColumn(int)，指定位置插入行或者列
        """
        rowcount = self.rowCount()
        self.insertRow(rowcount)

    def removeRowColumn(self):
        """动态移除行列 """
        """
        removeColumn(int column) 移除column列及其内容。
        removeRow(int row)移除第row行及其内容。
        :return:
        """
        rowcount = self.rowCount()
        self.removeRow(rowcount-1)


    #=========第2部分：对单元格的进行设置=============
    """1.单元格设置字体颜色和背景颜色"""
    """2.设置单元格中的字体和字符大小"""
    """3.设置单元格内文字的对齐方式："""
    """4.合并单元格效果的实现："""
    """5.设置单元格的大小(见settableSize()函数)"""
    """6 单元格Flag的实现"""
    def setCellFontColor(self):
        newItem = self.item(0,1)
        newItem.setBackground(Qt.red)
        #newItem.setBackground(QColor(0, 250, 10))
        #newItem.(QColor(200, 111, 100))

    def setCellFontSize(self):
        """
        首先，先生成一个字体QFont对象，并将其字体设为宋体，大小设为12，并且加粗
        再利用单元格的QTableWidgetItem类中的setFont加载给特定的单元格。
        如果需要对所有的单元格都使用这种字体，则可以使用
        self.MyTable.setFont(testFont)
        #利用QTableWidget类中的setFont成员函数，将所有的单元格都设成该字体
        :return:
        """
        # textFont = QFont("song", 12, QFont.Bold)
        #
        # newItem = QTableWidgetItem("张三")
        # newItem.setBackgroundColor(QColor(0,60,10))
        # newItem.setTextColor(QColor(200,111,100))
        # newItem.setFont(textFont)
        # self.setItem(0, 0, newItem)
        # self.setStyleSheet("background-color: rgba(250, 250, 250, 250);""font: 11pt \"Times New Roman\";")
        self.setStyleSheet("font: 11pt \"Times New Roman\";")
        pass

    def setCellAlign(self):
        """
        这个比较简单，使用newItem.setTextAlignment()函数即可，
        该函数的参数为单元格内的对齐方式，和字符输入顺序是自左相右还是自右向左。
        水平对齐方式有：
        Constant         Value  Description
        Qt.AlignLeft    0x0001  Aligns with the left edge.
        Qt.AlignRight   0x0002  Aligns with the right edge.
        Qt.AlignHCenter 0x0004  Centers horizontally in the available space.
        Qt.AlignJustify 0x0008  Justifies the text in the available space.
        垂直对齐方式：
        Constant        Value   Description
        Qt.AlignTop     0x0020  Aligns with the top.
        Qt.AlignBottom  0x0040  Aligns with the bottom.
        Qt.AlignVCenter 0x0080  Centers vertically in the available space.
        如果两种都要设置，只要用 Qt.AlignHCenter |  Qt.AlignVCenter 的方式即可
        :return:
        """
        newItem = QTableWidgetItem("张三")
        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setItem(0, 0, newItem)

    def setCellSpan(self):
        """
        self.MyTable.setSpan(0, 0, 3, 1)
        # 其参数为： 要改变单元格的   1行数  2列数
        要合并的  3行数  4列数
        :return:
        """
        self.setSpan(0,0,3,1)

    def update_item_data(self, data):
        """更新内容"""
        self.setItem(0, 0, QTableWidgetItem(data))  # 设置表格内容(行， 列) 文字

class MyAwardTable(QTableWidget):

    lose_count = pyqtSignal(str)

    def __init__(self,parent=None):
        super(MyAwardTable,self).__init__(parent)
        self.setShowGrid(False)

        self.setTableHeader()
        self.setTableSize()
        self.setCellFontSize()
        self.setTableEditTrigger()
        self.setTableSelectMode()

    def setLoseCount(self,awardlist):
        '''连挂计数,返回字符串'''
        rlt_list = []
        for i in range(100):    #列
            count = 0
            for j in range(100):    #行
                try:
                    if awardlist[j][i]==0:
                        count +=1
                    else:
                        rlt_list.append(count)
                        count = 0
                except:
                    continue

        #最多15期连挂
        for i in range(20):
            if i==0:
                text = ' '
            else:
                text += '%s=%s '%(i,rlt_list.count(i))
        return text

    def setTableSize(self):
        """设置表格单元格尺寸"""
        #设置默认行高
        self.verticalHeader().setDefaultSectionSize(25)
        # self.verticalHeader().setHint

        #设置默认列宽
        # self.horizontalHeader().setDefaultSectionSize(40)
        #设置背景色交替
        # self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)   #设置列宽均分

    def setTableHeader(self,rowH=None,columnH=None):
        '''设置表格的表头'''
        #设置column表头名称
        if not columnH:
            columnname = ["0","1","2","3","4","5","6","7","8",
                        "9","10","11","12","13","14","15","16","17","18","19"]
        else:
            columnname = columnH
        self.setColumnCount(len(columnname))
        self.setHorizontalHeaderLabels(columnname)


        #设置row表头名称
        if not rowH:
            rowname = ['001','002','003','004','005']
        else:
            rowname = rowH
        self.setRowCount(len(rowname))
        self.setVerticalHeaderLabels(rowname)

        # 4.3 隐藏表头
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setVisible(True)
        # self.verticalHeaderItem()

        for x in range(self.columnCount()):
            #设置表头字体
            headItem = self.horizontalHeaderItem(x)  # 获得水平方向表头的Item对象
            headItem.setFont(QFont("Times New Roman",9,weight=600))
            #设置表头字体颜色
            headItem.setForeground(QBrush(Qt.blue))
            #设置表头对齐方式
            headItem.setTextAlignment(Qt.AlignHCenter)
            #设置背景色

        for x in range(self.rowCount()):
            headItem = self.verticalHeaderItem(x)
            headItem.setFont(QFont("Arial",7))
            headItem.setForeground(QBrush(Qt.blue))
            headItem.setTextAlignment(Qt.AlignLeft)

        self.horizontalHeader().setStyleSheet("background-color: rgba(250, 250, 250, 250);")

    def setTableData(self,play='cqc',ptype='3-3',award_list=None):
        '''刷新列表数据，如果刷新失败，返回False，否则返回最新期数和中奖号码'''
        #先清空表
        self.setRowCount(0)
        self.clearContents()
        dat = datetime.now().strftime('%Y%m%d')
        issue_list = []
        all_issues = AWARD.award(play,dat,num=50)   #最近50期
        #获取所有期数
        for issue in all_issues:
            issue_list.append(issue['issue'])
        current_issues = sorted(tr.current_issues,key=lambda a:a['issue'],reverse = False)
        # print(current_issues)
        # print(issue_list)
        for issue in current_issues:
            if issue['wn_number'] != '' and issue['wn_number'] !=None:
                if issue['issue'] in issue_list:
                    pass
                else:
                    temp = {}
                    temp['issue'] = issue['issue']
                    temp['wn_number'] = issue['wn_number']
                    all_issues.append(temp)
        # print(all_issues)
        #对结果进行整理
        rlt = AWARD.get_award1(all_issues,play,ptype,dat,num=50,num1=100,bet_number_list=award_list) #num1:最好的计划数

        # rlt = AWARD.get_award(play,ptype,dat,num=50,num1=30,bet_number_list=award_list)
        text = self.setLoseCount(rlt[2])
        self.lose_count.emit(text)
        if not rlt:
            self.setTableHeader()
            rowcount = self.rowCount()
            self.insertRow(rowcount)
            return False

        rows_h,column_h,data = rlt

        #设置表头
        self.setTableHeader(rows_h,column_h)

        #输入数据
        for i in range(len(data)):
            # print(data[i])
            for j in range(len(data[i])):
                self.setItem(i,j,QTableWidgetItem(str(data[i][j])))
                self.item(i,j).setFont(QFont("Times New Roman",12,weight=600))
                self.item(i,j).setTextAlignment(Qt.AlignHCenter)
                if int(data[i][j]) == 0:
                    pass
                    # self.item(i,j).setFont(QFont("Times New Roman",12,weight=600))
                    self.item(i,j).setForeground(QColor(240,0,0))
                if str(data[i][j]) in '12':
                    # self.item(i,j).setFont(QFont("Times New Roman",12,weight=600))
                    self.item(i,j).setForeground(QColor(80,70,255))
                if int(data[i][j]) >= 3:
                    pass
                    # self.item(i,j).setFont(QFont("Times New Roman",12,weight=600))
                    self.item(i,j).setForeground(QBrush(Qt.blue))
        # #底板插入一行
        # rowcount = self.rowCount()
        # self.insertRow(rowcount)
        # self.setItem()

    def setTableEditTrigger(self):
        """设置表格是否可编辑"""
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setTableSelectMode(self):
        """设置表格为整行选择"""
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.setSelectionMode(QAbstractItemView.NoSelection)

    def setCellFontSize(self):
        # self.setStyleSheet("font: 10pt \"Times New Roman\";")
        self.setStyleSheet("background-color: rgba(240, 240, 240, 250);")
        pass

class MyReportTable(QTableWidget):
    def __init__(self,parent=None):
        super(MyReportTable,self).__init__(parent)
        self.setShowGrid(True)

        self.setTableHeader()
        self.setTableSize()
        self.setCellFontSize()
        self.setTableEditTrigger()
        self.setTableSelectMode()

    def setTableSize(self):
        """设置表格单元格尺寸"""
        #设置默认行高
        self.verticalHeader().setDefaultSectionSize(30)
        #设置默认列宽
        self.horizontalHeader().setDefaultSectionSize(150)
        #设置背景色交替
        self.setAlternatingRowColors(True)

    def setTableHeader(self,rowH=None,columnH=None):
        '''设置表格的表头'''
        #设置column表头名称
        if not columnH:
            columnname = ["1","2","3","4","5","6"]
        else:
            columnname = columnH
        self.setColumnCount(len(columnname))
        self.setHorizontalHeaderLabels(columnname)

        #设置row表头名称
        if not rowH:
            rowname = []
        else:
            rowname = rowH
        self.setRowCount(len(rowname))
        self.setVerticalHeaderLabels(rowname)

        # 4.3 隐藏表头
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setVisible(True)

        for x in range(self.columnCount()):
            #设置表头字体
            headItem = self.horizontalHeaderItem(x)  # 获得水平方向表头的Item对象
            headItem.setFont(QFont("Times New Roman",14))
            #设置表头字体颜色
            headItem.setForeground(QBrush(Qt.blue))
            #设置表头对齐方式
            headItem.setTextAlignment(Qt.AlignHCenter)
            #设置背景色

        for x in range(self.rowCount()):
            headItem = self.verticalHeaderItem(x)
            headItem.setFont(QFont("Arial",10))
            headItem.setForeground(QBrush(Qt.blue))
            headItem.setTextAlignment(Qt.AlignLeft)

        self.horizontalHeader().setStyleSheet("background-color: rgba(250, 250, 250, 250);")

    def setTableData(self):
        ''''''
        #先清空表
        self.setRowCount(0)
        self.clearContents()

        #读取数据
        dat = datetime.now().strftime('%Y-%m-%d')
        # dat = '2018-06-10'
        # print(dat)
        rlt = PLAN.read_betreport(dat)
        # print(rlt)
        plans = []
        issues = []
        for plan in rlt:
            # plans.append(plan[0]+'(%s)'%plan[3])
            plans.append(plan[0])
            issues.append(plan[7])
        column_h = list(set(plans))
        column_h.sort(key=plans.index)
        # print(column_h)
        rows_h = list(set(issues))
        rows_h.sort(key=issues.index)
        # print(rep_issues)

        #设置表头
        self.setTableHeader(rows_h,column_h)

        #输入数据
        for report in rlt:
            plan_name,bet_number,issue = report[0],report[3],report[7]
            row = rows_h.index(issue)
            # column = column_h.index(plan_name+'(%s)'%bet_number)
            column = column_h.index(plan_name)
            # print((row,column))
            data = "%s[%s, %s, %s]     %s"%(report[3],report[4],report[5],report[6],report[9])
            self.setItem(row,column,QTableWidgetItem(data))
            if str(report[9])=='0':
                # self.item(row,column).setFont(QFont("Times New Roman",12,weight=600))
                self.item(row,column).setForeground(QColor(240,0,0))


        # #底板插入一行
        # rowcount = self.rowCount()
        # self.insertRow(rowcount)

    def setTableEditTrigger(self):
        """设置表格是否可编辑"""
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setTableSelectMode(self):
        """设置表格为整行选择"""
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.setSelectionMode(QAbstractItemView.NoSelection)

    def setCellFontSize(self):
        # self.setStyleSheet("font: 12pt \"Times New Roman\";")
        self.setStyleSheet("background-color: rgba(240, 240, 240, 250);""font: 12pt \"Times New Roman\";")
        pass

class QPlainTextEditLogger(logging.Handler):
    def __init__(self,parent=None):
        super(QPlainTextEditLogger,self).__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self,record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self,m):
        pass


class TimerRunner(QThread):

    issue_win_data = pyqtSignal(list)
    amount_percent_data = pyqtSignal(list)
    bet_status = pyqtSignal(int)
    login_status = False


    # scheduler = BlockingScheduler()
    scheduler = BackgroundScheduler()

    check_Email = False
    bet_free_time = True
    bet_stop_issue = 0
    current_percent = 0.0
    percent_span = [-0.9,0.1]
    current_issue = 0
    current_win = '00000'
    current_issues = []
    
    cycle_time = 30   #定时器循环时间
    time_count = 0     
    
    start_task_flag = False
    eml_flag = False
    begin = False

    def checkEmailSubject(self):
        '''检查Email的主题'''
        # subject,Date = getEmailSubject()
        check = eml.checkEmail()
        if check:
            subject,Date,content = check
            # print(subject,Date,content)

            #email是否已经写入数据库？
            if PLAN.read_email(Date):
                logging.info('-No new email')
                return
            else:
                logging.info('-Check the new email')
                pattern = re.compile(r'<div>(.*?)</div>')
                content = pattern.findall(content)
                logging.info(content)
                try:
                    content = content[0]
                    content = eval(content)
                except:
                    #如果失败，则不转换，即仍然是字符串
                    pass
                #email写入数据库
                PLAN.write_email((Date,subject,str(content)))
        else:
            return

        if subject == '重启':
            os.system('shutdown -r -t 3')

        if subject == '关机':
            eml.send_eml('远程关机',msg="远程关机！")
            os.system('shutdown -s -t 3')

        if subject =='active':
            rlt1 = PLAN.active_plan(c[0],c[1])
            rlt = PLAN.read_all_plan()

            with open("result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>激活结果：%s</div>'%rlt1
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('active result',atta="result.html")

        if subject == 'modify':
            rlt1 = PLAN.modify_plan(pset)
            rlt = PLAN.read_all_plan()

            with open("result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>修改结果：%s</div>'%(True if rlt1 else False)
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('modify result',atta="result.html")

        if subject == 'add':
            rlt1 = PLAN.add_plan(pset)
            rlt = PLAN.read_all_plan()

            with open("result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>添加结果：%s</div>'%(True if rlt1 else False)
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('add result',atta="result.html")

        if subject == 'high':
            rlt1 = PLAN.high_bet(plist)
            rlt = PLAN.read_all_plan()

            with open("result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>高倍投结果：%s</div>'%(True if rlt1 else False)
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('hith betting result',atta="result.html")

        if subject == 'myplan':
            rlt = PLAN.read_all_plan()
            with open("result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('myplan-back',atta="result.html")

        if subject == 'award':
            if '<br>' in content:
                rlt = AWARD.ptype_wn_line('cqc','前三后三',_dat,num=60,num1=15,bet_number_list=None)
            else:
                rlt = AWARD.ptype_wn_line('cqc','前三后三',_dat,num=60,num1=15,bet_number_list=content)

            with open("result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))

            eml.send_eml('award-back',atta="result.html")

    def sendEmailSubject(self,t):
        pass

    def start_task(self,play):
        '''1.获取最近中奖号码，2.更新最近5期投注结果，3.生成投注任务，4.投注，5.投注结果写入数据库'''

        self.time_count = 0 #每次循环都将计时设为0
        #1.获取所有中奖号码，和开奖期号
        self.bet_status.emit(0)
        
        result = BET.get_issue(play)   #来源1 (最近中奖号码)
        # logging.info(result)
        if not result:
            self.login_status = False
            logging.info('-Source 1 network error, switch source 2')
            dat = datetime.now().strftime('%Y%m%d')
            result = AWARD.award(play,dat)  #来源2 (每期中奖号码)
            if result:
                award_number = result[-1]    #开奖期号
                issues = result             #所有中奖号码
        else:
            self.login_status = True
            award_number = result['last_number'] #开奖期号
            issues = result['issues']   #最近5期中奖号码（可能含当期）

        if not result:
            logging.info('-Failure to win the award period！')
            self.bet_status.emit(2)     #获取开奖期号失败
            return False
        self.bet_status.emit(1)         #获取开奖期号成功
        logging.info('-Award  period：%s (%s)'%(award_number['issue'],award_number['wn_number']))
        self.current_issue = award_number['issue']
        self.current_win = award_number['wn_number']
        self.current_issues = issues
        # print(self.current_issues)
        self.issue_win_data.emit([self.current_issue,self.current_win,str(int(self.current_issue)+1)])

        #连续6期没有激活计划则关机
        if PLAN.check_shutdown(award_number['issue']):
            logging.info('-6 consecutive periods of no activation plan, shutdown')
            #重置数据库
            PLAN.bet_ok()
            #发送邮件
            eml.send_eml('betting result',msg="6 consecutive periods of no activation plan, shutdown. betting result：%s"%self.current_percent)
            #设置投注结束状态值
            PLAN.bet_status(_dat,1)   #设置状态值(已经发送邮件)
            #关机
            os.system('shutdown -s -t 30')
            return


        #处理候选投注任务
        #先将投注结果写入数据库

        PLAN.write_bet_rlt(issues)

        #3.对候选投注任务进行分析，得出最终投注任务
        plans = PLAN.analysis_plans(play,(award_number['issue'],award_number['wn_number']))
        self.bet_status.emit(3)     #成功获取投注任务
        
        #4.获取中奖金额,去刷新cookie
        #刷新失败重复3次
        for i in range(3):
            rlt = BET.refresh()
            self.login_status = rlt[0]  #登入状态
            if rlt[0]:
                self.current_percent = PLAN.money(_dat,rlt[1],award_number['issue'])
                logging.info('-Refresh cookie/amount success [Amount: %s , Percentage: %s]'%(rlt[1],self.current_percent))
                self.amount_percent_data.emit([rlt[1],self.current_percent])
                break
            else:
                logging.info('-Refresh cookie/amount failure, retry... [Percentage: %s]'%self.current_percent)
                self.amount_percent_data.emit([None,self.current_percent])
            sleep(1)

        #5.投注
        #刷新失败了也投注

        if self.percent_span[0] < self.current_percent < self.percent_span[1] :
            #当投注列表不为空时，进入投注
            if plans[0]:
                self.bet_stop_issue = 0 #只要投注了就将其置0
                bet_rlt = BET.bet(plans[0],simulation=False)  #可能是空列表,但也要传过去

                #6.投注结果写入数据库
                PLAN.after_bet(bet_rlt)
            else:
                logging.info("-Empty betting list , Not betting")
        else:
            logging.info('-Finish the task today, stop betting')
            rlt = PLAN.bet_status(_dat)   #读取状态值(是否成功发送邮件的状态值)
            if not rlt:
                #重置数据库plans(activate=0,status=0,lose=0,high_bet=1)
                PLAN.bet_ok()

                #发送邮件
                rlt = eml.send_eml('betting result',msg="betting ok stop：%s"%self.current_percent)
                if rlt:
                    #写入状态值1
                    PLAN.bet_status(_dat,1)   #设置状态值(已经发送邮件)
        self.bet_status.emit(5)     #投注成功
        #如果有挂的计划,发送邮件
        if plans[1]:
            rlt_p = PLAN.read_all_plan()

            rlt_a = AWARD.ptype_wn_line('cqc','3-3',_dat,num=60,num1=15,bet_number_list=None)
            with open("result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                for i in rlt_p:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("---------------".encode('utf-8')+b'\n')
                for i in rlt_a:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))

            eml.send_eml('betting lose',msg='there is a plan lose :%s'%str(plans[1]),atta="result.html")

    def job_1s(self):
        '''a 1 minutes play'''
        self.start_task_flag = True
        self.start()  

    def job_eml(self):
        '''a 5 minutes play'''
        self.eml_flag = True
        self.start()

    def job_change(self):
        '''to reset job time '''
        #current time
        current_time = datetime.now().strftime('%X')

        job = self.scheduler.get_job(job_id='job_10')
        if job:
            if current_time < "10:05:00":   #判断是在10点钟触发的
                logging.info('-change job_10 trigger to 10 minute')
                if job.name == 'job_10_5':
                    self.scheduler.reschedule_job('job_10',trigger='cron',minute='5-59/10')
                    job.modify(name='job_10_10')
            else:
                logging.info('-change job_10 trigger to 5 minute')
                if job.name == 'job_10_10':
                    self.scheduler.reschedule_job('job_10',trigger='cron',minute='3-59/5')
                    job.modify(name='job_10_5')
            logging.info('-change job_10 end')

    def run(self):

        if self.start_task_flag:
            self.start_task_flag = False
            self.bet_free_time = False
            logging.info('【--- job_1s --- %s -】'%datetime.now().strftime("%H:%M:%S"))
            
            self.start_task('cqc')
            self.bet_free_time = True
            
        if self.eml_flag:
            self.eml_flag = False
            self.bet_free_time = False
            logging.info('【--- job_eml --- %s -】'%datetime.now().strftime("%H:%M:%S"))

            self.checkEmailSubject()
            self.bet_free_time = True

        if self.begin:
            self.begin = False
            
            #先start
            rlt = BET.start()
            self.login_status = rlt
        
            self.scheduler.add_job(self.job_1s,'interval',seconds=self.cycle_time,max_instances=5,misfire_grace_time=1000,id='job_1s',name='job_1s')
            # self.scheduler.add_job(self.job_1s,'cron',hour='0-2,8-23',second=30,max_instances=5,misfire_grace_time=1000,id='job_1s',name='job_1s')
            self.scheduler.add_job(self.job_eml,'cron',hour='0-2,9-23',minute='3-59/10',max_instances=5,misfire_grace_time=1000,id='job_eml',name='job_eml')
            # self.scheduler.add_job(self.job_change,'cron',hour='10,22',max_instances=5,misfire_grace_time=1000,id='job_change',name='job_change') #每天10、22点整执行
            try:
                self.scheduler.start()
            except (KeyboardInterrupt,SystemExit):  #使用BlockingScheduler()时，退出时会执行except中的代码
                logging.info('clear jobs ...')
                self.scheduler.remove_all_jobs()

            #首次更新数据
            #1.获取所有中奖号码，和开奖期号
            self.bet_status.emit(0)
            result = BET.get_issue('cqc')   #来源1 (最近中奖号码)
            # logging.info(result)
            if not result:
                logging.info('-Source 1 network error, switch source 2')
                dat = datetime.now().strftime('%Y%m%d')
                result = AWARD.award('cqc',dat)  #来源2 (每期中奖号码)
                if result:
                    award_number = result[-1]    #开奖期号
                    issues = result             #所有中奖号码
            else:
                award_number = result['last_number'] #开奖期号
                issues = result['issues']   #最近5期中奖号码（可能含当期）

            if not result:
                logging.info('-Failure to win the award period！')
                self.bet_status.emit(2)     #获取开奖期号失败
                return False
            self.bet_status.emit(1)         #获取开奖期号成功
            logging.info('-Get award data：%s (%s)'%(award_number['issue'],award_number['wn_number']))

            self.current_issue = award_number['issue']
            self.current_win = award_number['wn_number']
            self.current_issues = issues
            # print(self.current_issues)
            # logging.info(self.current_issues)
            self.issue_win_data.emit([self.current_issue,self.current_win,str(int(self.current_issue)+1)])
            
            #4.获取中奖金额,去刷新cookie
            #刷新失败重复3次
            for i in range(3):
                rlt = BET.refresh()
                if rlt[0]:
                    self.current_percent = PLAN.money(_dat,rlt[1],award_number['issue'])
                    logging.info('-Refresh cookie/amount success [Amount: %s , Percentage: %s]'%(rlt[1],self.current_percent))
                    self.amount_percent_data.emit([rlt[1],self.current_percent])
                    break
                else:
                    logging.info('-Refresh cookie/amount failure, retry... [Percentage: %s]'%self.current_percent)
                    self.amount_percent_data.emit([None,self.current_percent])
                sleep(1)
            self.bet_status.emit(5)
            logging.info('-Running Success')



if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName('face')
    app.setApplicationName('face')

    log_out('./log.log')
    logging.info('\n')
    _dat = datetime.now().strftime('%Y%m%d')

    PLAN = Plan(_dat)       #要第一个实例化

    AWARD = Award()     #单独实例化
    eml = Eml()         #单独实例化
    web_name = 'www.zd222.net'
    _token,cookie_list = PLAN.read_cookies(web_name)
    BET = Bet(web_name,_token,cookie_list)


    tr = TimerRunner()

    face = face()

    # console = QPlainTextEditLogger(face.ui.Log_TableWidget)
    # logging.getLogger().addHandler(console)
    
    sys.exit(app.exec_())        

    