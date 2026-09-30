import math
import numpy as np
import cmath
import tkinter as tk
from tkinter import ttk

from rich.table import Table
from rich import box  

def new_bar(matriz):
    #cria barras. [tipo de barra(0), capacitância(1), tensão(2), angulo(3), potência ativa(4), potência reativa(5), existe carga?(6),retância positiva(7), tensão base(8), strafo(9)]
    #tensão em p.u., ângulo em radianos, potência ativa e reativa em p.u.

    bar = [0,0,0,0,0,0,0,0,0,0]

    bartype = int(input("Insira o tipo da barra: "))
    carga = int(input("Existe carga? (1 = sim, 0 = não): "))
    gerador = float(input("Insira o valor de reatância positiva do gerador (p.u.): "))
    c = float(input("Insira a potência reativa da capacitância da barra (p.u.): "))
    vb = float(input("Insira o valor da tensão base da barra (kV): "))
    t = int(input("Existe trafo? (1 = sim, 0 = não): "))
    if(t == 1):
        st = float(input("Insira o valor Strafo (p.u.): "))
    else:
        st = 0

    if bartype == 1:

        v = float(input("Insira a tensão (p.u.): "))
        dg = float(input("Insira o angulo (rad): "))
        bar = [bartype,c,v,dg,0,0,carga, gerador, vb, st]

    else:
        if bartype == 2:
            v = float(input("Insira a tensão (p.u.): "))
            p = float(input("Insira a potência ativa gerada (pu): "))

            if(carga == 0):
                bar = [bartype,c,v,0,p,0,carga, gerador, vb, st]
            else:
                bar = [bartype,c,v,0,-p,0,carga, gerador, vb, st]
        else:
            if bartype == 3:
                p = float(input("Insira a potência ativa liberada (pu): "))
                q = float(input("Insira a potência reativa liberada (pu): "))

                if(carga == 0):
                    bar = [bartype,c,1,0,p,q,carga, gerador, vb, st]
                else:
                    bar = [bartype,c,1,0,-p,-q,carga, gerador, vb, st]

    matriz.append(bar)

def new_connect(y, frombar, tobar,bars, connections):
    #cria linhas
    r = float(input("Insira a resistência (p.u.): "))
    xl = float(input("Insira a reatância indutiva (p.u.): "))
    b = float(input("Insira a susceptância (p.u.): "))

    addconnect = [frombar, tobar, r, xl, b]
    connections.append(addconnect)

    z = r + (xl*1j) 

    y[frombar-1][tobar-1] += -1/z
    y[tobar-1][frombar-1] += -1/z

    y[frombar-1][frombar-1] += 1/z + (b*1j)/2
    y[tobar-1][tobar-1] += 1/z + (b*1j)/2   

def soma_shunt(y, bars):
    #soma elemento shunt das barras
    for i in range(len(bars)):
        if(bars[i][1] != 0):
            y[i][i] += (bars[i][1]*1j)


def new_matriz(tam1, tam2):
    #criação genérica de matriz tam1xtam2
    matriz = []
    for l in range(tam1):
        linha = []
        for c in range(tam2):
            elemento = 0
            linha.append(elemento)
        matriz.append(linha)
    return matriz

def convergence(x, e):
    #teste de convergência
    for i in range(len(x)):
        if(abs(x[i]) > e):
            return False
    
    return True

def bars_qnt(bars):
    #quantidade de PQ e PV (PQ é qnt[0], PV é qnt[1])
    qnt = [0, 0]
    for i in range(len(bars)):
            if bars[i][0] == 2:
                qnt[0] = qnt[0] + 1
            
            if bars[i][0] == 3:
                qnt[1] = qnt[1] + 1      

    return qnt

def create_x(bars, Y, qnt):
    #matriz de delta P e delta Q
    x = new_matriz(qnt[0] + (2 * qnt[1]), 1)

    i = 0

    for i1 in range(len(bars)):
        if bars[i1][0] != 1:
            dP = 0
            for i2 in range(len(Y[0])):
                if Y[i1][i2] != 0:
                    dP += bars[i2][2] * (Y[i1][i2].real * math.cos(bars[i1][3] - bars[i2][3]) + Y[i1][i2].imag * math.sin(bars[i1][3] - bars[i2][3]))
            
            x[i] = bars[i1][4] - (bars[i1][2] * dP)
            i += 1

    for i1 in range(len(bars)):
        if bars[i1][0] == 3:
            dQ = 0
            for i2 in range(len(Y[0])):
                if Y[i1][i2] != 0:
                    dQ += bars[i2][2] * (Y[i1][i2].real * math.sin(bars[i1][3] - bars[i2][3]) - Y[i1][i2].imag * math.cos(bars[i1][3] - bars[i2][3]))

            x[i] = bars[i1][5] - (bars[i1][2] * dQ)
            i +=  1

    return x

def create_h(bars, Y):
    #Cria submatriz h
    H = new_matriz(len(bars) - 1, len(bars) - 1)

    b = 0
    b2 = 0
    

    for i in range(len(H)):
        select = 0
        j = 0
        while(j<len(H[0])):
            valor = 0
            while(select == 0):
                if bars[b][0] != 1:
                    select = 1
                else:
                    b+=1

            for b2 in range(len(Y)):
                valor = 0
                if bars[b2][0] != 1:
                    if b == b2:
                        for n in range(len(Y)):
                            if Y[b][n] != 0 and b != n:
                                valor += bars[n][2] * (-Y[b][n].real * math.sin(bars[b][3] - bars[n][3]) + Y[b][n].imag * math.cos(bars[b][3] - bars[n][3]))
                        H[i][j] = -(valor * bars[b][2])

                    else:
                            valor = bars[b][2]*bars[b2][2] * (Y[b][b2].real * math.sin(bars[b][3] - bars[b2][3]) - Y[b][b2].imag * math.cos(bars[b][3] - bars[b2][3]))
                            H[i][j] = -(valor)
                    j+=1      

            
        b+=1
                
    return H

def create_n(bars, Y):
    #Cria submatriz n
    qnt = bars_qnt(bars)
    N = new_matriz(len(bars) - 1, qnt[1])

    b = 0
    b2 = 0

    for i in range(len(N)):
        select = 0
        j = 0
        while j < len(N[0]):
            valor = 0
            while(select == 0):
                if bars[b][0] != 1:
                    select = 1
                else:
                    b+=1
            
            for b2 in range(len(Y)):
                valor = 0
                if bars[b2][0] == 3:
                    if b == b2:
                        for n in range(len(Y)):
                            if Y[b][n] != 0 and b != n:
                                valor += bars[n][2] * (Y[b][n].real * math.cos(bars[b][3] - bars[n][3]) + Y[b][n].imag * math.sin(bars[b][3] - bars[n][3]))

                        if valor != 0:
                            N[i][j] = -(valor + 2*bars[b][2]*Y[b][b].real)

                    else:
                            valor = bars[b][2] * (Y[b][b2].real * math.cos(bars[b][3] - bars[b2][3]) + Y[b][b2].imag * math.sin(bars[b][3] - bars[b2][3]))
                            N[i][j] = -(valor) 
                    j+=1 
        b+=1
            
    return N

def create_m(bars, Y):
    #Cria submatriz m
    qnt = bars_qnt(bars)
    M = new_matriz(qnt[1], len(bars) - 1)

    b = 0
    b2 = 0

    for i in range(len(M)):
        select = 0
        j = 0
        while j <len(M[0]):
            valor = 0
            while(select == 0):
                if bars[b][0] == 3:
                    select = 1
                else:
                    b+=1

            for b2 in range(len(Y)):
                valor = 0
                if bars[b2][0] != 1:
                    if b == b2:
                        for n in range(len(Y)):
                            if Y[b][n] != 0 and b!=n:
                                        valor += bars[n][2] * (Y[b][n].real * math.cos(bars[b][3] - bars[n][3]) + Y[b][n].imag * math.sin(bars[b][3] - bars[n][3]))
                        M[i][j] = -(valor * bars[b][2])
                    else:

                        valor = -bars[b][2] * bars[b2][2] * (Y[b][b2].real * math.cos(bars[b][3] - bars[b2][3]) + Y[b][b2].imag * math.sin(bars[b][3] - bars[b2][3]))
                        M[i][j] = -(valor)
                    j+=1
        b+=1
    return M

def create_l(bars, Y):
    #Cria submatriz l
    qnt = bars_qnt(bars)
    L = new_matriz(qnt[1], qnt[1])

    b = 0
    b2 = 0

    for i in range(len(L)):
        select = 0
        j = 0
        while j < len(L[0]):
            valor = 0
            while(select == 0):
                if bars[b][0] == 3:
                    select = 1
                else:
                    b+=1  
            
            for b2 in range(len(Y)):
                valor = 0
                if bars[b2][0] == 3:
                    if b == b2:
                        for n in range(len(Y)):
                            if Y[b][n] != 0 and b!=n:
                                        valor += bars[n][2] * (Y[b][n].real * math.sin(bars[b][3] - bars[n][3]) - Y[b][n].imag * math.cos(bars[b][3] - bars[n][3]))
                        
                        if valor!=0:
                            L[i][j] = -(valor + -2*bars[b][2]*Y[b][b].imag)

                    else:
                        valor = bars[b][2] * (Y[b][b2].real * math.sin(bars[b][3] - bars[b2][3]) - Y[b][b2].imag * math.cos(bars[b][3] - bars[b2][3]))
                        L[i][j] = -(valor)
                    j+=1   
        b+=1  

            
                
    return L

def create_jacob(bars, Y, qnt):
    #Une as submatrizes
    H = create_h(bars,Y)
    N = create_n(bars,Y)
    M = create_m(bars,Y)
    L = create_l(bars,Y)

    jacob1 = new_matriz(len(H), len(H[0]) + len(N[0]))

    i1 = 0
    j1 = 0

    for i in range(len(jacob1)):
        j1=0
        for j in range(len(jacob1[0])):
            if(j < len(H[0])):
                jacob1[i][j] = H[i][j]
            else:
                jacob1[i][j] = N[i1][j1]
                j1+=1
        i1+=1
    jacob2 = new_matriz(len(M), len(M[0]) + len(L[0]))

    i1 = 0
    j1 = 0

    for i in range(len(jacob2)):
        j1=0
        for j in range(len(jacob2[0])):
            if(j < len(M[0])):
                jacob2[i][j] = M[i][j]
            else:
                jacob2[i][j] = L[i1][j1]
                j1+=1
        i1+=1

    result = np.vstack((jacob1, jacob2))

    return result
            
def calc_pow(bars,y, qnt):
    #calculo da potência final
    v1 = v2 = 0
    for i in range(len(bars)):
        if bars[i][0] == 1:
            for b in range(len(y)):
                if y[i][b] != 0:
                    v1 += bars[b][2] * (y[i][b].real * math.cos(bars[i][3] - bars[b][3]) + y[i][b].imag * math.sin(bars[i][3] - bars[b][3]))
                    v2 += bars[b][2] * (y[i][b].real * math.sin(bars[i][3] - bars[b][3]) - y[i][b].imag * math.cos(bars[i][3] - bars[b][3]))
            bars[i][4] = v1*bars[i][2]
            bars[i][5] = v2*bars[i][2]
    
        v1 = v2 = 0

        if bars[i][0] == 2:
            for b in range(len(y)):
                if y[i][b] != 0:
                    v2 += bars[b][2] * (y[i][b].real * math.sin(bars[i][3] - bars[b][3]) - y[i][b].imag * math.cos(bars[i][3] - bars[b][3]))
            bars[i][5] = v2*bars[i][2]
                
                
def NewtonRhapson(y,bars,qnt,e):
    #Processo do Newton Rhapson de fato
    test = 0
    while True:
        x = create_x(bars, y, barsqnt)
        jacob = np.linalg.inv(np.negative(create_jacob(bars, y,qnt)))

        #print(x)

        result = np.matmul(jacob,x)

        i = 0
        i1 = 0
        #print(create_jacob(bars, y),"\n")
        #bars_print(bars)
        #print(result,"\n")

        while i < qnt[0] + qnt[1]:
            if bars[i1][0] != 1:
                bars[i1][3] = bars[i1][3] + result[i]
                i1+=1
                i+=1
            else:
                i1+=1
        
        i1 = 0

        while  i < (qnt[0] + qnt[1]*2):
            if bars[i1][0] == 3:
                bars[i1][2] = bars[i1][2] + result[i]
                i1+=1
                i+=1
            else:
                i1+=1

        #print(result)
        x = create_x(bars, y, barsqnt)
        #print("test")

        if convergence(x,e) == True:
            calc_pow(bars,y, barsqnt)
            break

def exist_in(x,vet):
    #verifica se o elemento x existe em um vetor
    flag = False
    count = int
    count = 0
    while count < len(vet):
        if vet[count][0] == x:
            flag = True
        count += 1

    return flag

def get_corrente(barqnts,Sb):
    #recebe as correntes harmôncias
    vet = []
    bar = 1
    while(bar != -1):

        
        bar = int(input("Insira a barra da inserção (-1 para parar): "))
        if(bar != -1):

            h = int(input("Insira a ordem harmônica: "))
            i = float((input("Insira o valor da corrente: ")))/( (Sb*1000)/(bars[bar-1][8]*np.sqrt(3)) )
            f = np.radians((float(input("Insira o fasor da corrente: "))))

            a = ( i * np.cos(f))
            b = ( i * np.sin(f))
            if(exist_in(h,vet)):
                for count in range(len(vet)):
                    if vet[count][0] == h:
                        for count1 in range(len(vet[count][1])):
                            if count1 == bar-1:
                                vet[count][1][count1] = [complex(a,b)]
            else:
                veti = new_matriz(barqnts, 1)
                addvet = [0,0]
                veti[bar-1] = [complex(a,b)]
                addvet[0] = h
                addvet[1] = veti
                #print(addvet,"\n")
                vet.append(addvet)

        #print(vet,"\n")
        
    return vet

def correct_y(connections, barsqnt, h,bars):
    y = new_matriz(barsqnt, barsqnt)
    for count in range(len(connections)):

        frombar = connections[count][0]
        tobar = connections[count][1]
        r = connections[count][2]

        xl = connections[count][3]*h
        b = connections[count][4]*h

        z = r + (xl*1j) 


        y[frombar-1][tobar-1] = -1/z
        y[tobar-1][frombar-1] = -1/z

        y[frombar-1][frombar-1] += 1/z + (b*1j)/2
        y[tobar-1][tobar-1] += 1/z + (b*1j)/2


    for i in range(len(bars)):
        if(bars[i][7] > 0):
            y[i][i] += 1/(bars[i][7]*h*1j)
        
        if(bars[i][6] == 1):
            
            r = (bars[i][2]*bars[i][2])/(-bars[i][4])
            xl = (bars[i][2]*bars[i][2])/(bars[i][5]*1j)
            y[i][i] += 1/r + 1/(xl*h)

        if(bars[i][1] > 0):
            y[i][i] += (bars[i][1]*1j*h)
    
    return y


def harmonic_calc(currents, connections, barsqnt,bars,vh):
    DTT = new_matriz(barsqnt, 1)
    DIT = new_matriz(barsqnt, len(currents))
    for count in range(len(currents)):
        h = currents[count][0]

        Yh = np.linalg.inv(correct_y(connections,barsqnt,h,bars))
        #print(currents[count][1])
        #print("\n")
        #print(Yh)

        v = np.matmul(Yh,currents[count][1])

        for l in range(len(DIT)):
            DIT[l][count] = v[l][0]

        for i in range(len(DTT)):
            DTT[i][0] += abs(v[i][0])*abs(v[i][0])

    for i in range(len(DTT)):
        DTT[i][0] = (np.sqrt(DTT[i][0])*100)
    vh.append(v)

    #print(f'VPAC = {abs(v[1][0])*13800/math.sqrt(3.0)}∠{cmath.phase(v[1][0])*(180/math.pi) + 30}°')

    #print("MEU VPAC: ",v[1])
    table = Table(show_header=True, header_style="bold orange_red1", box=box.HEAVY, title="Distorções harmônicas individuais para h = 5", title_style="bold orange_red1")
    table.add_column("Barra", justify="center")
    table.add_column("Tensão harmônica (V)\nh = 5", justify="center")
    table.add_column("DIT (h = 5)", justify="center")
    for i in range(len(DTT)):
        table.add_row(f'Barra {i + 1}', f'{abs(v[i][0])*(bars[i][8] * 1e3)/math.sqrt(3.0):.2f}∠{cmath.phase(v[i][0])*(180/math.pi) + 30:.2f}°', f'{DTT[i][0]:.2f}%')
    #print("DIT: \n",DIT,"\n")
    #print("DTT: \n",DTT,"\n")

    print('\n')  
    add_result_table(table, "Distorções harmônicas")

    return DTT

def calc_impedancias(PAC,bars,h,connections):

    sBase = Sb * 1e6
    vBase = bars[PAC][8] * 1e3
    zBase = (vBase**2) / sBase
    impedancias = new_matriz(1,len(bars)-1)[0]
    fill = 0
    for i in range(len(bars)):
        if(bars[i][0] == 1):
            for c in range(len(connections)):
                if(connections[c][0] == (i+1) or connections[c][1] == (i+1)):
                    #print(c)
                    Rcon = connections[c][2]
                    Xcon = connections[c][3]*h
                    #print("Rcon, Xcon:",Rcon,Xcon)
            #Lcon = (Xcon)/(2*math.pi*60)
            #Zcon = complex(Rcon,Xcon)*((13800*13800)/10000000)
            Zcon = complex(Rcon,Xcon)*zBase
            impedancias[fill] = Zcon
            #print("Zcon = ",Zcon)
            fill += 1
        else:
            if(i != PAC):
                #Zbase = (v*v)/(bars[i][9]*1000000)
                #print("Zb[",i,"]",Zbase)
                #Rind = ((bars[i][2]*bars[i][8]*1000)*(bars[i][2]*bars[i][8]*1000))/(bars[i][4]*1000000)
                #Rind = ((bars[i][2]*13800)*(bars[i][2]*13800))/(bars[i][4]*10000000)
                Rind = ((bars[i][2]*vBase)*(bars[i][2]*vBase))/(bars[i][4]*sBase)
                Rind = Rind*-1
                #print("R[",i,"]",Rind)
                #Lind = ((bars[i][2]*13800)*(bars[i][2]*13800)*h)/(bars[i][5]*10000000)
                Lind = ((bars[i][2]*vBase)*(bars[i][2]*vBase)*h)/(bars[i][5]*sBase)
                Lind = Lind*-1
                #print("L[",i,"]",Lind)
                #Cind = ((bars[i][2]*13800)*(bars[i][2]*13800))/(bars[i][1]*10000000*h)
                Cind = ((bars[i][2]*vBase)*(bars[i][2]*vBase))/(bars[i][1]*sBase*h)
                #print("C[",i,"]",Cind)
                #Rind_ = Rind*((bars[PAC][8]/bars[i][8])*(bars[PAC][8]/bars[i][8]))
                #Lind_ = Lind*((bars[PAC][8]/bars[i][8])*(bars[PAC][8]/bars[i][8]))
                #Cind_ = Cind*((bars[i][8]/bars[PAC][8])*(bars[i][8]/bars[PAC][8]))
                for c in range(len(connections)):
                    if(connections[c][0] == (i+1) or connections[c][1] == (i+1)):
                        Rtrafo = connections[c][2]
                        Xtrafo = connections[c][3]*h

                #Ztrafo = complex(Rtrafo,Xtrafo)*((13800*13800)/10000000)
                Ztrafo = complex(Rtrafo,Xtrafo)*zBase
                #print("RL_par[",i,"]",RL_par)
                Zind = Ztrafo + 1/(1/Rind + 1/(1j*Lind) + 1/(-1j*Cind))
                #print("Zc[",i,"]",Zc)

                #print("RL_C_par[",i,"]",RL_C_par)
                #print("Z_ind[",i,"]",Z_ind)
                impedancias[fill] = Zind
                #if(i == 2):
                #    print("Rind: ",Rind)
                #    print("Lind: ",Lind)
                #    print("Cind: ",Cind)
                #    print("Zind[",i,"]",Zind)
                #    print("V = ",(bars[i][2]*13800))
                fill += 1

    return impedancias

def calc_impedancias_trans(PAC,c,connections,h):
    impedancias = [0,0]
    for count in range (len(connections)):
        if ((connections[count][0] == c+1) or (connections[count][1] == c+1)):
            impedancias[0] += complex(connections[count][2], connections[count][3]*h)
        else:
            if ((connections[count][0] != c+1) and (connections[count][1] != c+1)):
                impedancias[1] += complex(connections[count][2],connections[count][3]*h)
    return impedancias


def projection_complex(z, w):
    # Cálculo do produto escalar z * w
    dot_product = z.real * w.real + z.imag * w.imag
    
    # Cálculo do módulo de w
    modulus_w = abs(w)
    
    # Cálculo da projeção vetorial
    projection = (dot_product / modulus_w**2) * w
    
    return projection

def defasar_30(z):
    return cmath.rect(abs(z),cmath.phase(z) + (30*(cmath.pi/180)))

def compartilha(y,bars, connections, currents, vh):
    #console = Console()

    vpac = 0
    iCon = 0
    iInd = []
    zCon = 0
    zInd = []
    vc_pac = []
    vs_pac = []
    vc_proj = []
    vs_proj = []
    resp = []

    cVec = []
    cVec = [int(item) for item in input("Insira a barra consumidora: ").split()]
    cVec = [x-1 for x in cVec]
    for c in cVec:
        for count in range(len(y[c])):
            if y[c][count] != 0 and count != c:
                PAC = count
        zsh = 0
        zch = 0
        impedancias = calc_impedancias(PAC,bars,5,connections)
        zCon = impedancias[0]
        zInd.append(impedancias[c - 1])

        #improviso
        #impedancias = (cmath.rect(5.9478,(89.5998*(math.pi/180))),cmath.rect(62.5424,(-4.3393*(math.pi/180))),cmath.rect(51.2691,(-4.9947*(math.pi/180))),cmath.rect(83.2596,(-21.6006*(math.pi/180))))
        #print(impedancias)
        #for i in range(len(impedancias)):
        #    print(f'Z{i} = {abs(impedancias[i])}∠{cmath.phase(impedancias[i])*(180/math.pi)}°')

        #vPAC = vh[0][PAC][0]
        #print(f'VPAC = {abs(vPAC)}∠{cmath.phase(vPAC)*(180/math.pi)}°')
        #j = 0
        #for i in range(len(vh[0])):
        #    if i != PAC:
        #        vBus = vh[0][i][0]
        #        print(f'V{i} = {abs(vBus)}∠{cmath.phase(vBus)*(180/math.pi)}°')
        #        zBranch = calc_impedancias_trans(PAC, i ,connections, 5)[0]
        #        iInj = ((vPAC - vBus) / zBranch) * (10e6 / (math.sqrt(3) * 13800))
        #        print(f'I{i} = {abs(iInj)}∠{cmath.phase(iInj)*(180/math.pi)}°')
        #        j += 1

        flag = 0
        # i = 0 flag = 0: zsh += 1/impedancias[0] flag = 1
        # i = 1 flag = 1: i = 2
        # i = 2 flag = 1: zch = impedancias[1] flag = 2
        # i = 3 flag = 2: zsh += 1/impedancias[2] flag = 3
        # i = 4 flag = 3: zsh += 1/impedancias[3] flag = 4
        for i in range(len(bars)):
            #print("i, flag: ",i,flag)
            if(i != PAC and i != c):
                #print("Flag, impedância",flag,impedancias[flag])
                zsh += 1/impedancias[flag]
                flag += 1
            else:
                if (i == c):
                    zch = impedancias[flag]
                    flag += 1
        
        #print("Zch: ",abs(zch))
        zsh = 1/zsh

        #print("Zsh: ",abs(zsh))
        #print("Zch 19.044: ",abs(zch)*19.044)

        #trocar 0 para h no final
        #print("vh[0][PAC]:",vh[0][PAC])
        #print("vh[0][c]:",vh[0][c])

        #vc = complex(vh[0][c].real*-1,vh[0][c].imag)
        #vpac =  0.00501242+0.032241j
        vpac = vh[0][PAC][0]
        vc = vh[0][c][0]


        ipac = ((vpac - ((vc)))/calc_impedancias_trans(PAC, c ,connections, 5)[0])

        iCon = ((vpac - ((vh[0][0][0])))/calc_impedancias_trans(PAC, 0 ,connections, 5)[0])
        
        vpac = vpac * bars[PAC][8] * 1e3 / cmath.rect(math.sqrt(3), -30*(math.pi/180)) # Em volts, seq negativa
        #print(f'VPAC = {abs(vpac)}∠{cmath.phase(vpac)*(180/math.pi)}°')

        ipac = ipac * (Sb * 1e6 / (math.sqrt(3) * bars[PAC][8] * 1e3)) # Em A
        ipac = defasar_30(ipac) # Trafo delta-estrela
        #print(f'I{c+1}-PAC = {abs(ipac)}∠{cmath.phase(ipac)*(180/math.pi)}°')
        iInd.append(ipac)

        
        iCon = iCon * (Sb * 1e6 / (math.sqrt(3) * bars[PAC][8] * 1e3)) # Em A
        iCon = defasar_30(iCon)
        
        #ipac = defasar_30(ipac)
        #vpac = defasar_30(vpac)
        #vpac = vpac/math.sqrt(3)
        #vpac = (cmath.rect(264.2867,(128.3914*(math.pi/180))))
        ish = (((vpac)/zsh) + ipac)
        ich = (((vpac)/zch) - ipac)

        vspach = ((zsh*zch)/(zsh+zch))*ish

        vcpach = ((zsh*zch)/(zsh+zch))*ich

        vs_pac.append(vspach)
        vc_pac.append(vcpach)

        #print("ish: ",abs(ish),cmath.phase(ish)*(180/math.pi) ," -> ",ish)
        #print("ich: ",abs(ich),cmath.phase(ich)*(180/math.pi)," -> ",ich)
        #print("ipac: ",abs(ipac),cmath.phase(ipac)*(180/math.pi)," -> ",ipac)
        #print("zsh: ",abs(zsh),cmath.phase(zsh)*(180/math.pi)," -> ",zsh)
        #print("zch: ",abs(zch),cmath.phase(zch)*(180/math.pi)," -> ",zch)
        #print("Vspah:",abs(vspach),cmath.phase(vspach)*(180/math.pi)," -> ",vspach)
        #print("Vcpah:",abs(vcpach),cmath.phase(vcpach)*(180/math.pi)," -> ",vcpach)
        #
        #print("Vpac:",abs(vpac),cmath.phase(vpac)*(180/math.pi)," -> ",vpac)

        vs_projC = projection_complex(vspach,vpac)
        vs_projC = abs(vs_projC)
        vc_projC = projection_complex(vcpach,vpac)
        vc_projC =  abs(vc_projC) * math.cos(cmath.phase(vc_projC) - cmath.phase(vpac)) # Considerar sinal da projeção

        vs_proj.append(vs_projC)
        vc_proj.append(vc_projC)
        #print("\nVs_proj:",abs(vs_proj))
        #print("\nVc_proj:",abs(vc_proj))
        #print(f'\nVc_proj = {abs(vc_proj)}∠{cmath.phase(vc_proj)*(180/math.pi)}°')
        #print(f'\nVs_projABS2 = {vc_proj}')

        respC = []
        respC.append((abs(vc_projC)/abs(vpac))*100) # Método 1
        respC.append((vc_projC/abs(vpac))*100) # Método 2
        respC.append(0.0) # Método 3, sendo necessário calcular todos os valores de vc_proj para obter o resultado final
        resp.append(respC)

    # Método 3
    for i in range(len(resp)):
        sumVcProj = 0
        for vcProjx in vc_proj:
            sumVcProj += abs(vcProjx)
        resp[i][2] = (abs(vc_proj[i])/sumVcProj)*100

    total = [0, 0, 0]
    for i in range(len(resp)):
        total[0] += resp[i][0]
        total[1] += resp[i][1]
        total[2] += resp[i][2]

    table1 = Table(show_header=True, header_style="bold orange1", box=box.HEAVY, title="Grandezas elétricas constatadas no PAC - análise para h = 5", title_style="bold orange1")
    table1.add_column("Grandeza\nordem h = 5", justify="center")
    table1.add_column("Valores", justify="center")
    table1.add_row(f'V_pac-h (V)', f'{abs(vpac):.2f}∠{cmath.phase(vpac)*(180/math.pi):.2f}°')
    table1.add_row(f'I_con-h (A)', f'{abs(iCon):.2f}∠{cmath.phase(iCon)*(180/math.pi):.2f}°')
    for i in range(len(iInd)):
        table1.add_row(f'I_ind{i + 1}-h (A)', f'{abs(iInd[i]):.2f}∠{cmath.phase(iInd[i])*(180/math.pi):.2f}°')
    table2 = Table(show_header=True, header_style="bold blue", box=box.HEAVY, title="Impedâncias harmônicas das partes do sistema - análise para h = 5", title_style="bold blue")
    table2.add_column("Grandeza\nordem h = 5", justify="center")
    table2.add_column("Valor de\nimpedância (Ω)", justify="center")
    table2.add_row(f'Z_con-h', f'{abs(zCon):.2f}∠{cmath.phase(zCon)*(180/math.pi):.2f}°')
    for i in range(len(zInd)):
        table2.add_row(f'Z_ind{i + 1}-h', f'{abs(zInd[i]):.2f}∠{cmath.phase(zInd[i])*(180/math.pi):.2f}°')
    table3 = Table(show_header=True, header_style="bold green", box=box.HEAVY, title="Fasores de contribuição individual de tensão em cada análise de compartilhamento", title_style="bold green")
    table3.add_column("Compartilhamento\ninvestigado", justify="center")
    table3.add_column("Vs-proj-h (V)", justify="center")
    table3.add_column("Vc-proj-h (V)", justify="center")
    for i in range(len(vs_pac)):
        table3.add_row(f'Indústria {i + 1}', f'{abs(vs_pac[i]):.2f}∠{cmath.phase(vs_pac[i])*(180/math.pi):.2f}°', f'{abs(vc_pac[i]):.2f}∠{cmath.phase(vc_pac[i])*(180/math.pi):.2f}°')
    table4 = Table(show_header=True, header_style="bold red", box=box.HEAVY, title="Projeções escalares dos fasores de contribuição individual de cada parte", title_style="bold red")
    table4.add_column("Compartilhamento\ninvestigado", justify="center")
    table4.add_column("Vs-proj-h (V)", justify="center")
    table4.add_column("Vc-proj-h (V)", justify="center")
    for i in range(len(vs_proj)):
        table4.add_row(f'Indústria {i + 1}', f'{vs_proj[i]:.2f}', f'{vc_proj[i]:.2f}')
    table5 = Table(show_header=True, show_footer=True, header_style="bold magenta", box=box.HEAVY, title="Percentuais de responsabilidades cabidos às indústrias", title_style="bold magenta")
    table5.add_column("Compartilhamento\ninvestigado", justify="center", footer="TOTAL")
    table5.add_column("Responsabilidade\nMétodo 1", justify="center", footer=f'{total[0]:.2f}%')
    table5.add_column("Responsabilidade\nMétodo 2", justify="center", footer=f'{total[1]:.2f}%')
    table5.add_column("Responsabilidade\nMétodo 3", justify="center", footer=f'{total[2]:.2f}%')
    for i in range(len(resp)):
        table5.add_row(f'Indústria {i + 1}', f'{resp[i][0]:.2f}%', f'{resp[i][1]:.2f}%', f'{resp[i][2]:.2f}%')
    add_result_table(table1, "Grandezas no PAC")
    add_result_table(table2, "Impedâncias")
    add_result_table(table3, "Fasores de contribuição")
    add_result_table(table4, "Projeções escalares")
    add_result_table(table5, "Responsabilidades")


def add_result_table(table, tab_title):
    headers = [str(column.header).replace("\n", " ") for column in table.columns]
    rows = []
    for row_index in range(len(table.rows)):
        rows.append(tuple(str(column._cells[row_index]) for column in table.columns))
    footers = [str(column.footer).replace("\n", " ") for column in table.columns]
    result_tables.append((tab_title, headers, rows, footers))


def show_results(tables):
    window = tk.Tk()
    window.title("Resultados da análise harmônica")
    window.geometry("1180x760")
    window.minsize(760, 500)
    window.configure(background="#101820")

    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure("Root.TFrame", background="#101820")
    style.configure("Header.TFrame", background="#172733")
    style.configure(
        "Tabs.TNotebook",
        background="#101820",
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "Tabs.TNotebook.Tab",
        background="#1C303D",
        foreground="#B8C8D3",
        padding=(16, 9),
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "Tabs.TNotebook.Tab",
        background=[("selected", "#2C7A7B")],
        foreground=[("selected", "#FFFFFF")],
    )
    style.configure(
        "Title.TLabel",
        background="#172733",
        foreground="#F5F7FA",
        font=("Segoe UI", 19, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background="#172733",
        foreground="#9FB3C8",
        font=("Segoe UI", 10),
    )
    style.configure(
        "Close.TButton",
        background="#2C7A7B",
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        padding=(18, 8),
    )
    style.map("Close.TButton", background=[("active", "#38A3A5")])

    root = ttk.Frame(window, style="Root.TFrame", padding=22)
    root.pack(fill=tk.BOTH, expand=True)

    header = ttk.Frame(root, style="Header.TFrame", padding=(24, 20))
    header.pack(fill=tk.X)
    ttk.Label(
        header,
        text="Resultados da análise harmônica",
        style="Title.TLabel",
    ).pack(anchor=tk.W)
    ttk.Label(
        header,
        text="Cálculo concluído • valores organizados por etapa da análise",
        style="Subtitle.TLabel",
    ).pack(anchor=tk.W, pady=(5, 0))

    notebook = ttk.Notebook(root, style="Tabs.TNotebook")
    notebook.pack(fill=tk.BOTH, expand=True, pady=(16, 12))

    style.configure(
        "Results.Treeview",
        background="#0B1117",
        fieldbackground="#0B1117",
        foreground="#E6EDF3",
        rowheight=30,
        font=("Segoe UI", 10),
        borderwidth=0,
    )
    style.configure(
        "Results.Treeview.Heading",
        background="#2C7A7B",
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        padding=(10, 8),
    )
    style.map(
        "Results.Treeview",
        background=[("selected", "#245A75")],
        foreground=[("selected", "#FFFFFF")],
    )

    for tab_title, headers, rows, footers in tables:
        tab = ttk.Frame(notebook, style="Root.TFrame", padding=(0, 14, 0, 0))
        notebook.add(tab, text=tab_title)
        table_frame = ttk.Frame(tab, style="Root.TFrame")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = [f"column_{index}" for index in range(len(headers))]
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Results.Treeview",
            selectmode="browse",
        )
        vertical_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=tree.yview,
        )
        horizontal_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=tree.xview,
        )
        tree.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )

        for column_id, header in zip(columns, headers):
            tree.heading(column_id, text=header)
            tree.column(column_id, anchor=tk.CENTER, width=max(140, len(header) * 10), stretch=True)

        for row in rows:
            tree.insert("", tk.END, values=row)

        if any(footers):
            tree.insert("", tk.END, values=footers, tags=("footer",))
            tree.tag_configure("footer", background="#172733", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"))

        tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    footer = ttk.Frame(root, style="Root.TFrame")
    footer.pack(fill=tk.X)
    ttk.Label(
        footer,
        text="Análise finalizada",
        style="Subtitle.TLabel",
    ).pack(side=tk.LEFT)
    ttk.Button(
        footer,
        text="Fechar",
        command=window.destroy,
        style="Close.TButton",
    ).pack(side=tk.RIGHT)

    window.mainloop()


# CÓDIGO

result_tables = []

Sb = float(input("Insira a base de potência: "))
qntbars = int(input("Insira a quantidade de barras: "))
print("-="*30)
print("TIPOS DE BARRA:\n1 - SLACK (Referência) \n2 - PV \n3 - PQ")
print("-="*30)

bars = []

for i in range(qntbars):
    print("-="*30)
    print("BARRA",i+1)
    print("-="*30)
    new_bar(bars)

barsqnt = bars_qnt(bars)
print("-="*30)
print("LIGAÇÕES (-1 para parar)")
print("-="*30)

y = new_matriz(qntbars, qntbars)

connections = []
vh = []
frombar = 0

while(frombar != -1):
    frombar = int(input("Da barra: "))
    if frombar != -1:
        tobar = int(input("Para barra: "))
        new_connect(y,frombar,tobar,bars, connections)
soma_shunt(y,bars)   
e = pow(10,-15)

NewtonRhapson(y,bars,barsqnt,e)
harmonic = get_corrente(qntbars,Sb)

harmonic_calc(harmonic,connections,qntbars,bars,vh)
compartilha(y,bars,connections,harmonic,vh)
show_results(result_tables)
