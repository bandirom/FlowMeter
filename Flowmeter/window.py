from tkinter import *
from tkinter import messagebox, filedialog, ttk
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
import flowmeter
import graphs
from tkcalendar import Calendar, DateEntry

fm = flowmeter.Flowmeter()

def insert_data(data, time= True):
    root = Root()
    root.insert_data_to_text(data, time)

def change_T(T):
    Root().change_label_T(T)
  
class Root(Tk):
    root = None                           # Атрибут для хранения единственного экземпляра
    new = True
    def __new__(self,*dt,**mp):           # класса Root
        if self.root is None:               # Если он еще не создан, то
            self.root = Tk.__new__(self,*dt,**mp) # вызовем __new__ родительского класса
        return self.root                    # вернем root
        
    def __init__(self):
        if  self.new:
            self.new = False
            print("Init GUI")
            self.connect = False
            self.n = self.counter()
            super(Root,self).__init__()
            self.title("Flowmeter")
            self.geometry("800x400+450+200")
            self.minsize(600,400)
            self.InitUI()
    
    def InitUI(self):
        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.com_name = StringVar()
        self.message = StringVar()
        
        self.b = Button(self, text="Authorization", command=self.auth_window)
        self.b.place( x = 40, y = 140 )
        
        self.groupCom = LabelFrame(self, text="Connection",font=("Arial", 13,"bold"))
        self.groupCom.place(x = 40, y = 40, width = 250 )

        self.label_com_port = Label(self.groupCom, text = "Com port: ")
        self.label_com_port.grid(column =0, row =0)

        self.combo_com_port = ttk.Combobox(self.groupCom, width = 10, textvariable = self.com_name, state='readonly')
        self.combo_com_port['values'] = fm.com_ports_list
        if len(fm.com_ports_list) > 0:
            self.combo_com_port.set(fm.com_ports_list[0])
        self.combo_com_port.grid(column = 1, row = 0)

        self.btn_com = ttk.Button(self.groupCom, text = "Connect", command = self.btn_com_click)
        self.btn_com.grid(column = 1, row = 1)

        self.btn_r = Button(self.groupCom, text = "R", command = self.click_btn_r)
        self.btn_r.grid(row = 0, column = 2, padx = 10)

        self.btn_ping = Button(self.groupCom, text = "Ping", command = self.click_btn_ping )
        self.btn_ping.grid(column = 2, row = 1)
        
        self.groupSetting = LabelFrame(self, text="Setting",font=("Arial", 13,"bold"))
        self.groupSetting.place(x = 300, y = 40, width = 480 )
        
        self.data_log = Text(self.groupSetting,
                             height=7,width=40,
                             font='TimeNewRoman 10',
                             wrap=WORD,state='normal')
        self.data_log.grid( row = 0, column = 0, columnspan = 3)

        self.scroll = Scrollbar(self.groupSetting, command=self.data_log.yview)
        self.scroll.grid(row = 0, column = 3, sticky = N+E+S)
        self.data_log.config(yscrollcommand=self.scroll.set)
        
        self.save_log = ttk.Button(self.groupSetting, text="Save log", command=self.save_log, state='normal')
        self.save_log.grid( row = 0, column = 4, padx=2)

        self.clear = Button(self.groupSetting, text="Clear", command=self.clear_log, state='normal')
        self.clear.grid( row = 1, column = 0)
        
        self.start = Button(self.groupSetting, text="Start", command=self.start_transmitt, state='disable')
        self.start.grid( row = 1, column = 1)
        
        self.stop = Button(self.groupSetting, text="Stop", command=self.stop_transmitt, state='disable')
        self.stop.grid( row = 1, column = 2)

        self.graphic = ttk.Button(self, text="Charts", command=self.open_grafics, state='normal')
        self.graphic.place(x = 40, y = 200 )

        self.cur_t = LabelFrame(self, text="Current T °С ",font=("Arial", 13,"bold"))
        self.cur_t.place(x = 150, y = 130 )

        self.label_cur_t = Label(self.cur_t, text="T",font=("Arial", 15,"bold"))
        self.label_cur_t.pack(fill="both", expand=True)

    def change_label_T(self,T):
        self.label_cur_t.configure(text = T)

##        self.pb = ttk.Progressbar(self.groupSetting, length=100)
##        self.pb.grid( row = 2, column = 2)
##        self.pb.start(100)
    
    def open_grafics(self):
        def create_chart():
            gr = graphs.Graphics()
            gr.create_chart(cal.selection_get(), self.check_F.get(), self.check_T.get())

        self.check_F = BooleanVar()
        self.check_A = BooleanVar()
        self.check_T = BooleanVar()
        self.set_param = Toplevel(self)
        self.set_param.title("Chart options")
        self.set_param.geometry("640x420+450+200")
        self.frame=LabelFrame(self.set_param, text="Date",font=("Arial", 13,"bold"))
        self.frame.place(x = 40, y = 40, width = 280, height = 250)
        cal = Calendar(self.frame,
                   font="Arial 14", selectmode='day',
                   cursor="hand2", year=2019, month=2, day=4)
        cal.pack(fill="both", expand=True)
        ttk.Button(self.set_param, text="Create chart", command=create_chart).place(x = 400, y = 300 )
        ttk.Checkbutton(self.set_param,text=u'Instant flow',variable=self.check_F,onvalue=True,offvalue=False).place(x = 360, y = 60 )
        ttk.Checkbutton(self.set_param,text=u'Temperature',variable=self.check_T, onvalue=True,offvalue=False).place(x = 360, y = 80 )


    def save_log(self):
        self.filename =  filedialog.asksaveasfilename(initialdir = "/home/pi/Desktop/",title = "Select file",filetypes = (("txt files","*.txt"),))
        print (self.filename)
        self.log_file_data = self.data_log.get('1.0', END)
        with open(self.filename, "a") as file:
            file.write( self.log_file_data)
        
    def clear_log(self):
        self.data_log.configure(state = NORMAL)
        self.data_log.delete('1.0', END)       
        self.data_log.configure(state = DISABLED)
        
    def change_button_state(self, state):
          self.start.configure(state = state)
          self.stop.configure(state = state)
    
    def start_transmitt(self):
        self.trigger = fm.send_triger(trigger = True)
        self.insert_data_to_text("start transmit")

    def stop_transmitt(self):
        self.trigger = fm.send_triger(trigger = False)
        self.insert_data_to_text("stop transmit")
                  
    def insert_data_to_text(self, data, time = True):
        print(data)
        self.data_log.configure(state = NORMAL)
        
        if time:
            self.data_log.insert(1.0,'{}. {} - {}\n'.format(self.n(),data, self.date_time()))
        else:
            self.data_log.insert(1.0,'{}\n'.format(data))   
        self.data_log.configure(state = DISABLED)
        
    def counter(self):
        num = 0
        def incrementer():
            nonlocal num
            num += 1
            return num
        return incrementer

    def date_time(self):
        now = datetime.now()
        return now.strftime("%d/%m/%y %H:%M:%S")
    
    def auth_window(self):
        def authorization():
            print("you maybe logined")
        self.window = Toplevel(self)
        self.window.title("Authorization")
        self.window.geometry("400x200+450+200")
        self.login = StringVar()
        self.password = StringVar()
        self.window.label_login = Label(self.window, text = "Login",)
        self.window.label_login.grid(row = 0, column = 0)
        
        self.window.label_pass = Label(self.window, text = "Password",)
        self.window.label_pass.grid(row = 1, column = 0)
       
        self.window.login = Entry(self.window,textvariable=self.login)
        self.window.login.grid(row = 0, column = 1)
        
        self.window.password = Entry(self.window,textvariable=self.password, show='*')
        self.window.password.grid(row = 1, column = 1)
        
        self.window.btn_auth = Button(self.window, text="Login", command=authorization, state='normal')
        self.window.btn_auth.grid( row = 2, column = 1)
    
    def click_btn_r(self):
        fm.com_ports_list = fm.refresh_list()
        self.combo_com_port.configure(values = fm.com_ports_list)
        
    def click_btn_ping(self):
        print("ping")
        self.resp = fm.ping_fm()
        if self.resp[0] == True:
            self.insert_data_to_text(self.resp[1])
        else:
            messagebox.showinfo("GUI Python", "Serial port is not open")
        
    def btn_com_click(self):
        if self.connect:
            self.connect = False
            self.btn_com.configure(text = "Connect")
            self.combo_com_port.configure(state ='readonly')
            self.disconnection()
            self.change_button_state(state = 'disabled')
        else:
            self.com_port = self.com_name.get()
            if self.connection():
                self.connect = True
                self.btn_com.configure(text = "Disconnect")
                self.combo_com_port.configure(state = DISABLED)
                self.change_button_state(state = 'normal')
            else:
                messagebox.showinfo("GUI Python", "Error open serial port")
            
    def connection(self):
        self.com_port = self.com_port[:self.com_port.find(" ")]
        self.connect = fm.connection(self.com_port)
        if self.connect:
            return True
        else:
            return False
    
    def disconnection(self):
        fm.disconnection()
        
    def __str__(self):
        print("root")
