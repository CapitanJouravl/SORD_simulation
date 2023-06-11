import tkinter as tk
from tkinter import ttk
import numpy as np
import math as mth
import matplotlib.pyplot as plt
from random import randrange
from scipy.signal import butter, lfilter, hilbert

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
    M = 2
    d = 1
    m = np.arange(M-1, -1, -1)
    #print(m)
    n = 1024# количество точек бпф
    #print(m)
    f = 5000

    fd = 30000
    dt = 1/fd
    ts = np.arange(0, 0.02, dt) #длительность сигнала
    Tau = []
    #print(AngleT)
    #print(DistT)
    #Создание массива массивов задержек
    Tau = np.zeros((len(DistT), len(m)))
    for i in range(len(DistT)):
        Tau2 = []
        Tau1 = np.sin(np.deg2rad(AngleT[i])) * d / c
        #print(Tau1)
        for j in range(len(m)):
            Tau2.append(m[j] * Tau1)
        Tau[i] = Tau2
    #print(Tau)

    sig = np.zeros((len(m), len(ts)), dtype= float)
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
        sig = np.sin(2 * np.pi * f * ts)
        #for i in range(len(DistT)):
        #    sig1 = np.zeros((len(m), len(ts)), dtype= float)
        #    for j in range(len(m)):
        #        sig1[j] = np.sin(2*np.pi*f*(ts-Tau[i][j]))
        #    sig= sig+sig1# суммированные сигналы от целей с задержками
    #print(np.shape(sig))

    ##Формирование массива шума
    t = np.arange(0,3,dt)
    sNoise = 0*np.random.normal(size = t.size)  # длительность всего тракта с шумом
    SNoise = np.zeros((len(m), len(sNoise)), dtype=float)
    for i in range(len(m)):
        SNoise[i] = sNoise
    #print(SNoise.shape)
    ##

    ## Нахождение первого и последнего отсчетов тракта, в которые пришли сигналы
    SigSTART = np.zeros((len(m), len(DistT)), dtype = int)
    SigEND = np.zeros((len(m), len(DistT)), dtype = int)
    for i in range(len(DistT)):
        SigSTART[0][i] = int(round(((2 * DistT[i] / c) / dt), 0))# время в момент прихода сигнала на первом элементе
        SigSTART[1][i] = SigSTART[0][i]+int(Tau[i][0]/dt)# время в момент прихода сигнала на втором элементе
        #print(SigSTART)
        SigEND[0][i] = int(SigSTART[0][i] + ts.size - 1)# время в момент прекращения сигнала на первом элементе
        SigEND[1][i] = int(SigSTART[1][i] + ts.size - 1)# время в момент прекращения сигнала на втором элементе
    #print(SigSTART)
    #print(SigEND)
    ##

    ##Формирование полного тракта с добавлением сигнала после отражения от цели
    for i in range(len(m)):
        for k in range(len(DistT)):
            a = 0
            for j in range(SigSTART[i][k], SigEND[i][k] + 1):
                SNoise[i][j] = SNoise[i][j] + sig[a]
                a = a+1
    #print(SNoise.shape)
    #print(SNoise)
    ##

    ##Рисование грфика сигнала во временной области
    #Sris = SNoise[0]
    #fig = plt.figure()
    #plt.plot(t, Sris)
    #plt.title('Сигнал на ПЭ')
    #plt.xlabel('Время, с')
    #plt.ylabel('Амплитуда сигнала')
    #plt.show()
    ##
    Imp_Start = []
    Imp = np.zeros((len(m), len(t)))
    K = np.zeros(len(m))
    for j in range(len(m)):
        imp_Start = []
        ##Полосовой фильтр
        order = 6  # порядок
        nyq = 0.5 * fd  # полоса работы фильтра
        low = 4900 / nyq  # нижняя частота среза
        high = 5100 / nyq  # верхняя частота среза
        b, a = butter(order, [low, high], btype='band')  # коеф-нт фильтра
        sFilt = lfilter(b, a, SNoise[j])

        amplitudeS = np.abs(hilbert(sFilt))
        # print(np.max(amplitudeS))
        imp = np.array([])
        for i in range(0, t.size):
            if amplitudeS[i] > 0.2:
                imp = np.append(imp, 1)
            else:
                imp = np.append(imp, 0)
        # print(np.max(imp))
        Imp[j] = imp

        minUp, maxUp, k = 0, 0, 0
        arrInd = []
        for i in range(0, t.size):
            if imp[i] == 1:
                if maxUp == 0:
                    minUp = i
                        #print(minUp)

                if minUp != 0:
                    maxUp = i
            else:
                if (minUp != 0) and (maxUp != 0):
                    # arrInd [мин. индекс, макс. индекс, кол-во отсчетов импульса]
                    arrInd.append([minUp, maxUp, maxUp - minUp])
                    k = k + 1
                    imp_Start.append(minUp)
                    minUp = 0
                    maxUp = 0
        Imp_Start.append(imp_Start)
        K[j] = k
    #print(Imp_Start)
    ##Определение дистанции
    t_p = Imp_Start[0][0]
    Dist_r = t_p*dt*c/2
    #print(Dist_r)

    ##Определение пеленга
    Tau_ras = (Imp_Start[1][0] - Imp_Start[0][0])*dt
    #print(Tau_ras)
    peleng = np.rad2deg(np.arcsin(Tau_ras*c/d))
    #print(peleng)

    ##Определение типа цели
    #print(np.min(K))
    #print(np.max(SNoise[0]))
    if np.min(K)<=3 and np.max(SNoise[0])>1:
        Target = 'Подводная лодка'
    if np.min(K)==3 and np.max(SNoise[0])<1:
        Target = 'Имитатор'
    if np.min(K)>3 and np.max(SNoise[0])>1:
        Target = 'Облако обломков'
    #print(Target)

    fig1 = plt.figure()
    plt.plot(t, Imp[0])
    plt.title('Импульс на 1')
    plt.xlabel('Время, с')
    plt.ylabel('Амплитуда сигнала')
    plt.show()

    fig2 = plt.figure()
    plt.plot(t, Imp[1])
    plt.title('Импульс на 2')
    plt.xlabel('Время, с')
    plt.ylabel('Амплитуда сигнала')
    plt.show()


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