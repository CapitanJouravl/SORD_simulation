import tkinter as tk
from tkinter import ttk
import numpy as np
import math as mth
from numpy import random as rnd
from random import randrange

win = tk.Tk()
win.title('Антенна')
win.geometry('700x750')

frm = tk.Frame(win, width = 700, height = 400, bg = 'gray').place(y = 0, x = 0)

btns = [['Заданные Параметры', 'Полученные Параметры', 'Старт'],
        ['Тип сигнала', '1', '3'],
        ['Тип цели', '2', '4'],
        ['Угол прихода', '0', '5'],
        ['Дистанция', '0', '6']
        ]
def signal(SignalType, AngleT, DistT):
    c = 1500
    M = 20
    m = np.arange(M-1, -1, -1)
    #print(m)
    f = 5000
    fd = 60000
    dt = 1/fd
    ts = np.arange(0, 0.2, dt) #длительность сигнала
    Tau = []
    #Создание массива массивов задержек
    for i in range(len(DistT)):
        Tau2 = []
        Tau1 = np.sin(np.deg2rad(AngleT[i])) * DistT[i] / c
        for j in range(len(m)):
            Tau2.append(m[j] * Tau1)
        Tau.append(Tau2)
    #print(Tau)

    sig = np.array(np.zeros(len(ts)))
    ### не используется, будет добавлено в DLC ##########
    if SignalType == 'Ам':                            ###
        fmod = 3                                      ###
        SigMod = np.sin(2*np.pi*fmod*ts)              ###
        for i in range(len(DistT)):                   ###
            sig1 = []                                 ###
            sig2 = []                                 ###
            for j in range(len(m)):                   ###
                sig1= np.sin(2*np.pi*f*(ts-Tau[i][j]))###
                sig1 = sig1 * SigMod                  ###
                sig2 = [[sig2],                       ###
                        [sig1]]                       ###
            sig= [sig, [sig2]]                        ###
    #####################################################

    elif SignalType == 'Гармонический':
        for i in range(len(DistT)):
            sig1 = np.array([])
            sig2 = np.array(np.zeros(len(ts)))
            for j in range(len(m)):
                sig1= np.sin(2*np.pi*f*(ts-Tau[i][j]))
                sig2 = sig2+sig1# суммированные сигналы от одной цели с разными задержками
                #sig2 = np.sum(sig2, axis=0)
            #print(sig2)
            sig= sig+sig2# суммированные сигналы от целей с задержками
    #print(sig)

    t = np.arange(0,3,dt)
    SNoise = np.random.normal(size = t.size)  # длительность всего тракта с шумом
    SigSTART = int(round(((2 * np.min(DistT) / c) / dt), 0))# время в момент прихода сигнала
    #print(SigSTART)
    SigEND = int(SigSTART + ts.size - 1)# время в момент прекращения сигнала
    print(SigEND)

    a = 0
    #Формирование полного тракта с добавлением сигнала после отражения от цели
    for i in range(SigSTART, SigEND + 1):
        SNoise[i] = SNoise[i] + sig[a]
        a = a+1
    print(SNoise)


def target(TargetType, SignalType, Angle, Dist):
    #print(Angle)
    #print(Dist)
    DistX = []
    DistX.append(0)
    DistY = []
    DistY.append(0)
    DX1 = int(float(Dist) * mth.cos(int(Angle)*np.pi/180))
    DY1 = int(float(Dist) * mth.sin(int(Angle)*np.pi/180))
    DX = []
    DY = []
    DistT = []
    AngleT = []
    if TargetType == 'Пл':
        for i in range(1, 7):
            DistX.append(DistX[i-1]+randrange(5, 20))
            DistY.append(randrange(-5, 5))
    if TargetType == 'Имитатор':
        for i in range(1, 3):
            DistX.append(DistX[i-1]+randrange(15, 30))
            DistY.append(0)
    if TargetType == 'Облако':
        for i in range(1, 15):
            DistX.append(randrange(-50, 60))
            DistY.append(randrange(-40, 50))
    for j in range(1,len(DistX)):
        DistX[j] = DistX[j]*mth.cos(int(Angle)*np.pi/180)-DistY[j]*mth.sin(int(Angle)*np.pi/180)
        DistY[j] = DistX[j]*mth.sin(int(Angle)*np.pi/180)+DistY[j]*mth.cos(int(Angle)*np.pi/180)
        DX.append(DX1 + DistX[j])
        DY.append(DY1 + DistY[j])
        DistT.append(mth.sqrt((int(DX1) + int(DistX[j]))**2+(int(DY1) + int(DistY[j]))**2))
        AngleT.append(mth.degrees(mth.atan((DY1 + DistY[j])/(DX1 + DistX[j]))))
    ###
    #print(DX)
    #print(DY)
    #print(DistT)
    #print(AngleT)
    signal(SignalType, AngleT, DistT)

def risovalka():
    print('Иди остальное доделывай')

def start():
    SignalType = Sbox.get()
    TargetType = Tbox.get()
    Angle = Z[0].get('1.0','end')
    Dist = Z[1].get('1.0', 'end')
    #print(SignalType)
    #print(TargetType)
    #print(Angle)
    #print(Dist)
    target(TargetType, SignalType, Angle, Dist)


Z = []
for i in range(len(btns)):
    for j in range(len(btns[i])):
        num = j*len(btns)+i
        if btns[i][j] == 'Тип сигнала' or btns[i][j] == 'Тип цели' or btns[i][j] == 'Угол прихода' or btns[i][j] == 'Дистанция':
            tk.Label(text = btns[i][j],
                     font = ('Timews New Roman',10,'bold'),
                     width = 20, height = 1).place(y = 410+(i+1)*50, x = j*200)
        elif btns[i][j] == 'Заданные Параметры':
            tk.Label(text=btns[i][j],
                     font=('Timews New Roman', 10, 'bold'),
                     width=30, height=1).place(y = 410+(i+1)*60, x = 75)
        elif btns[i][j] == 'Полученные Параметры':
            tk.Label(text=btns[i][j],
                     font=('Timews New Roman', 10, 'bold'),
                     width=35, height=1).place(y = 410+(i+1)*60, x = 400)
        elif btns[i][j] == '1':
            Sbox = ttk.Combobox(win, state = ('readonly'),
                                values=['Гармонический'])#'Ам', можно вернуть, но я не знаю зачем, если обработки будут одинаковыми
            Sbox.place(y = 410+(i+1)*50, x = j*200)
        elif btns[i][j] == '2':
            Tbox = ttk.Combobox(win, state = ('readonly'),
                                values=['Пл','Имитатор','Облако'])
            Tbox.place(y = 410+(i+1)*50, x = j*200)
        elif btns[i][j] == '0':
            Z.append(tk.Text(font=('Timews New Roman', 10, 'bold'),
                    width=17, height=1))
            Z[-1].place(y=410 + (i + 1) * 50, x=(j) * 200)
        elif btns[i][j] == '3' or btns[i][j] == '4' or btns[i][j] == '5' or btns[i][j] == '6':
            tk.Label(text=btns[i][j],
                     font=('Timews New Roman', 10, 'bold'),
                     width=20, height=1).place(y = 410+(i+1)*50, x = (j)*200)
        elif btns[i][j] == 'Старт':
            tk.Button(text = 'Старт',
                      font=('Timews New Roman', 10, 'bold'),
                      width=30, height=1, command = start).place(y = 405, x = 200)


win.mainloop()