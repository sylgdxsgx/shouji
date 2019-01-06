import os
import sqlite3
import requests
from win32.win32crypt import CryptUnprotectData
from time import sleep

def getcookiefromchrome(host='www.zd05.net'):
    cookiepath = os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies"
    sql = "select host_key,name,encrypted_value from cookies where host_key='%s'" % host
    with sqlite3.connect(cookiepath,check_same_thread=False) as conn:
        cu = conn.cursor()
        cookies = {name:CryptUnprotectData(encrypted_value)[1].decode() for host_key,name,encrypted_value in cu.execute(sql).fetchall()}
        # print(cookies)
        return cookies
        
if __name__=="__main__":
    while(1):
        cookies = getcookiefromchrome()
        print(cookies)
        print('\n')
        sleep(5)