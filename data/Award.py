import requests
from bs4 import BeautifulSoup
import logging
import time

class Award():

    def award(self,play,dat,num=None):
        '''输入彩种、日期、最近n期,返回已开奖期号的中奖情况，序列或者False
           如返回：[{'issue': '180602001', 'wn_number': '55248'}, {'issue': '180602002', 'wn_number': '94209'},{'issue': '180602003'},...]'''
        if play== 'cqc':
            url = 'http://caipiao.163.com/award/cqssc/%s.html'%dat
        elif play=='tx':
            url = 'http://www.dajiatiao.com/kjjl/'
        try:
            r = requests.get(url,timeout=5)
        except:
            logging.info('-Network Timeout（award)')
            return False
        
        soup = BeautifulSoup(r.text,'html.parser')
        award_list = []
        if play=='cqc':
            table = soup.table
            tds = table.find_all('td','start')
            for td in tds:
                award = {}
                try:
                    award['issue'] = td['data-period']
                    award['wn_number'] = td['data-win-number'].replace(' ','')
                    award_list.append(award)    #已开奖才加入队列
                    # award[td['data-period']] = td['data-win-number'].replace(' ','')
                except:
                    pass
                # award_list.append(award)
            rlt = sorted(award_list,key=lambda a:a['issue'],reverse = False)
        elif play=='tx':
            body = soup.body
            tds = body.find_all('div','list')
            for td in tds:
                award = {}
                try:
                    award['issue'] = td.contents[0].string
                    award['wn_number'] = td.contents[1].string.replace(',','')
                    award_list.append(award)    #已开奖才加入队列
                    # award[td['data-period']] = td['data-win-number'].replace(' ','')
                except:
                    pass
                # award_list.append(award)
            rlt = sorted(award_list,key=lambda a:a['issue'],reverse = False)
            
        if num != None:
            if num>len(rlt):
                num = len(rlt)
            rlt = rlt[-num:]
        # logging.info(rlt)
        return rlt

    def _all_issue_rlt(self,awardlist,ptype,num=15,bet_number_list=None):
        '''返回每期的中奖情况
        bet_number_list ==None时：返回最好的15个投注号码的中奖情况
        bet_number_list !=None时：返回列表中的投注号码的中奖情况，bet_number_list是一个序列'''
        # print(bet_number_list)
        issues_rlt = []
        # bet_number_list!=None时
        if bet_number_list:
            for award_dict in awardlist:
                try:
                    issue = award_dict['issue']
                    wn_number = award_dict['wn_number']
                except:
                    continue
                for bet_number in bet_number_list:
                    rlt = self._per_issue_rlt(ptype,bet_number,wn_number)
                    award_dict[bet_number] = rlt
                issues_rlt.append(award_dict)
            return issues_rlt

        # bet_number_list==None时
        temp_dict_list = []     #bet_number无值时临时保存
        count_dict = {}         #每种类型的中奖计数
        if ptype == '3-3':
            for i in range(10):
                for j in range(10):
                    number="%s-%s"%(i,j)
                    count_dict[number] = 0

            for award_dict in awardlist:
                try:
                    issue = award_dict['issue']
                    wn_number = award_dict['wn_number']
                except:
                    continue

                # temp_dict = {'issue':issue,'wn_number':wn_number,'0-0':1,'0-1':0,'0-2':2, ...}
                temp_dict = {'issue':issue,'wn_number':wn_number}
                for i in range(10):
                    for j in range(10):
                        number="%s-%s"%(i,j)
                        rlt = self._per_issue_rlt(ptype,number,wn_number)    #100次
                        temp_dict[number] = rlt
                        count_dict[number] += rlt
                temp_dict_list.append(temp_dict)

        if ptype in('----1','---1-','--1--','-1---','1----'):
            for i in range(10):
                number="%s"%i
                count_dict[number] = 0

            for award_dict in awardlist:
                try:
                    issue = award_dict['issue']
                    wn_number = award_dict['wn_number']
                except:
                    continue

                # temp_dict = {'issue':issue,'wn_number':wn_number,'0-0':1,'0-1':0,'0-2':2, ...}
                temp_dict = {'issue':issue,'wn_number':wn_number}
                for i in range(10):
                    number="%s"%i
                    rlt = self._per_issue_rlt(ptype,number,wn_number)    #100次
                    temp_dict[number] = rlt
                    count_dict[number] += rlt
                temp_dict_list.append(temp_dict)

        #筛选出15期最好的
        count_dict_sort = sorted(count_dict.items(),key=lambda x:x[1],reverse=True)
        best_list = count_dict_sort[:num]
        for i in temp_dict_list:
            temp_dict = {'issue':i['issue'],'wn_number':i['wn_number']}
            for j in best_list:
                #temp_dict的key包含issue、wn_number、以及15个投注号码
                temp_dict[j[0]] = i[j[0]]
            issues_rlt.append(temp_dict)

        return issues_rlt

    def _per_issue_rlt(self,ptype,bet_number,win_number):
        '''返回一期中奖个数:False, 0,1,2...'''
        win_rlt = 0
        if ptype == "3-3":
            try:
                first,second = str(bet_number).split('-')
                if first != second:
                    win_rlt = win_number[:3].count(first) + win_number[-3:].count(second)
                else:
                    win_rlt = win_number.count(first)
            except:
                logging.info('-Data err')
                return False
        elif ptype == "----1":
            win_rlt = bet_number.count(win_number[-1])
        elif ptype == "---1-":
            win_rlt = bet_number.count(win_number[-2])
        elif ptype == "--1--":
            win_rlt = bet_number.count(win_number[-3])
        elif ptype == "-1---":
            win_rlt = bet_number.count(win_number[-4])
        elif ptype == "1----":
            win_rlt = bet_number.count(win_number[-5])
        elif ptype == "11111":
            for i in bet_number:
                win_rlt += bet_number.count(i)
        return win_rlt

    def _ptype_wn_rlt1(self,issues,play,ptype,dat,num=None,num1=15,bet_number_list=None):
        '''每次调用该函数，返回该日期里，该投注类型的中奖情况
           play：彩种      ptype：投注类型      dat：日期      num：最近n期    bet_number：投注号码'''
        # award_list = self.award(play,dat,num)
        award_list = issues
        if not award_list:
            return False
        rlt = self._all_issue_rlt(award_list,ptype,num=num1,bet_number_list=bet_number_list)

        return rlt


    def _ptype_wn_rlt(self,play,ptype,dat,num=None,num1=15,bet_number_list=None):
        '''每次调用该函数，返回该日期里，该投注类型的中奖情况
           play：彩种      ptype：投注类型      dat：日期      num：最近n期    bet_number：投注号码'''
        #内部函数
        award_list = self.award(play,dat,num)
        if not award_list:
            return False
        rlt = self._all_issue_rlt(award_list,ptype,num=num1,bet_number_list=bet_number_list)

        return rlt

    def ptype_wn_line(self,play,ptype,dat,num=None,num1=15,bet_number_list=None):
        '''将序列转化为易看的图表'''
        #face中发邮件用到
        rlt = self._ptype_wn_rlt(play,ptype,dat,num,num1,bet_number_list)
        if not rlt:
            return False

        temp_list = []
        for i in rlt:
            if play=='tx':
                line = '-- %s (%s):| '%(i['issue'][-4:],i['wn_number'])
            else:
                line = '-- %s (%s):| '%(i['issue'][-3:],i['wn_number'])
            del i['issue']
            del i['wn_number']
            if i:
                for key,value in i.items():
                    line += "%s:&nbsp;&nbsp;&nbsp;%s|&nbsp;"%(key,value if value else '_')
                temp_list.append(line)
        return temp_list
        

    def get_award1(self,issues,play,ptype,dat,num=None,num1=15,bet_number_list=None):
        '''将序列转化为易看的图表'''
        #num:
        #num1:15个最好的计划
        rlt = self._ptype_wn_rlt1(issues,play,ptype,dat,num,num1,bet_number_list)
        # logging.info(rlt)
        if not rlt:
            return False
        # print(rlt)
        header_list = []
        issue_list = []
        award_list = []
        for i in rlt:
            if play=='tx':
                issue_list.append('%s'%i['issue'][-4:])
            else:
                issue_list.append('%s'%i['issue'][-3:])
            del i['issue']
            del i['wn_number']
            if i:
                header_list_line = []
                award_list_line = []
                for key,value in i.items():
                    header_list_line.append(key)
                    award_list_line.append(value)
                #保存header
                if not header_list:
                    header_list = header_list_line
                award_list.append(award_list_line)
        return (issue_list,header_list,award_list)

    def get_award(self,play,ptype,dat,num=None,num1=15,bet_number_list=None):
        '''将序列转化为易看的图表'''
        rlt = self._ptype_wn_rlt(play,ptype,dat,num,num1,bet_number_list)
        # logging.info(rlt)
        if not rlt:
            return False
        # print(rlt)
        header_list = []
        issue_list = []
        award_list = []
        for i in rlt:
            if play=='tx':
                issue_list.append('%s'%i['issue'][-4:])
            else:
                issue_list.append('%s'%i['issue'][-3:])
            del i['issue']
            del i['wn_number']
            if i:
                header_list_line = []
                award_list_line = []
                for key,value in i.items():
                    header_list_line.append(key)
                    award_list_line.append(value)
                #保存header
                if not header_list:
                    header_list = header_list_line
                award_list.append(award_list_line)
        return (issue_list,header_list,award_list)

if __name__=="__main__":
    from datetime import datetime
    date = datetime.now().strftime('%Y%m%d')
    award = Award()
    
    # rlt = award.ptype_wn_rlt('cqc','3-3',date,num=50,num1=15)
    # print(rlt)

    # rlt = award.get_award('cqc','3-3',date,num=50,num1=15)
    # print(rlt)

    # rlt = award.award('tx',date)
    # for i in rlt:
        # print(i)

        

