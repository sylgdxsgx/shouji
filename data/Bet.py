import inspect
import sqlite3
import requests
import json
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlencode


def write_log(msg):
    msg4 = '  File"%s", line %s in %s  %s'%(inspect.stack()[2][1],inspect.stack()[2][2],inspect.stack()[2][3],inspect.stack()[2][4])
    msg2 = '  File"%s", line %s in %s  %s'%(inspect.stack()[1][1],inspect.stack()[1][2],inspect.stack()[1][3],inspect.stack()[1][4])
    # logging.info(msg4)
    # logging.info(msg2)
    logging.info('    %s [%s]'%(msg,msg2))
    logging.info('')

class Bet():

    def __init__(self,web_name,token,cookie):
        self.web_name = web_name
        self.base_url = 'https://'+self.web_name
        self.bet_home = 'https://'+self.web_name+'/home'
        self.refresh_url = 'https://'+self.web_name+'/users/refresh-amount'
        self.history_url = 'https://'+self.web_name+'/bets/bet-info'
        
        self.bet_url = {}
        self.bet_url['cqc'] = 'https://'+self.web_name+'/bets/bet/1'
        self.bet_url['tx'] = 'https://'+self.web_name+'/bets/bet/37'
        self.bet_url['pk10'] = 'https://'+self.web_name+'/bets/bet/24'

        self.issue_url = {}
        self.issue_url['cqc'] = 'https://'+self.web_name+'/bets/load-issue/1'
        self.issue_url['tx'] = 'https://'+self.web_name+'/bets/load-issue/37'
        self.issue_url['pk10'] = 'https://'+self.web_name+'/bets/load-issue/24'
        
        self.token = token
        
        self.s = requests.Session()
        
        #更新投注单元cookies
        self.moneyunit = '0.010'
        self.s.cookies.update({'lastMoneyUnit':self.moneyunit})
        
        
        #更新用户id cookies
        try:
            co = requests.cookies.RequestsCookieJar()
            for j in cookie:  #添加cookie到CookieJar
                co.set(j["name"],j["value"])
            self.s.cookies.update(co)   #更新session里的cookie
        except:
            #当cookie==False时，进入这里
            pass

        
        #session的头参数
        self.s.headers.update({'Origin':self.bet_home,\
                                'Accept':'application/json',\
                                'X-Requested-With':'XMLHttpRequest',\
                                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',\
                                'Content-Type':'application/x-www-form-urlencoded',\
                                'Referer':self.bet_url['cqc']})

        
        #期号的请求参数
        self.issue_params = {'params[0][type]':'bets','params[1][type]':'traces','_':'1527434857582'}
        
        



    def start(self):
        #cookies数据有误时，则进行登入操作，否则进行刷新操作
        if len(self.s.cookies) == 1:    #cookie只有lastMoneyUnit这个
            logging.info('-The cookies of the web site %s is INVALID'%self.web_name)
            rlt = self.login()
        else:
            logging.info("-Try refresh")
            status,msg = self.refresh()
            #刷新失败(数据过时)则登入操作
            if not status:
                logging.info('-The cookies of the web site %s is OUT OF DATE'%self.web_name)
                rlt = self.login()
            logging.info("-The cookies of the web site %s is VALID"%self.web_name)
            rlt = True
        if rlt:
            return True
        return False

            

    def analysis_plans(self,plan):
        '''生成投注数据,返回字典'''
        data = {}
        # data['name'] = plan[0]  #不能放这里
        if plan[2] in('----1','---1-','--1--','-1---','1----'):
            data['name'] = plan[0]
            data['play'] = plan[1]
            data['info'] = '%s - %s*%s*%s'%(plan[4],plan[5],plan[6],plan[7])
            data['issue'] = plan[8]
            if plan[2] =='----1':
                data['bet_str']   = '||||%s'%plan[3]
            elif plan[2] == "---1-":
                data['bet_str']   = '|||%s|'%plan[3]
            elif plan[2] == "--1--":
                data['bet_str']   = '||%s||'%plan[3]
            elif plan[2] == "-1---":
                data['bet_str']   = '|%s|||'%plan[3]
            else:
                data['bet_str']   = '%s||||'%plan[3]
                
            data['bet_num']   = len(plan[3])
            data['moneyunit'] = plan[4]
            data['multiple']  = plan[5]*plan[6]*plan[7]
            data['orders']    = 'orders[%s]'%plan[8]
            data['amount']    = 2*len(plan[3])*float(plan[4])*plan[5]*plan[6]*plan[7]
        elif plan[2] == "11111":
            data['name'] = plan[0]
            data['play'] = plan[1]
            data['info'] = '%s - %s*%s*%s'%(plan[4],plan[5],plan[6],plan[7])
            data['issue'] = plan[8]
            data['bet_str']   = '%s|%s|%s|%s|%s'%(plan[3],plan[3],plan[3],plan[3],plan[3])
            data['multiple']  = plan[5]*plan[6]*plan[7]
            data['bet_num']   = len(plan[3])*5
            data['moneyunit'] = plan[4]
            data['orders']    = 'orders[%s]'%plan[8]
            data['amount']    = 2*len(plan[3])*5*float(plan[4])*plan[5]*plan[6]*plan[7]
        elif plan[2] == "3-3":
            data['name'] = plan[0]
            data['play'] = plan[1]
            data['info'] = '%s - %s*%s*%s'%(plan[4],plan[5],plan[6],plan[7])
            data['issue'] = plan[8]
            first,second = str(plan[3]).split('-')
            matrix = ['','','','','']
            matrix[-5] += first
            matrix[-4] += first
            matrix[-3] += first
            
            matrix[-3] += second
            matrix[-2] += second
            matrix[-1] += second
            matrix_3 = list(set(matrix[-3]))
            matrix_3.sort(key=matrix[-3].index)
            matrix[-3] = ''.join(matrix_3)
            data['bet_str']   = '%s|%s|%s|%s|%s'%(matrix[0],matrix[1],matrix[2],matrix[3],matrix[4])
            data['bet_num']   = len(matrix[0])+len(matrix[1])+len(matrix[2])+len(matrix[3])+len(matrix[4])
            data['moneyunit'] = plan[4]
            data['multiple']  = plan[5]*plan[6]*plan[7]
            data['orders']    = 'orders[%s]'%plan[8]
            data['amount']    = 2*(3*len(first)+3*len(second))*float(plan[4])*plan[5]*plan[6]*plan[7]

        if data['play'] == 'cqc':
            data['gameId'] = 1
        elif data['play'] == 'tx':
            data['gameId'] = 37

        return data

    def bet(self,planlist,simulation=False):
        '''先刷新后再判断投注列表是否为空
           不为空就投注
           planlist:[['plan1', 'cqc', '后一', '23478', '0.010', 3, 5, 1, '12347'],]'''
        
        result = [] #保存结果
        
        if not planlist:
            logging.info("-The list of bets is empty , not bets！")
            return result

        for plan in planlist:
            data = self.analysis_plans(plan)

            rlt = self.send(data,simulation)
            
            plan.append(rlt)
            result.append(plan)

        return result
         
    def get_issue(self,play):
        '''返回最近5期中奖号码,以及上期中奖号码.出错则返回False'''
        try:
            r = self.s.get(self.issue_url[play],params=urlencode(self.issue_params),timeout=10)
            # logging.info('%s'%r.json())
            # logging.info('%s'%r.json()['data']['last_number'])
            
        except:
            logging.info("-Getting the issue network timeout！")
            # write_log("获取期号网络超时！")
            return False
        try:
            if r.json()['isSuccess'] == 1:
                return r.json()['data']
            else:
                return False  
        except json.decoder.JSONDecodeError as e:
            logging.info(e)
            # raise
        except:
            logging.info('-未知错误')

    def login(self):
        return self.login_2()

    def login_1(self):
        logging.info('-selenium login ...')
        options = Options()
        options.add_argument('-headless')  # 无头参数
        driver = webdriver.Firefox(firefox_options=options)
        driver.implicitly_wait(10)  # 隐性等待，最长等30秒(网页加载完成)
        loginButton = (By.ID,"loginButton")
        for i in range(3):
            # driver.get(self.base_url)
            try:
                driver.get(self.base_url)
                WebDriverWait(driver,10,0.5).until(EC.element_to_be_clickable(loginButton)) #等待登入按钮可点击为止
                _token = driver.find_element_by_name("_token").get_attribute("value")
                driver.find_element_by_id("login-name").send_keys("sylgdxsgx")
                driver.find_element_by_id("login-pass").send_keys("shi890916")
                driver.find_element_by_id("loginButton").click()
                # print(driver.current_url, driver.title, _token)
                if driver.current_url == self.bet_home: # 登入成功
                    # "往session添加cookies"
                    cookie = driver.get_cookies()
                    # print(type(cookie),cookie,'\n')
                    co = requests.cookies.RequestsCookieJar()
                    for j in cookie:  #添加cookie到CookieJar
                        co.set(j["name"],j["value"])
                    #更新session里的cookie
                    self.s.cookies.update(co)   
                    self.token = _token     #更新_token值
                    driver.quit()
                    logging.info('-selenium login success')
                    
                    #写入数据库
                    try:
                        conn = sqlite3.connect('./test.db',check_same_thread=False)
                        c = conn.cursor()
                        #先查询是否存在
                        c.execute("SELECT * FROM security WHERE web_name=?",(self.web_name,))
                        rlt = c.fetchone()
                        if rlt:
                            c.execute("UPDATE security SET token=?,cookies=? WHERE web_name=?",(_token,str(cookie),self.web_name))
                            logging.info('-update cookies(%s)...'%self.web_name)
                        else:
                            c.executemany("INSERT INTO security VALUES (?,?,?,?)",[(self.web_name,_token,str(cookie),''),])
                            logging.info('-Set cookies for the new domain (%s)...'%self.web_name)
                        conn.commit()
                        conn.close()
                        logging.info('-Cookies(%s) writes database success'%self.web_name)
                    except:
                        logging.info('-Cookies(%s)writes database failure'%self.web_name)
                    # 打开指定页面
                    # r = self.s.get(self.bet_url[play],timeout=5)
                    # print(r.request.headers)
                    # print('\n',r.cookies)

                    return (_token,cookie)
            except:
                logging.info('-selenium failure to login，retry...')
                pass
                # driver.close()
                # raise  
        try:
            driver.quit()
        except:
            pass
        logging.info('-selenium failure to login !')
        return False

    def login_2(self):
        logging.info('-selenium login ...')
        options = Options()
        options.add_argument('-headless')  # 无头参数
        driver = webdriver.Firefox(firefox_options=options)
        # driver = webdriver.Firefox()
        driver.implicitly_wait(10)  # 隐性等待，最长等30秒(网页加载完成)
        loginButton = (By.ID,"loginButton")
        for i in range(3):
            # driver.get(self.base_url)
            try:
                driver.get(self.base_url)
                WebDriverWait(driver,10,0.5).until(EC.element_to_be_clickable(loginButton)) #等待登入按钮可点击为止
                _token = driver.find_element_by_name("_token").get_attribute("value")
                driver.find_element_by_id("login-name").send_keys("sylgdxsgx")
                driver.find_element_by_id("login-pass").send_keys("shi890916")
                driver.find_element_by_id("loginButton").click()
                # print(driver.current_url, driver.title, _token)
                # print(driver.current_url,self.base_url)
                if driver.current_url == self.base_url+'/': # 登入成功,其实总是会进来
                    # "往session添加cookies"
                    cookie = driver.get_cookies()
                    # print(type(cookie),cookie,'\n')
                    co = requests.cookies.RequestsCookieJar()
                    for j in cookie:  #添加cookie到CookieJar
                        co.set(j["name"],j["value"])
                    #更新session里的cookie
                    self.s.cookies.update(co)
                    self.token = _token     #更新_token值
                    driver.quit()
                    logging.info('-selenium login success')

                    #写入数据库
                    try:
                        conn = sqlite3.connect('./test.db',check_same_thread=False)
                        c = conn.cursor()
                        #先查询是否存在
                        c.execute("SELECT * FROM security WHERE web_name=?",(self.web_name,))
                        rlt = c.fetchone()
                        if rlt:
                            c.execute("UPDATE security SET token=?,cookies=? WHERE web_name=?",(_token,str(cookie),self.web_name))
                            logging.info('-update cookies(%s)...'%self.web_name)
                        else:
                            c.executemany("INSERT INTO security VALUES (?,?,?,?)",[(self.web_name,_token,str(cookie),''),])
                            logging.info('-Set cookies for the new domain (%s)...'%self.web_name)
                        conn.commit()
                        conn.close()
                        logging.info('-Cookies(%s) writes database success'%self.web_name)
                    except:
                        logging.info('-Cookies(%s)writes database failure'%self.web_name)
                    # 打开指定页面
                    # r = self.s.get(self.bet_url[play],timeout=5)
                    # print(r.request.headers)
                    # print('\n',r.cookies)

                    return (_token,cookie)
            except:
                logging.info('-selenium failure to login，retry...')
                pass
                # driver.close()
                # raise
        try:
            driver.quit()
        except:
            pass
        logging.info('-selenium failure to login !')
        return False

    def refresh(self):
        '''返回(TRUE,amount)或者(False,Msg)'''
        try:
            r = self.s.post(self.refresh_url,data={'_token':self.token},timeout=10)     #刷新
            # logging.info('\n%s\n'%r.json())
            # print(r.json())
        except:
            return (False,"refresh-amount network timeout！")
            
        # logging.info(r.json())
        # print(r.json())
        # print(r.text)
        try:
            if r.json()['isSuccess'] == True:
                return (True,r.json()['data']['amount'])
            else:
                return (False,r.json()['Msg']+"(cookies Incorrect)")
        except:
            return (False,"refresh error,may login fail")
     
    def send(self,data,simulation=False):
        '''投注，返回0,1'''
        if not data:
            logging.info('-%s Failure to generate bets data, cancel bets！'%data['name'])
            return False
        data_cqc = {
                'gameId':data['gameId'],
                'isTrace':0,
                'traceWinStop':1,
                'traceStopValue':1,
                'balls[0][jsId]':1,
                'balls[0][wayId]':78,
                'balls[0][ball]':data['bet_str'],
                'balls[0][viewBalls]':0,
                'balls[0][num]':data['bet_num'],
                'balls[0][type]':'yixing.dingweidan.fushi',
                'balls[0][onePrice]':2,
                'balls[0][moneyunit]':data['moneyunit'],
                'balls[0][multiple]':data['multiple'],
                'balls[0][position][]':0,
                'balls[0][position][]':0,
                'balls[0][position][]':0,
                'balls[0][position][]':0,
                'balls[0][position][]':1,
                'balls[0][is_dekaron]':False,
                data['orders']:1,
                'amount':data['amount'],
                'prize':1952,
                '_token': self.token
                }

        data_cqc = urlencode(data_cqc)
        # print('\n%s\n'%data_cqc)
        if simulation:
            #模拟投注
            return True
        try:
            r = self.s.post(self.bet_url[data['play']],data=data_cqc,timeout=5)   #投注
            # print('\n投注请求cookies：\n',r.request.headers['cookie'])
            # print('投注响应cookies：\n',r.cookies)
            rlt = r.json()['isSuccess']
            if not rlt:
                logging.info("-%s Failed bets"%data['name'])
                return False
            logging.info('-%s %s phase (%s) Betting results：%s'%(data['name'],data['issue'],data['info'],r.json()))
        except:
            logging.info("-%s Betting Timeout！"%data['name'])
            return False

        # logging.info('    模拟投注成功！ %s'%data['orders'])
        return True
    
if __name__=="__main__":
    token = 'kb1QkyuIqRYHpugbhjIR4tmTqtuAhOmQi1qp0KcZ'
    cookie = 'eyJpdiI6Ik9WNDFTZUJSSXhlRzdmWWJ6RllQaEE9PSIsInZhbHVlIjoiZFBpWmhaWW5tbHZoWFd0dkx0eHhTazNTWGpYbjNDS0pUcExQZ3hUNGg3TWpIZjBuZVdqYVwvZng3VWhkUngxKzY4bjZWVkdHOGFNcUl1dnZQNFdIT0dBPT0iLCJtYWMiOiJhYzE3NWQ0YTliY2ZjMmFlNThkNGFhZDQ2MDY0YWVhNDE5MGQ2ZDk1NDEwNmIzZDZmMDA1YTNhNDRkNGUxYzdlIn0%3D'
    bet = Bet(token,cookie)

    # bet.login()