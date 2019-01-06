import os
import sys
import sqlite3
import logging
import re
from time import sleep
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from atexit import register
from data.Plan import Plan
from data.Bet import Bet
from data.Award import Award
from data.Eml import Eml


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
    # create an instance
    # logging.getLogger().addHandler(console) #实例化添加handler

    """
    # logging.config.dictConfig(codecs.open("logger.yml", 'r', 'utf-8').read())
    with open("logger.yml",'r') as f:
        logging.config.dictConfig(f.read())
    logger = logging.getLogger("billingcodeowner")
    """

def main():
    tr.run()

@register
def _out():
    logging.info('The program is going to quit (KeyboardInterrupt or SystemExit) ...')
    logging.info('Jobs: %s'%TimerRunner().scheduler.get_jobs())
    logging.info('clear jobs ...')
    TimerRunner().scheduler.remove_all_jobs()
    logging.info('Jobs: %s'%TimerRunner().scheduler.get_jobs())
    logging.info('DOWN')

    
class TimerRunner():

    # scheduler = BlockingScheduler()
    scheduler = BackgroundScheduler()
    # _dat = datetime.now().strftime('%Y%m%d')
    # plan = Plan(_dat)
    # award = Award()
    # eml = Eml()
    
    # token = 'DWJCV1roJ6E8Me7SGQjfLvO42w7CgHgPoC7A3AQ8'
    # cookie = 'eyJpdiI6IlFCZnBxWHJLcmRpYkowZnhuQ0dZOGc9PSIsInZhbHVlIjoic1E1N3Y1dHdNM1lSdmtZT283ZWJ3dGluT0ZTQzU2SDlOTGpSSGpcL3RqTWN4cEorSFBDUjdKZzdRRjJzNHp6YTJaZTd5NDVlYXFkOXc3UDk0OGNXemtnPT0iLCJtYWMiOiI5ZTM1N2VhNzYzNDg5YThiNDg0MjE1OWRjYjU5OGE0Y2Y0ZmFlZjQ1ZTRhYjVjODQ2NmY1NzQ0NmEwMDFiYTM4In0%3D'
    
    # bet = Bet(token,cookie)
    
    check_Email = False
    bet_free_time = True
    bet_stop_issue = 0
    current_percent = 0.0

    def checkEmailSubject(self):
        '''检查Email的主题'''
        # subject,Date = getEmailSubject()
        logging.info('检查Email')
        check = eml.checkEmail()
        if check:
            subject,Date,content = check
            # print(subject,Date,content)

            #email是否已经写入数据库？
            if plan.read_email(Date):
                logging.info('    No new email')
                return
            else:
                logging.info('    Check the new email')
                pattern = re.compile(r'<div>(.*?)</div>')
                content = pattern.findall(content)[0]
                try:
                    content = eval(content)
                except:
                    #如果失败，则不转换，即仍然是字符串
                    pass
                #email写入数据库
                plan.write_email((Date,subject,str(content)))
        else:
            return

        if subject == '重启':
            os.system('shutdown -r -t 3')

        if subject == '关机':
            eml.send_eml('远程关机',msg="远程关机！")
            os.system('shutdown -s -t 3')

        if subject =='active':
            rlt1 = plan.active_plan(c[0],c[1])
            rlt = plan.read_all_plan()

            with open("data/result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>激活结果：%s</div>'%rlt1
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('active result',atta="data/result.html")

        if subject == 'modify':
            rlt1 = plan.modify_plan(pset)
            rlt = plan.read_all_plan()

            with open("data/result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>修改结果：%s</div>'%(True if rlt1 else False)
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('modify result',atta="data/result.html")

        if subject == 'add':
            rlt1 = plan.add_plan(pset)
            rlt = plan.read_all_plan()

            with open("data/result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>添加结果：%s</div>'%(True if rlt1 else False)
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('add result',atta="data/result.html")

        if subject == 'high':
            rlt1 = plan.high_bet(plist)
            rlt = plan.read_all_plan()

            with open("data/result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                line = '<div>高倍投结果：%s</div>'%(True if rlt1 else False)
                f.write(line.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('hith betting result',atta="data/result.html")

        if subject == 'myplan':
            rlt = plan.read_all_plan()
            with open("data/result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
            eml.send_eml('myplan-back',atta="data/result.html")

        if subject == 'award':
            if '<br>' in content:
                rlt = award.ptype_wn_line('cqc','前三后三',_dat,num=60,num1=15,bet_number_list=None)
            else:
                rlt = award.ptype_wn_line('cqc','前三后三',_dat,num=60,num1=15,bet_number_list=content)

            with open("data/result.html" , 'wb') as f:
                f.write("<!DOCTYPE html>".encode('utf-8')+b'\n')
                f.write('<html lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>'.encode('utf-8')+b'\n')
                for i in rlt:
                    line = '<div>%s</div>'%str(i)
                    f.write(line.encode('utf-8')+b'\n')
                f.write("</body></html>".encode('utf-8'))
                
            eml.send_eml('award-back',atta="data/result.html")          

    def sendEmailSubject(self,t):
        pass
        
    def start_task(self,play):
        '''1.获取最近中奖号码，2.更新最近5期投注结果，3.生成投注任务，4.投注，5.投注结果写入数据库'''
        
        #1.获取所有中奖号码，和开奖期号
        logging.info('1. Get all the winning numbers, and the award period')
        result = bet.get_issue(play)   #来源1 (最近中奖号码)
        # logging.info(result)
        if not result:
            logging.info('    Source 1 network error, switch source 2')
            dat = datetime.now().strftime('%Y%m%d')
            result = award.award(play,dat)  #来源2 (每期中奖号码)
            if result:
                award_number = result[-1]    #开奖期号
                issues = result             #所有中奖号码
        else:
            award_number = result['last_number'] #开奖期号
            issues = result['issues']   #最近5期中奖号码（可能含当期）
        
        if not result:
            logging.info('    Failure to win the award period！')
            return False

        logging.info('    Award   period：%s (%s)'%(award_number['issue'],award_number['wn_number']))
        logging.info('    Betting period：%d '%(int(award_number['issue'])+1))
        #2.得到候选投注任务（该play，已激活，未标记为已投注）
        logging.info('2. Generating the investment task')
        plans = plan.get_cand_plan(play,award_number['issue'])
        logging.info("  2.1 List of candidate bets:%s"%str([p[0] for p in plans[1]]))
        #连续6期没有激活计划则关机
        if not plans[0]:
            if self.bet_stop_issue == 0:
                self.bet_stop_issue = int(award_number['issue']) #保存第一次么有激活计划的期号
            logging.info('    Plan to stop：issues %s'%self.bet_stop_issue)
            
            if int(award_number['issue']) - self.bet_stop_issue == 100:
                
                logging.info('    6 consecutive periods of no activation plan, shutdown')
                
                #重置数据库
                plan.bet_ok()

                #发送邮件
                eml.send_eml('betting result',msg="6 consecutive periods of no activation plan, shutdown. betting result：%s"%self.current_percent)
                
                #设置投注结束状态值
                plan.bet_status(_dat,1)   #设置状态值(已经发送邮件)
                    
                #关机
                os.system('shutdown -s -t 30')
                return
        
                
        #处理候选投注任务
        #先将投注结果写入数据库
        plan.write_bet_rlt(plans[1],issues)

        #3.对候选投注任务进行分析，得出最终投注任务
        logging.info('  2.2 Get the final betting task')
        plans = plan.analysis_plans(plans[1],(award_number['issue'],award_number['wn_number']))

        #4.获取中奖金额,去刷新cookie
        logging.info('3. Betting')
        logging.info('  3.1 Refresh the cookie/ amount')
        
        #刷新失败重复3次
        for i in range(3):
            rlt = bet.refresh()
            if rlt[0]:
                self.current_percent = plan.money(_dat,rlt[1],award_number['issue'])
                logging.info('    Refresh the success [Amount: %s , Percentage: %s]'%(rlt[1],self.current_percent))
                break
            else:
                logging.info('    Refresh the failure, retry... [Percentage: %s]'%self.current_percent)
            sleep(1)
 
        #5.投注
        #刷新失败了也投注
        
        logging.info('  3.2 Start betting')
        if -0.9 < self.current_percent < 0.30 :
            #当投注列表不为空时，进入投注
            if plans[0]:    
                self.bet_stop_issue = 0 #只要投注了就将其置0
                bet_rlt = bet.bet(plans[0])  #可能是空列表,但也要传过去

                #6.投注结果写入数据库
                plan.after_bet(bet_rlt)
            else:
                logging.info("    The list of bets is empty , Not betting")
        else:
            logging.info('    Finish the task today, stop betting')
            rlt = plan.bet_status(_dat)   #返回状态值(是否成功发送邮件的状态值)
            if not rlt:
                #重置数据库
                plan.bet_ok()

                #发送邮件
                rlt = eml.send_eml('betting result',msg="betting ok stop：%s"%self.current_percent)
                if rlt:
                    #设置投注结束状态值
                    plan.bet_status(_dat,1)   #设置状态值(已经发送邮件)
                    
        #如果有挂的计划,发送邮件
        if plans[1]:
            rlt_p = plan.read_all_plan()
        
            rlt_a = award.ptype_wn_line('cqc','前三后三',_dat,num=60,num1=15,bet_number_list=None)
            with open("data/result.html" , 'wb') as f:
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
                
            eml.send_eml('betting lose',msg='there is a plan lose :%s'%str(plans[1]),atta="data/result.html")
        
      
    def job_1s(self):
        '''a 1 minutes play'''
        self.bet_free_time = False
        logging.info('  【--- job_1s --- %s -】'%datetime.now().strftime("%H:%M:%S"))
        
        self.start_task('cqc')
        
        # self.checkEmailSubject()
        self.bet_free_time = True
        
    def job_eml(self):
        '''a 5 minutes play'''
        self.bet_free_time = False
        logging.info('job_eml --- %s -'%datetime.now().strftime("%H:%M:%S"))

        self.checkEmailSubject()
        self.bet_free_time = True
        
    def job_5(self):
        self.bet_free_time = False
        logging.info('  【--- job_5 --- %s -】'%datetime.now().strftime("%H:%M:%S"))
        
        self.start_task('cqc')
        
        # self.checkEmailSubject()
        self.bet_free_time = True
    
    def job_change(self):
        '''to reset job time '''
        #current time
        current_time = datetime.now().strftime('%X')
        
        job = self.scheduler.get_job(job_id='job_10')
        if job:
            if current_time < "10:05:00":   #判断是在10点钟触发的
                logging.info('change job_10 trigger to 10 minute')
                if job.name == 'job_10_5':
                    self.scheduler.reschedule_job('job_10',trigger='cron',minute='5-59/10')
                    job.modify(name='job_10_10')
            else:
                logging.info('change job_10 trigger to 5 minute')
                if job.name == 'job_10_10':
                    self.scheduler.reschedule_job('job_10',trigger='cron',minute='3-59/5')
                    job.modify(name='job_10_5')
            logging.info('change job_10 end')
        
    def run(self):
        # self.scheduler.add_job(self.job_5,'interval',seconds=10,max_instances=5,misfire_grace_time=1000,id='job_5',name='job_5')
        self.scheduler.add_job(self.job_1s,'cron',hour='0-2,8-23',second=30,max_instances=5,misfire_grace_time=1000,id='job_1s',name='job_1s')
        self.scheduler.add_job(self.job_eml,'cron',hour='0-2,9-23',minute='3-59/10',max_instances=5,misfire_grace_time=1000,id='job_eml',name='job_eml')
        # self.scheduler.add_job(self.job_change,'cron',hour='10,22',max_instances=5,misfire_grace_time=1000,id='job_change',name='job_change') #每天10、22点整执行
        try:
            self.scheduler.start()
        except (KeyboardInterrupt,SystemExit):  #使用BlockingScheduler()时，退出时会执行except中的代码
            logging.info('clear jobs ...')
            self.scheduler.remove_all_jobs()

        # logging.info('%s'%self.scheduler.get_jobs())
        
        num = 0
        while 1:
            num +=1
            sleep(1)

            #闲下来时(定时器未运行时)才会往下执行
            if not self.bet_free_time:
                continue
                
            #手动操作
            if num%2 == 0:
                manual_rlt = plan.read_manual()
                if not manual_rlt:
                    continue
                
                logging.info('手动操作成功')
                plan.reset_manual()
                
                play,status,status2 = manual_rlt
                if status == 1:
                    rlt = award.ptype_wn_line_local(play,'前三后三',_dat,num=60,num1=15,bet_number_list=[status2])
                    if rlt:
                        for i in rlt:
                            print(i)
        
   

      
if __name__ == "__main__":
    log_out('data/log.log')
    logging.info('\n')
    _dat = datetime.now().strftime('%Y%m%d')

    plan = Plan(_dat)
    _token,cookie_list = plan.read_cookies('www.zd111.net')
    
    bet = Bet(_token,cookie_list)
    
    award = Award()
    eml = Eml()
    tr = TimerRunner()
    main()
