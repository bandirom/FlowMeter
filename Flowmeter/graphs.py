import numpy as np
from matplotlib import pylab
import shelve # bin
import matplotlib.pyplot as plt
import numpy as np
import pymysql, pymysql.cursors # database
from datetime import datetime
from time import sleep
import logging
import shelve
from cryptography.fernet import Fernet
import matplotlib.dates as mdates
from datetime import datetime, date, time
import datetime as d
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
class DataBase(object):
    db = None
    def __new__(self,*args, **kwargs):           # класса db
        if self.db is None:               # Если он еще не создан, то
            self.db = object.__new__(self,*args, **kwargs) # вызовем __new__ родительского класса
        return self.db                    # вернем db

    def __init__(self, *args, **kwargs):
        print("init db")

        try:
            self.read_data()
            self.connect_to_db()
        except Exception as e:
            print(e)

    def read_data(self):
         with shelve.open("data") as data:
            key = data["key"]
            self.user = data[data["login"]]
            password = data["pass"]
         cipher = Fernet(key)
         self.password = cipher.decrypt(password).decode("utf-8") 

    def connect_to_db(self):
        self.connection = pymysql.connect(host='localhost',
                             user=self.user,
                             password=self.password,
                             db='flowmeter',
                             charset='utf8mb4',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)
        print ("connect successful!!")
    
    def get_data(self, D, F=False,T=False):
        print(D,F,T)
        if F:
            try:
                with self.connection.cursor() as cursor:
                    n=self.counter()
                    F_data = []
                    D_data = []
                    sql = "SELECT F, D FROM data WHERE D > {} AND D < {} ".format(D.strftime("'%Y-%m-%d 00:00:00'"),D.strftime("'%Y-%m-%d 23:59:59'"))
                    cursor.execute(sql)
                    numb = cursor.execute(sql) - 1
                    for row in cursor:
                        n()
                        result = cursor.fetchone()
                        F_data.append(result["F"])
                        D_data.append(result["D"].strftime("%H:%M:%S"))#%Y-%m-%d
                        if n() == numb:
                            break      
                return F_data, D_data
            except Exception as e:
                print("Error get data", e)

    def counter(self):
        num = 0
        def incrementer():
            nonlocal num
            num += 1
            return num
        return incrementer

    def insert_data(self,data):
        F,T = data[0],data[1]
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO data (F,T,D) VALUES (%s,%s,now())" #
                cursor.execute(sql,(F,T))
                print("Data was inserted to db")
        except Exception as e:
            print("Error to insert data",e)   
    
    def __del__(self):
        print("connection close")
        self.connection.close()


class Graphics(object):
    gr = None
    def __new__(self,*args, **kwargs):           # класса Root
        if self.gr is None:               # Если он еще не создан, то
            self.gr = object.__new__(self,*args, **kwargs) # вызовем __new__ родительского класса
        return self.gr                    # вернем root

    def __init__(self):
        print("init gr") #, date, T,F

    def create_chart(self,date, F_check, T_check):
        db = DataBase()
        self.date = date
        self.F, self.D = [], []
        self.F,self.D = db.get_data(D = date, F=F_check, T = T_check)
        self.build_chart()

    def build_chart(self):
        #F = np.array(self.F)
        #D = np.array(self.D)#, dtype='datetime64'
        t = time(00, 00)
        dt=datetime.combine(self.date, t)
       #dt = datetime.strptime("00:00", "%H:%M")
       #plt.xticks(range(0,24,2),[str(i)+':00' for i in range(0,24,3)],rotation=90 )
        x = [dt + d.timedelta(hours=i) for i in range(24)]
        #print(x)
        
        plt.title('Instant flow chart', fontsize=16, y=1.05) # заголовок
        plt.axhline(800, color = 'red', linestyle='--') # доп гориз линия
        plt.xlabel('Time', fontsize=14) # название оси х
        plt.ylabel('Instant flow',fontsize=16) # название оси у
        plt.plot(self.D,self.F, label = "Instant flow") # график
        plt.xticks(rotation=45 , fontsize= 6) #range(0,24),labels = [str(i)+':00' for i in range(0,24)],
        #plt.ylim(0,120) # максимальное значение на оси у
        #plt.xlim('0:00','24:00')
        plt.legend(loc='best') # надпись на графике
        plt.grid()   # линии вспомогательной сетки True, axis='y', linestyle='-'
        plt.show()

 #   def __del__(self):
 #       print()
 #       logging.debug('graphics destructor')
 #       return super().__del__()
        # text1 = plt.text(1.7, 0.5, date)
        #ax.plot(dates,ydata)
   #     plt.xticks(x1, D)
        #plt.xticks(rotation='vertical')  # plt.xticks(rotation='vertical') 