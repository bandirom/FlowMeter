import serial
from serial.tools import list_ports
from time import sleep
import threading, requests, json, logging, re, io
import window as w
import graphs
from datetime import timedelta, datetime
 

db = graphs.DataBase()

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
        
class Flowmeter(threading.Thread):
    def __init__(self, *args, **kwargs):
        print("init flowmeter")
        self.serBuffer = ""
        self.Thread_ = False
        self.data = "" # дані з FlowMeter
        self.ser = serial.Serial()
        self.com_ports_list = serial.tools.list_ports.comports()
        threading.Thread.__init__(self, target = self.SerialEvent) #thread.start()
        self.start()
        return super().__init__(*args, **kwargs)
   

    def run(self):
        self.minutes = datetime.now()
        logging.debug('start second thread')
        while(True):
            if self.Thread_:
                if self.ser.is_open:
                    now = datetime.now()
                    if now >= self.minutes:
                        print(now)
                        self.minutes = now +timedelta(seconds =5) #minutes=1,
                        self.data = self.SerialEvent()
                        try:
                            if self.data is not None:
                                self.data = self.parsing_data(self.data)
                                print(self.data)
                                if self.data is not None and (self.isfloat(self.data[0]) and self.isfloat(self.data[1])):
                                    w.change_T(self.data[1])
                                    db.insert_data(self.data)
                                    #Network(self.data[0])
                        except Exception as e:
                            print(e)
    #S=ssssss F=ffffff A=aaaaa.aa T=tttt;\r\n
    def parsing_data(self, data):
        if data.startswith("S="):
            data = re.findall(r'\w+', data)
            print (data)
            temp_f = data[3]
            temp_t = data[8]
            t,f = [],[]
            t = re.findall(r'\w',temp_t)
            f = re.findall(r'\w',temp_f)
            t.insert(2,'.')
            f.insert(3,'.')
            temp_t = "".join(t)
            f_LPM = "".join(f)
            f_MPH =round(float(f_LPM)/0.06)
            data = [f_LPM,temp_t]
            return data
        elif data.startswith("IN OPERATION MODE"):
            print (data)
            return "IN OPERATION MODE"
        elif data.startswith("IN USER MODE"):
            return "IN USER MODE"

    def isfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def com_list(self):
        self.com_ports_list = serial.tools.list_ports.comports()
        print(self.com_ports_list)
        return self.com_ports_list

    def send_triger(self, trigger):
        if self.ser.is_open:
            if trigger:
                self.ser.write(serial.to_bytes(0x9d))
                sleep(0.2)
                self.ser.write(serial.to_bytes(0x54))

                self.Thread_= True
            else:    
                self.ser.write(serial.to_bytes(0x9d))
                sleep(0.2)
                self.ser.write(serial.to_bytes(0x00))
                self.Thread_= False
            return True
        else:
            return False
        
        
    def connection(self, com_port):
        print(com_port)
        self.ser.port = com_port
        self.ser.baudrate = 57600
        self.ser.bytesize = serial.EIGHTBITS 
        self.ser.parity = serial.PARITY_NONE 
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout =  3000
        try:
            self.ser.open()
            return True
        except Exception as e:
            print ("error open serial port: " + str(e))
            return False


    def disconnection(self):
        self.ser.close()
        
    def refresh_list(self):
        return self.com_list()
    
    def ping_fm(self):
        if self.ser.is_open:
            self.ser.write(serial.to_bytes(0x9d))
            self.serBuffer = self.waitResponse()
            self.result = [True, self.serBuffer]
        else:
            print ("serial port is not open")
            self.result = [False]   
        return self.result
        
    def waitResponse(self):
        sleep(0.1)
        return self.SerialEvent()
        
    def SerialEvent(self):
        if (self.ser.inWaiting()>0):
          #  c = self.ser.readline()
          #  c = c.decode("ascii")
          #  return c             
            self.c = self.ser.read(self.ser.inWaiting()).decode("ascii")
            self.c = self.c[:self.c.find("\r")]
            return self.c                 
                 
class Network():
    
    def __init__(self, F):
        logging.debug('running init process data transmitt')
        #url = 'http://10.73.34.232:8080'
        url = 'http://192.168.0.63:8080'
       # url = '10.73.121.250/N2Control/api/N2/PostData'
        headers = {'content-type': 'application/json'}
        payload = {'Machine':'W031D-1880130', 'F': F }
        print(payload)
        try:
            r = requests.post(url,
                          data = json.dumps(payload),
                          headers = headers)
            w.insert_data(json.dumps(payload), time = False)
            w.insert_data("Successfull transmitted")
        except Exception as e:
            print(e)
            w.insert_data("Transmission failure")
            
    def __del__(self):
        logging.debug('network destructor')

#make_magic(Flowmeter)
