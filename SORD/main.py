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
    M = 20
    d = 0.2
    m = np.arange(M-1, -1, -1)
    n = 1024# количество точек бпф
    #print(m)
    f = 5000

    fd = 60000
    df = fd / n  # шаг дискретизации в частотной области
    fn = 4900  # нижняя частота пропускания
    fv = 5100  # верхняя частота пропускания
    kn = int(np.round(fn / df + 1, 0))  # для нижней частоты
    kv = int(np.round(fv / df + 1, 0))  # для верхней частоты
    dt = 1/fd
    fr = np.fft.fftfreq(n, d=dt)
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

    sig = np.zeros((len(m), len(ts)), dtype= int)
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
            sig1 = np.zeros((len(m), len(ts)), dtype= int)
            for j in range(len(m)):
                sig1[m] = np.sin(2*np.pi*f*(ts-Tau[i][j]))
            #print(sig1.shape)
            sig= sig+sig1# суммированные сигналы от целей с задержками
    #print(sig.shape)

    ##Формирование массива шума
    t = np.arange(0,3,dt)
    sNoise = np.random.normal(size = t.size)  # длительность всего тракта с шумом
    SNoise = np.zeros((len(m), len(sNoise)), dtype=int)
    for i in range(len(m)):
        SNoise[i] = sNoise
    #print(SNoise.shape)
    ##

    ## Нахождение первого и последнего отсчетов тракта, в которые пришел сигнал
    SigSTART = int(round(((2 * np.min(DistT) / c) / dt), 0))# время в момент прихода сигнала
    #print(SigSTART)
    SigEND = int(SigSTART + ts.size - 1)# время в момент прекращения сигнала
    #print(SigEND)
    ##

    ##Формирование полного тракта с добавлением сигнала после отражения от цели
    for i in range(len(m)):
        a = 0
        for j in range(SigSTART, SigEND + 1):
            SNoise[i][j] = SNoise[i][j] + sig[i][a]
            a = a+1
    #print(SNoise.shape)
    #print(SNoise)
    ##

    ##Рисование грфика сигнала во временной области
    #Sris = np.sum(SNoise,axis = 0)
    Sris = SNoise[0]
    fig = plt.figure()
    plt.plot(t, Sris)
    plt.title('Сигнал на ПЭ')
    plt.xlabel('Время, с')
    plt.ylabel('Амплитуда сигнала')
    #plt.show()
    ##
    ##Полосовой фильтр
    order = 6  # порядок
    nyq = 0.5 * fd  # полоса работы фильтра
    low = 4900 / nyq  # нижняя частота среза
    high = 5100 / nyq  # верхняя частота среза
    b, a = butter(order, [low, high], btype='band')  # коеф-нт фильтра
    sFilt = lfilter(b, a, Sris)

    amplitudeS = np.abs(hilbert(sFilt))

    imp = np.array([])
    for i in range(0, t.size):
        if amplitudeS[i] > 0.2:
            imp = np.append(imp, 1)
        else:
            imp = np.append(imp, 0)

    minUp, maxUp, k = 0, 0, 0
    arrInd = []
    for i in range(0, t.size):
        if imp[i] == 1:
            if maxUp == 0:
                minUp = i

            if minUp != 0:
                maxUp = i
        else:
            if (minUp != 0) and (maxUp != 0):
                # arrInd [мин. индекс, макс. индекс, кол-во отсчетов импульса]
                arrInd.append([minUp, maxUp, maxUp - minUp])
                k = k + 1
                minUp = 0
                maxUp = 0

    sizeArr = np.array(arrInd).shape[0]  # кол-во строк массива

    if sizeArr == 1:
        indImp = arrInd[0:2]
    else:
        longArrInd = np.array(arrInd)[:, 2]  # массив с длиннами импульсов
        indImp = arrInd[np.argmax(longArrInd)][0:2]  # индексы самого длинного испульса
    indImpReal = [np.mean(indImp) - ts.size / 2, np.mean(indImp) + ts.size / 2]
    indMin, indMax = int(indImpReal[0]), int(indImpReal[1])
    SS = SNoise[:, indMin: indMax]  # сигнал для дальнейшей обработки
    #print(SNoise.shape)

    N = int(round(len(ts) / n, 0))  # число тактов обработки сигнала
    #print(N)
    b = np.arange(-90, 90, 1) * np.pi / 180  # угол фазирования
    #Wp = np.zeros((N, len(b)))
    Wp = []
    #print(Wp.shape)

    for i in range(1, N):
        iN = (i - 1) * n + 1  # начальное значение временного интервала
        iK = i * n  # конечное значение временного интервала
        ## обрабатываемая выборка сигнала
        Sig = np.zeros((M, iK - iN + 1))
        #print(Sig.shape)
        for i in range(0, M):
            k = 0
            for j in range(iN, iK):
                Sig[i][k] = SS[i][j]
                k = k + 1

        Vp = np.array([])  # отклик в такте обработки
        sf = np.fft.fft(Sig, n, 1)
        for j in range(0, len(b)):
            ##Формирование массива фазирующих коэффициентов
            T0 = d / c * np.sin(b[j])
            T = np.arange(M, 0, -1) * T0
            coef = np.zeros((M, n), dtype=complex)
            for l in range(0, M):
                coef[l] = np.exp(1j * 2 * np.pi * T[l] * fr)

            sfComp = np.multiply(sf, coef)  # компенсация временных задержек
            PK = np.sum(sfComp, axis=0)  # формирование ПК в направлении b
            Z = np.array([])
            ##квадрат модуля пространственного канала
            for k in range(kn, kv):
                Z = np.append(Z, np.absolute(PK[k]) ** 2)
            #print(Z.shape)
            Vp = np.append(Vp, np.sum(Z, axis=0))
            #print(Vp.shape)
        print(Vp)
        Wp.append(Vp)
        #print(Wp.shape)
    #print(Wp.shape)
    Wpt = np.sum(Wp, axis=0)
    b_ris = np.arange(-90, 90, 1)  # угол фазирования
    peleng = int(b[np.argmax(Wpt)]*180/np.pi)  # пеленг
    print(peleng)

    Wp = np.flipud(Wp)
    fig = plt.figure()
    plt.imshow(Wp, origin='lower',
               extent=[-90, 90, t[indMax], t[indMin]],
               aspect=500)
    plt.xlabel('Градусы')
    plt.ylabel('Время, с')
    plt.title('Набор откликов антенны в яркостном виде')
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