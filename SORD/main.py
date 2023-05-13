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

def signal(SignalType, Angle, Dist, DistX, DistY):
    f = 5000
    fd = 16000
    df = 1/fd
    t = np.arange(0, 2, df)
    if SignalType == 'Ам':
        fmod = 3
        SigMod = np.sin(2*np.pi*fmod*t)
        SigStart = np.sin(2*np.pi*f*t)
        sig = SigStart*SigMod
    elif SignalType == 'Шум':
        sig = rnd.randn(t.size)
    elif SignalType == 'Гармонический':
        sig = np.sin(2*np.pi*f*t)

def target(TargetType, SignalType, Angle, Dist):
    #print(Angle)
    #print(Dist)
    COS = mth.cos(int(Angle)*np.pi/180)
    print(COS)
    DistX = []
    DistX.append(0)
    DistY = []
    DistY.append(0)
    DX1 = Dist * COS
    DY1 = Dist * mth.sin(int(Angle)*np.pi/180)
    if TargetType == 'Пл':
        for i in range(1, 7):
            DistX.append(DistX[i-1]+randrange(5, 20))
            DistY.append(randrange(-5, 5))
    if TargetType == 'Имитатор':
        for i in range(1, 7):
            DistX.append(DistX[i-1]+randrange(5, 20))
            DistY.append(0)
    if TargetType == 'Облако':
        for i in range(1, 15):
            DistX.append(randrange(-50, 60))
            DistY.append(randrange(-40, 50))
    for j in range(len(DistX)):
        DistX[j] = DistX[j]*mth.cos(int(Angle)*np.pi/180)-DistY[j]*mth.sin(int(Angle)*np.pi/180)
        DistY[j] = DistX[j]*mth.sin(int(Angle)*np.pi/180)+DistY[j]*mth.cos(int(Angle)*np.pi/180)
        DX[j] = DX1 + DistX[j]
        DY[j] = DY1 + DistY[j]
    print(DX)
    signal(SignalType, Angle, Dist, DistX, DistY)

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
                                values=['Ам','Шум','Гармонический'])
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