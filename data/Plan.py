import inspect
import time
import sqlite3
import logging
from datetime import datetime

def write_log(msg):
    msg4 = '  File"%s", line %s in %s  %s'%(inspect.stack()[2][1],inspect.stack()[2][2],inspect.stack()[2][3],inspect.stack()[2][4])
    msg2 = '  File"%s", line %s in %s  %s'%(inspect.stack()[1][1],inspect.stack()[1][2],inspect.stack()[1][3],inspect.stack()[1][4])
    # logging.info(msg4)
    # logging.info(msg2)
    logging.info('    %s [%s]'%(msg,msg2))
    logging.info('')
    
class Plan():
    """1、从网络获取上期期号和中奖号码
       2、从数据库中（play列表）读取出指定（或所有）计划，进行分析，修改数据库(plan:handupstatus),得出投注任务
       3、投注任务发送出去
       4、根据投注任务的执行结果，写入数据库(plan:handupstatus,betnumber)(betlist:all)
       
       程序开始时会初始化plan表，
       自动投注模式和手动投注模式(比如第一次投注)
       手动投注模式在另一个函数中"""

    def __init__(self,dat):
        self._dat = dat
        # self.conn = sqlite3.connect('data/test.db',check_same_thread=False)
        self.conn = sqlite3.connect('./test.db',check_same_thread=False)
        
        self.c = self.conn.cursor()
        
        self.play = ['cqc','pk10','tx']
        self.btype = ['----1','---1-','--1--','-1---','1----','11111','3-3']  #投注类型
        #总计划规则,如，A：挂了也继续开始，B：挂后，停一期，再开始，C：挂后，停二期，再开始，D：挂后，停三期，再开始，E：挂后，等待中一期后再开始。
        self.handup_plan = ['A','B','C','D','E']
        self.betUnit = ['0.010','0.1']

        self.resetdata()
        
    def active_plan(self,pname,action):
        '''激活计划 '''
        try:
            self.c.execute("UPDATE plans SET activate=? WHERE plan_name=?",(action,pname))
            self.conn.commit()
            logging.info("-Activate Plan Success")
        except:
            logging.info("-Activate Plan Failure")
            return False
        return True

    def add_plan(self,pset):
        '''添加计划,返回计划名  False'''
        self.c.execute("SELECT plan_name FROM plans WHERE plan_name=?",(pset[0],))
        plan_name = self.c.fetchone()
        if plan_name:
            logging.info('-The plan already exists, please rename')
            return False

        p_list = [pset]
        try:
            self.c.executemany("INSERT INTO plans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",p_list)
            self.conn.commit()
        except:
            logging.info("-Add plan %s failure"%pset[0])
            return False
        logging.info('-Add plan %s success'%pset[0])
        return pset[0]

    def add_plan_from_award(self,play,ptype,betnumber,issue,activate,high,stop_in_wn):
        '''从award添加计划'''

        #读取出未激活的计划
        self.c.execute("SELECT * FROM plans WHERE circle_time<>? AND activate=?",(1,0))
        plans = self.c.fetchall()
        add_ok = 0
        if plans:   #如果有未激活的计划
            #修改计划
            for plan in plans:
                # logging.info("check %s"%plan[0])
                new_plan = plan[0]
                if not plan[9] :    #如果期号为空
                    logging.info("-change %s because bet_issue='%s'"%(plan[0],plan[9]))
                    try:    #修改该计划
                        self.c.execute("UPDATE plans SET circle_time=?,activate=?,play=?,plan_type=?,status=?,lose=?,lose_issue=?,bet_number=?,high_bet=?,stop_in_wn=? WHERE plan_name=?",(1,activate,play,ptype,0,0,"0",str(betnumber),high,stop_in_wn,new_plan))
                        self.conn.commit()
                        add_ok=1
                        break
                    except:
                        logging.info("-change %s as new plan failed"%plan[0])
                elif int(plan[9])+3 < int(issue):    #如果有超过2期没有投注了，且不是E计划
                    #circle_time=1表示新增的
                    before_tx = 'activate=%s,bet_issue=%s,bet_number=%s,bet_mult=%s,high_bet=%s,stop_in_wn=%s'%(plan[2],plan[9],plan[10],plan[13],plan[14],plan[15])
                    after_tx = 'circle_time=%s,activate=%s,play=%s,plan_type=%s,status=%s,lose=%s,lose_issue=%s,bet_number=%s,bet_mult=%s,high_bet=%s,stop_in_wn=%s'%(1,activate,play,ptype,0,0,"0",str(betnumber),plan[13],high,stop_in_wn)
                    logging.info("-change %s [%s] --> [%s]"%(plan[0],before_tx,after_tx))
                    try:
                        self.c.execute("UPDATE plans SET circle_time=?,activate=?,play=?,plan_type=?,status=?,lose=?,lose_issue=?,bet_number=?,high_bet=?,stop_in_wn=? WHERE plan_name=?",(1,activate,play,ptype,0,0,"0",str(betnumber),high,stop_in_wn,new_plan))
                        self.conn.commit()
                        add_ok=1
                        break
                    except:
                        logging.info("-change %s failed!!"%plan[0])
        if not add_ok:
            #新增计划
            self.c.execute("SELECT plan_name FROM plans")    #读出所有的计划名
            plannames = self.c.fetchall()
            max_name = 0
            for planname in plannames:
                name = planname[0]
                name = int(name[4:])
                max_name = name if name>max_name else max_name
            new_plan = 'plan%d'%(max_name+1)
            try:
                p_list=[(new_plan,1,activate,play,ptype,"A",0,0,"","",betnumber,self.betUnit[0],"(1,4,11)",1,high,stop_in_wn),]
                self.c.executemany("INSERT INTO plans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",p_list)
                self.conn.commit()
                logging.info("-add %s from award seccess %s"%(new_plan,str(p_list)[0]))
            except:
                logging.info("-add %s from award failed!!"%new_plan)

        else:
            logging.info("-change %s from award seccess"%new_plan)


    def analysis_plans(self,play,award_number):
        '''分析每个候选的plan的投注情况，返回投注任务列表，投注成功后或者判定为不投注时要更新bet_issue'''
        planlist = self.get_cand_plan(play,award_number[0])[1]
        bet_list = []       #保存投注任务
        lose_list = []      #保存挂的计划
        for plan in planlist:
            # print(plan)
            new_step = 0    #将要投的注数为0，即先设置为不投注
            bet_steps = eval(plan[12])

            #该计划可能上期投注了，也可能没有投注
            #bet_issue只是标记投注情况，并不是真正的投注了，是否真正投注要看betlist库
            #从betlist中读取投注情况(投注步数和中奖情况)
            self.c.execute("SELECT bet_step,win FROM betlist WHERE plan_name=? AND issue=?",(plan[0],award_number[0]))
            step_win = self.c.fetchone()  #如果数据库中没有[网络上期]投注记录(没有投注)，则返回None

            #处理结果2种：1.获取这期的投注计划，不更新bet_issue，2.这期不投注，只更新bet_issue
            
            #当上期投注时:
            if step_win:
                #如果中奖了
                if step_win[1]: #即中奖了
                    new_step = bet_steps[0]        #读取第一步注数

                #如果没有中奖
                else:
                    #获取当前步
                    step=step_win[0]
                    for i in range(len(bet_steps)):
                        if bet_steps[i]==step:
                            break
                    #是最后一步
                    if i == len(bet_steps)-1:    #是最后一步,即计划挂了
                        #先写数据库
                        logging.info('-changging database (plans):[%s]'%str(plan))
                        self.c.execute("UPDATE plans SET lose=?,lose_issue=? WHERE plan_name=?",(1,award_number[0],plan[0]))         #更新挂状态
                        # self.c.execute("UPDATE plans SET high_bet=? WHERE plan_name=?",(1,plan[0]))    #停止高倍投
                        self.conn.commit()
                        logging.info('-changged database (plan):[%s, lose=%s, lose_issue=%s]'%(plan[0],1,award_number[0]))
                        #再判断是否投注
                        if plan[5] == self.handup_plan[0]:   #A：挂了也继续开始
                            new_step = bet_steps[0]        #读取第一步注数
                        
                        #保存挂计划
                        lose_list.append(plan)
                    #不是最后一步
                    else:
                        new_step = bet_steps[i+1]

            #当上期没有投注时(不能用plan[9]了，因为可能plan[9]=0）:
            else:
                #1.异常
                if plan[6] == -1:   #status=-1
                    #先什么也不做
                    pass

                #2.首次投注
                elif not plan[9]:   #plan[9]为空时
                    new_step = bet_steps[0]        #读取第一步注数

                elif plan[9] < award_number[0]:
                    new_step = bet_steps[0]        #读取第一步注数

                #3.挂停了  (plan[9]=award_number[0]，因为挂停了会更新bet_issue)
                elif plan[7] == 1:
                    #挂了几期？
                    if plan[8][:6] == plan[9][:6]:
                        lose_num = int(plan[9]) - int(plan[8])
                    else:
                        lose_num = 120 - int(plan[8][-3:]) + int(plan[9][-3:])
                    #本期是否可以投注？
                    if plan[5] == self.handup_plan[0]:   #A：挂了也继续开始,(这里不可能执行)
                        new_step = bet_steps[0]        #读取第一步注数
                    elif plan[5] == self.handup_plan[1]: #B：挂后，停一期，再开始
                        if lose_num >= 1:
                            new_step = bet_steps[0]        #读取第一步注数
                    elif plan[5] == self.handup_plan[2]: #C：挂后，停二期，再开始
                        if lose_num >= 2:
                            new_step = bet_steps[0]        #读取第一步注数
                    elif plan[5] == self.handup_plan[3]: #D：挂后，停三期，再开始
                        if lose_num >= 3:
                            new_step = bet_steps[0]        #读取第一步注数
                    elif plan[5] == self.handup_plan[4]: #E：挂后，等待中一期后再开始
                        win_rlt = self.judeg_win(plan[3],plan[4],plan[10],award_number[1])
                        if win_rlt :
                            new_step = bet_steps[0]        #读取第一步注数
                    else:
                        pass
                #挂停了，但手动修改lose=0
                elif plan[7] == 0:
                    new_step = bet_steps[0]        #读取第一步注数

            #生成投注任务
            if new_step:
                #1.获取这期的投注计划，不更新bet_issue(投注完成才会更新)
                #[planname,play,ptype,betnumber,betunit,new_step,betmult,highbet,current_issue]
                issue = self.new_bet_issue(plan[0],award_number[0])
                result = [plan[0],plan[3],plan[4],plan[10],plan[11],new_step,plan[13],plan[14],issue]
                bet_list.append(result)
            else:
                #2.这期不投注，只更新bet_issue
                issue = self.new_bet_issue(plan[0],award_number[0])
                self.write_bet_issue(plan[0],issue)

        # logging.info("    第%s +1 期，投注任务："%award_number[0])
        for i in bet_list:
            logging.info("-Betting task:  %s"%i)
        return (bet_list,lose_list)
       
    def after_bet(self,rlt_list):
        '''投注成功后，更新数据库
           rlt_list:[['plan1', 'cqc', '个位', '23478', '0.010', 1, 5, 1, '180526076', True], ]
        '''
        pass
        # logging.info(rlt_list)
        for plan in rlt_list:
            if plan[-1]:        #最后一位为投注结果,投注成功
                #更新plans表
                self.c.execute("UPDATE plans SET lose=? WHERE plan_name=?",(0,plan[0]))         #更新挂状态
                self.c.execute("UPDATE plans SET status=? WHERE plan_name=?",(0,plan[0]))     #更新停状态
                self.c.execute("UPDATE plans SET bet_issue=? WHERE plan_name=?",(plan[8],plan[0]))  #更新投注期号
                self.c.execute("UPDATE plans SET bet_number=? WHERE plan_name=?",(plan[3],plan[0]))  #更新投注号码
                self.conn.commit()
                logging.info("-changged database (plans):[%s, status=%s, lose=%s, bet_issue=%s, bet_number=%s]"%(plan[0],0,0,plan[8],plan[3]))

                #更新betlist
                report = [(plan[0],plan[1],plan[2],plan[3],plan[5],plan[6],plan[7],plan[8],None,None,time.strftime("%Y-%m-%d")),]
                logging.info("-add to database (betlist):%s"%str(report[0]))
                self.c.executemany("INSERT INTO betlist VALUES (?,?,?,?,?,?,?,?,?,?,?)",report)
                self.conn.commit()
 
    def bet_status(self,dat,n=None):
        '''设置/返回投注状态值'''
        if n !=None:
            self.c.execute("UPDATE status SET status=? WHERE date_time=?",(n,dat))
            self.conn.commit()
            return True
        else:
            self.c.execute("SELECT * FROM status WHERE date_time=?",(dat,))
            status = self.c.fetchone()
            return status[6]

    def bet_ok(self):
        '''投注结束设置,重置数据'''
        self.c.execute("UPDATE plans SET circle_time=?,activate=?,status=?,lose=?,high_bet=?",(0,0,0,0,1))
        self.conn.commit()

    def check_shutdown(self,issue):
        '''连续6期没有投注则关机'''
        #读取激活的计划
        self.c.execute("SELECT plan_name,activate,bet_issue FROM plans WHERE activate=?",(1,))
        plans = self.c.fetchall()
        for plan in plans:
            planname,activate,bet_issue = plan
            if int(issue) -6 >=int(bet_issue) if bet_issue else 0:
                return False    #先不实现
        return False

    def get_cand_plan(self,play,award_issue):
        '''得到候选投注任务（该play，已激活，未标记为已投注,stop_in_wn>0）'''
        #读取所有的计划
        # plans = self.read_all_plan()
        self.c.execute("SELECT * FROM plans WHERE play=? AND activate=?",(play,1))
        plans = self.c.fetchall()
        
        plan_list = []  #保存候选投注任务
        
        #当没有激活计划时
        if not plans:
            logging.info('-No active plan')
            return (0,plan_list)    
            
        #每个计划轮询分析
        for plan in plans:

            #筛选未标记为已投注的计划
            #1、首次投注（plan[9]=0或者=''）
            #2、上期投注情况正常记录（plan[9]=award_number['issue']）
            #2.1、上期投注情况正常记录，但可能status=-1。
            #2.2、上期投注情况正常记录，但可能lose=1。
            # if award_issue != plan[9] and plan[9] != '0' and plan[9] !='':
            #     continue
            if plan[9]:
                if award_issue < plan[9] :
                    continue
            else:
                #bet_issue为空时
                pass

            #再筛选出stop_in_wn>0的计划
            if int(plan[-1])<=0:
                continue

            #投注任务
            plan_list.append(plan)  #将整个plan保存起来
        # logging.info("    %s"%str([plan[0] for plan in plan_list]))
        return (1,plan_list)

    def get_active_betnumber(self):
        '''获取激活的计划的bet_number'''
        self.c.execute("SELECT bet_number FROM plans WHERE activate=?",(1,))
        bet_numbers = self.c.fetchall()
        bet_numList = []
        for bet_number in bet_numbers:
            bet_numList.append(bet_number[0])
        return bet_numList

    def get_beted_report(self,dat):
        '''查询投注记录'''
        self.c.execute("SELECT * FROM betlist WHERE date=? ORDER BY issue",(dat,))
        report = self.c.fetchall()
        return report

    def high_bet(self,pset):
        '''高倍投注'''
        if len(pset) == 2:
            self.c.execute("UPDATE plans SET high_bet=? WHERE plan_name=?",(pset[1],pset[0]))
            self.conn.commit()
        return True

    def judeg_win(self,play,ptype,bet_number,win_number):
        '''判断计划规则是否中奖,中奖则返回1,2,3,... (一注中可能中多个奖) ,不中奖则返回0
           为什么是判断计划(plan)呢，而不是判断投注列表(betlist)呢？因为betlist中没有bet_number，而是在plan中
           所以每次投注后，计划(plan)都要更新一遍（主要更新投注号码，和handupstatus）
           怎么判断呢？通过betlist中记录的最后投注期号和plan中的bet_number，以及网络的上期期号和中奖号码来判断
           如果bet=None,则未投注该[网络上期]，如果bet!=None,则投注了
        '''

        #根据play,ptype,betnumber和生成投注矩阵
        if play in self.play:   #('tx','pk10','cqc')
            win_rlt = 0
            if ptype == self.btype[6]:  #"3-3"
                first,second = str(bet_number).split('-')
                if first != second:
                    win_rlt = win_number[:3].count(first) + win_number[-3:].count(second)
                else:
                    win_rlt = win_number.count(first)
            elif ptype == self.btype[0]:     #"----1"
                win_rlt = bet_number.count(win_number[-1])
            elif ptype == self.btype[1]:    #"---1-"
                win_rlt = bet_number.count(win_number[-2])
            elif ptype == self.btype[2]:    #"--1--"
                win_rlt = bet_number.count(win_number[-3])
            elif ptype == self.btype[3]:    #"-1---"
                win_rlt = bet_number.count(win_number[-4])
            elif ptype == self.btype[4]:    #"1----"
                win_rlt = bet_number.count(win_number[-5])
            elif ptype == self.btype[5]:    #"11111"
                for i in bet_number:
                    win_rlt += bet_number.count(i)
            else:
                pass
            return win_rlt
        else:
            return 0

    def modifyPlan(self,list):
        '''根据计划名称，修改计划，一次修改一个数据'''
        plan_name,column,text = list
        title = ['plan_name','circle_time','activate','play','plan_type','handup_plan','status','lose','lose_issue',
                 'bet_issue','bet_number','bet_unit','bet_steps','bet_mult','high_bet','stop_in_wn']

        js = "UPDATE plans SET %s=? WHERE plan_name=?"%title[int(column)]
        try:
            self.c.execute(js,(int(text) if int(column) in (1,2,6,7,13,14,15) else text,plan_name))
            #只要有动作，则更新circle_time=0
            # self.c.execute("UPDATE plans SET circle_time=? WHERE plan_name=?",(0,plan_name))
            self.conn.commit()
            logging.info('-modify the plan [%s, column=%s, value=%s] successfully'%(list[0],list[1],list[2]))
        except:
            logging.info('-modify the plan [%s, column=%s, value=%s] failure'%(list[0],list[1],list[2]))
            # raise
            return False
        return plan_name

    def modify_plan(self,pset):
        '''修改计划  只有传入的字段非空才被修改'''
        try:
            if pset[1] != '':
                self.c.execute("UPDATE plans SET circle_time=? WHERE plan_name=?",(pset[1],pset[0]))
            if pset[2] != '':
                self.c.execute("UPDATE plans SET activate=? WHERE plan_name=?",(pset[2],pset[0]))
            if pset[3] != '':
                self.c.execute("UPDATE plans SET play=? WHERE plan_name=?",(pset[3],pset[0]))
            if pset[4] != '':
                self.c.execute("UPDATE plans SET plan_type=? WHERE plan_name=?",(pset[4],pset[0]))
            if pset[5] != '':
                self.c.execute("UPDATE plans SET handup_plan=? WHERE plan_name=?",(pset[5],pset[0]))
            if pset[6] != '':
                self.c.execute("UPDATE plans SET status=? WHERE plan_name=?",(pset[6],pset[0]))
            if pset[7] != '':
                self.c.execute("UPDATE plans SET lose=? WHERE plan_name=?",(pset[7],pset[0]))
            if pset[8] != '':
                self.c.execute("UPDATE plans SET lose_issue=? WHERE plan_name=?",(pset[8],pset[0]))
            if pset[9] != '':
                self.c.execute("UPDATE plans SET bet_issue=? WHERE plan_name=?",(pset[9],pset[0]))
            if pset[10] != '':
                self.c.execute("UPDATE plans SET bet_number=? WHERE plan_name=?",(pset[10],pset[0]))
            if pset[11] != '':
                self.c.execute("UPDATE plans SET bet_unit=? WHERE plan_name=?",(pset[11],pset[0]))
            if pset[12] != '':
                self.c.execute("UPDATE plans SET bet_steps=? WHERE plan_name=?",(pset[12],pset[0]))
            if pset[13] != '':
                self.c.execute("UPDATE plans SET bet_mult=? WHERE plan_name=?",(pset[13],pset[0]))
            if pset[14] != '':
                self.c.execute("UPDATE plans SET high_bet=? WHERE plan_name=?",(pset[14],pset[0]))
            if pset[15] != '':
                self.c.execute("UPDATE plans SET stop_in_wn=? WHERE plan_name=?",(pset[15],pset[0]))
            self.conn.commit()
            logging.info('-modify the plan successfully')
        except:
            logging.info('-modify the plan failure')
            return False
        return pset[0]

    def money(self,dat,amount,issue):
        '''将投注金额写入数据库，返回百分比'''
        self.c.execute("SELECT * FROM status WHERE date_time=?",(dat,))
        status = self.c.fetchone()
        percent = 0.0
        if status :
            percent = (float(amount) - status[2])/status[2]
            if status[3] != issue:
                self.c.execute("UPDATE status SET current_issue=?,current_money=?,percent=? WHERE date_time=?",(issue,float(amount),percent,dat))
                self.conn.commit()
        else:
            self.c.execute("INSERT INTO status VALUES (?,?,?,?,?,?,?)",(dat,issue,float(amount),None,None,None,0))
            self.conn.commit()
        # percent = 0.21
        return percent

    def new_bet_issue(self,planname,old_issue):
        '''得出新的bet_issue '''
        dat = datetime.now().strftime('%y%m%d') #如：180608
        if len(old_issue) == 9:   #是重庆彩
            bet_issue = str(int(old_issue)+ 1) if old_issue[-3:]!='120' else dat+'001'
        elif len(old_issue) == 10:  #分分彩
            bet_issue = str(int(old_issue)+ 1) if old_issue[-4:]!='1440' else dat+'0001'
        else:
            bet_issue = str(int(old_issue)+ 1)    #先这样写

        return bet_issue

    def read_all_plan(self,play=None):
        '''通过彩种类型,读取所有计划，返回所有的计划字段'''
        if play:
            self.c.execute("SELECT * FROM plans WHERE play=?",(play,))
        else:
            self.c.execute("SELECT * FROM plans")
        all_plan = self.c.fetchall()
        return all_plan
    def read_betreport(self,dat,plan_name=None):
        '''根据时间和计划名读取记录'''
        if plan_name:
            self.c.execute("SELECT * FROM betlist WHERE date=? AND plan_name=?",(dat,plan_name))
        else:
            self.c.execute("SELECT * FROM betlist WHERE date=? ORDER BY issue",(dat,))
        all_report = self.c.fetchall()
        return all_report

    def read_cookies(self,web_name):
        '''读取指定网站的_token、cookies，返回(_token,cookies)'''
        self.c.execute("SELECT token,cookies FROM security WHERE web_name=?",(web_name,))
        try:
            _token,cookie_list = self.c.fetchone()[:2]
            
        
            if cookie_list:
                try:
                    cookie_list = eval(cookie_list)
                except:
                    logging.info('-cookies Formatting error')
                    return False,False
            # rlt = eval(rlt)
            return (_token,cookie_list)
        except:
            logging.info('-Database read cookies failure')
            return False,False
        
        
    def read_email(self,dt):
        '''读取邮件'''
        self.c.execute("SELECT * FROM email WHERE DateTime=?",(dt,))
        rlt = self.c.fetchone()
        return rlt
    
    def read_manual(self):
        '''读取列表进行操作'''
        self.c.execute("SELECT * FROM manual")
        rlts = self.c.fetchall()
        for rlt in rlts:
            if rlt[1] != 0:
                return rlt
        return 0
        
    def reset_manual(self,play=None):
        try:
            if play:
                self.c.execute("UPDATE manual SET query=0 WHERE play=?",(play,))
            else:
                self.c.execute("UPDATE manual SET query=0")
            self.conn.commit()
        except:
            logging.info('-Write <manual> database failure')
            return False
        return True
            
    def resetdata(self):
        '''重置数据库'''
        pass
        self.bet_status(self._dat,0)

    def save_cookies(self,web_name,token,cookie_list):
        '''每次登入成功后都把_token、cookie保存,传进来的是一个列表'''
        cookies = str(cookie_list)
        self.c.execute("UPDATE security SET token=?,cookies=? WHERE web_name=?",(token,cookies,web_name))
        self.conn.commit()
        
        
    def write_bet_issue(self,planname,issue):
        '''将新的bet_issue写入数据库中'''
        self.c.execute("UPDATE plans SET bet_issue=? WHERE plan_name=?",(issue,planname))  #更新投注号码
        self.conn.commit()
        logging.info("-changged database (plans):[%s, bet_issue=%s]"%(planname,issue))

    def write_email(self,email):
        '''写入数据库'''
        email_list = [email,]
        try:
            self.c.executemany("INSERT INTO email VALUES (?,?,?)",email_list)
            self.conn.commit()
        except:
            logging.info('-Write <email> database failure')
            return False
        return True
 
    def write_bet_rlt(self,issues):
        '''把最近5期的中奖号码和中奖情况写入数据库,issues为一个数组'''
        logging.info('-Renew databases')
        #更新betlist
        #更新plans.若是中奖了：1.stop_in_wn - 1,    2.若stop_in_wn=0则，active=0

        #先读取所有的计划,包括未激活的计划（人为操做关闭的计划）
        self.c.execute("SELECT * FROM plans")
        plans = self.c.fetchall()
        # print(plans)
        for plan in plans:
            for issue in issues:
                self.c.execute("SELECT ptype,bet_number,win_number FROM betlist WHERE plan_name=? AND play=? AND issue=?",(plan[0],plan[3],issue['issue']))
                rlt = self.c.fetchall()
                if not rlt:     #如果是空的
                    # print(plan[0],'查询为空',issue['issue'])
                    continue
                for i in rlt:
                    ptype,betnumber,winnumber = i
                    if winnumber == None and issue['wn_number']:    #如果还没有写入，则写入
                        win_rlt = self.judeg_win(plan[3],ptype,betnumber,issue['wn_number'])
                        self.c.execute('UPDATE betlist SET win_number=?,win=? WHERE plan_name=? AND play=? AND issue=? AND ptype=? AND bet_number=?',(issue['wn_number'],win_rlt,plan[0],plan[3],issue['issue'],ptype,betnumber))
                        self.conn.commit()
                        logging.info('-changged database (betlist):[%s, %s, %s, %s, %s]'%(plan[0],issue['issue'],betnumber,issue['wn_number'],win_rlt))
                        if win_rlt: #如果中奖了
                            if plan[15]>1:    #stop_in_wn>1时
                                activate,high_bet,stop_in_wn = (1,1,int(plan[15])-1)
                            elif plan[15]<=1:
                                activate,high_bet,stop_in_wn = (0,1,0)
                            else:
                                activate,high_bet,stop_in_wn = (0,1,0)
                            #更新计划的circle_time、activate、high_bet、stop_in_wn
                            self.c.execute('UPDATE plans SET circle_time=?,activate=?,high_bet=?,stop_in_wn=? WHERE plan_name=?',(0,activate,high_bet,stop_in_wn,plan[0]))
                            self.conn.commit()
                            logging.info('-changged database (plans):[%s, activate=%s, high_bet=%s, stop_in_wn=%s]'%(plan[0],activate,high_bet,stop_in_wn))
                    else:
                        pass

                    
        
                
                
        
if __name__=="__main__":
    _dat = datetime.now().strftime('%Y%m%d')
    plan = Plan(_dat)
    # plan.save_cookies('www.zd111.net','ffh ff2',[])
    # rlt = plan.read_cookies('www.zd111.net')
    rlt = plan.read_all_plan()
    print(rlt)
