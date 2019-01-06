import sqlite3
import time

connect = sqlite3.connect('test.db')

conn = connect.cursor()

# plan_name text primary key,     #计划名称
# circle_time int,                #计划的循环时间（1,5,10分钟）
# activate int,                   #计划是否激活使用
# play text,                      #计划彩种类型（tx,pk10,cqc)
# plan_type text,                 #计划彩种投注类型（后一，五星）
# bet_number text,                #计划投注号码（有的是变动的需要每期都更新）
# bet_unit text,                  #计划moneyUnit
# bet_steps text,                 #计划的投注步骤（1,3,8）（2,5,8）
# bet_mult int,                   #计划投注倍数
# handup_plan text,               #使用的总体投注方式（A、B、C...)如，A:当再次中了之后，再重启计划
# handup_status text,              #handupplan的状态，-1(异常)、0(停了0期)、1(停了1期)、...
# plan_lose int,                  #计划状态，0（还未失败），1（计划挂了）
# repeat int,                     #
# high_bet int,                   #对该计划高倍投


# name text,            #计划名称
# play text,            #计划彩种类型
# ptype text,           #彩种投注类型
# bet_number text,      #投注号码
# bet_step int,         #投注第？步了
# bet_mult int,         #投注倍数
# bet_high int,         #是否高倍投注
# issue text,           #当前期号
# win_number text,      #中奖号码
# win int,              #中奖情况
# date date,            #日期
  

"""
#创建数据库
conn.execute('''CREATE TABLE plan
    (plan_name text primary key,
    circle_time int,
    activate int,
    play text,
    plan_type text,
    bet_number text,
    bet_unit text,
    bet_steps text,
    bet_mult int,
    handup_plan text,
    handup_status text,
    plan_lose int,
    repeat int,
    high_bet int)''')
    
conn.execute('''CREATE TABLE betlist
    (plan_name text,
    play text,
    ptype text,
    bet_number text,
    bet_step int,
    bet_mult int,
    bet_high int,
    issue text,
    win_number text,
    win int,
    date date,
    FOREIGN KEY (plan_name) REFERENCES plan_name(plan_name))''')


conn.execute('''CREATE TABLE email
    (DateTime text,
    Action text,
    FOREIGN KEY (DateTime) REFERENCES DateTime(DateTime))''')

connect.commit()

"""

   
"""

#插入数据
plans = [('plan1', 5, 0, 'cqc', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),
        ('plan2', 5, 0, 'cqc', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),
        ('plan3', 10, 1, 'cqc', '前三后三', '2-8', '0.010', '(1,3,8)', 1, 'B', 0, 0, 0, 1),
        ('plan4', 5, 1, 'pk', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),
        ('plan5', 5, 1, 'pk', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),
        ('plan6', 5, 1, 'pk', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),
        ('plan7', 5, 1, 'tx', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),
        ('plan8', 5, 1, 'tx', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),
        ('plan9', 5, 1, 'tx', '个位', '23478', '0.010', '(1,3,8)', 1, 'A', 0, 0, 0, 1),]
    
# conn.executemany('INSERT INTO plan VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',plans)
conn.execute("INSERT INTO plan VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",('plan1', 10, 1, 'cqc', '前三后三', '2-8', '0.010', '(1,3,8)', 1, 'C', 0, 0, 0, 1))

# betnum = [('plan1', 'cqc', '前三后三', '2-8', 1, 1, 1, '180528103', None, None, '2018-05-28'),
        # ('plan1', 'cqc', '前三后三', '2-8', 1, 1, 1, '180528103', None, None, '2018-05-28'),
        # ('plan1', 'cqc', '前三后三', '2-8', 1, 1, 1, '180528102', None, None, '2018-05-28'),]
        
# conn.executemany("INSERT INTO betlist VALUES (?,?,?,?,?,?,?,?,?,?,?)",betnum)
# connect.commit()

# report=[('plan1', 'cqc', '个位', '23478', 1, 5, 1, '180526076', None, None,time.strftime("%Y-%m-%d")),]
# conn.executemany("INSERT INTO betlist VALUES (?,?,?,?,?,?,?,?,?,?,?)",report)

connect.commit()

"""

# betnum = [('plan1', 'cqc', '前三后三', '2-8', 1, 1, 1, '180528115', None, None, '2018-05-28'),
        # ('plan1', 'cqc', '前三后三', '2-8', 1, 1, 1, '180528117', None, None, '2018-05-28'),
        # ('plan1', 'cqc', '前三后三', '2-8', 1, 1, 1, '180528116', None, None, '2018-05-28'),]
        
# conn.executemany("INSERT INTO betlist VALUES (?,?,?,?,?,?,?,?,?,?,?)",betnum)
# connect.commit()

#更新
# report=('123456',2,'plan1','180526076')
# conn.execute('UPDATE betlist SET win_number=?,win=? WHERE plan_name=? AND issue=?',report)

# conn.execute("UPDATE betlist SET bet_step=? WHERE plan_name=?",(8,'plan3'))  
# connect.commit()

#删除整张表
# conn.execute("DELETE FROM plan")
# connect.commit()


#删除表中数据
# conn.execute("DELETE FROM betlist WHERE term_number=?",('12346',))
# connect.commit()


# conn.execute('UPDATE betlist SET win_number=? WHERE play=? AND issue=?',('12345','cqc','180527093'))
# conn.execute("SELECT win_number FROM betlist WHERE play=? AND issue=?",('cqc','180527092'))
# conn.execute("SELECT ptype,bet_number FROM betlist WHERE play=?",('cqc',))
# r = conn.fetchall()
# print(r)
# print(r[0] is None)
#查询
conn.execute("UPDATE security SET token=?,cookies=? WHERE web_name=?",('23253265453','cookwefewifeww','www.zd05.net'))
connect.commit()

conn.execute("SELECT * FROM security")
for i in conn.fetchall():
    print(i)


print('\n\n')
conn.execute("SELECT * FROM plans ORDER BY plan_name")
for i in conn.fetchall():
    print(i)
print('-------------')
conn.execute("SELECT bet_step,win FROM betlist  WHERE plan_name=? AND issue=? ORDER BY plan_name,issue",('plan4','180606118'))
rlt = conn.fetchone()
print(rlt)
for i in rlt:
    print(i)
print(type(rlt[0][1]))
# print('-------------')
# conn.execute("SELECT * FROM email")
# for i in conn.fetchall():
#     print(i)
connect.close()
