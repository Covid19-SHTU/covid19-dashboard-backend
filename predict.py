import math

import pandas as pd
import numpy as np
import keras
import tensorflow as tf
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt

def prog_data(data: list[int]) -> (int,np.array):
    max_v=max(data)
    min_v=min(data)
    scalar=max_v-min_v
    #print(max_v,min_v)
    t=np.array(data)
    t=t.astype(np.float32)
    t=t/scalar
    t=t.reshape(-1,1)
    data_x = np.array(t)
    return scalar,data_x

def tensorflow_predict(data: list[int], name: str, M:int,look_back:int) -> list[int]:
    print("Debug: predicting",name)
    model=tf.keras.models.load_model('saved_model/'+name)
    scalar,data_x=prog_data(data)

    K = look_back
    pred = data_x[-K:]
    for i in range(0, M):
        now_data = np.array(pred[-K:]).reshape(1, K, 1)
        prid_out = model.predict(now_data)
        pred = np.append(pred, prid_out[0][0])
    res=[]
    for i in range(K, len(pred)):
        if math.isnan(pred[i]):
            res.append(0)
        else:
            res.append(int(pred[i]*scalar))
    return res



def tensorflow_alchemy(data:list[int], look_back: int,name:str):
    scalar,data_x=prog_data(data)
    data_train = data_x[:]

    batch_size=2

    data_input_x = []
    data_input_y = []
    for i in range(len(data_train)-look_back-1):
        data_input_x.append(np.array(data_train[i:(i+look_back)]).reshape(look_back))
        data_input_y.append(np.array(data_train[i+look_back]).reshape(1))
    i=0
    data_input = []
    data_input_x2 = []
    data_input_y2 = []
    while i+batch_size<=len(data_input_x):
        tx = []
        ty = []
        for j in range(i,i+batch_size):
            tx.append(data_input_x[j])
            ty.append(data_input_y[j])
        data_input.append((np.array(tx),np.array(ty)))
        data_input_x2.append(np.array(tx))
        data_input_y2.append(np.array(ty))
        i+=batch_size


    data_input_x = np.array(data_input_x)
    data_input_y = np.array(data_input_y)
    model = Sequential()
    model.add(LSTM(64, activation='relu', input_shape=(look_back,1),return_sequences=True))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    num_epochs = 15
    model.fit(x=data_input_x,y=data_input_y, epochs=num_epochs, verbose=1,batch_size=batch_size)

    model.save("saved_model/"+name)



    return


def tensorflow_debug(data:list[list[int]], look_back: int,name:str):
    M=14
    N=len(data)
    N=1
    print(N)
    max_v=0
    min_v=9999999
    for i in data[:N]:
        max_v=max(max_v,max(i))
        min_v=min(min_v,min(i))
    scalar=max_v-min_v
    print(max_v,min_v)
    for i in range(N):
        t=np.array(data[i])
        t=t.astype(np.float32)
        t=t/scalar
        t=t.reshape(-1,1)
        data[i]=t
        if i==0:
            data_x = np.array(t)
        else:
            data_x=np.append(data_x,t)
        print(len(data[i]), len(data_x))
    #data=(data-data.mean())/data.std()
    #data_x=np.array(data).reshape(-1,1)
    split_percent=0.8
    split = int(len(data_x)*split_percent)
    print(split, len(data_x))
    data_train = data_x[:split]
    data_test = data_x[split:]

    batch_size=2

    train_generator = TimeseriesGenerator(data_train, data_train, length=look_back, batch_size=batch_size)
    print(train_generator[1])
    # #test_generator = TimeseriesGenerator(data_test, data_test, length=look_back, batch_size=1)
    data_input_x = []
    data_input_y = []
    for i in range(len(data_train)-look_back-1):
        data_input_x.append(np.array(data_train[i:(i+look_back)]).reshape(look_back))
        data_input_y.append(np.array(data_train[i+look_back]).reshape(1))
    i=0
    data_input = []
    data_input_x2 = []
    data_input_y2 = []
    while i+batch_size<=len(data_input_x):
        tx = []
        ty = []
        for j in range(i,i+batch_size):
            tx.append(data_input_x[j])
            ty.append(data_input_y[j])
        data_input.append((np.array(tx),np.array(ty)))
        data_input_x2.append(np.array(tx))
        data_input_y2.append(np.array(ty))
        i+=batch_size
    print(data_input[1])


    data_input_x = np.array(data_input_x)
    data_input_y = np.array(data_input_y)
    print(np.shape(data_input_x), np.shape(data_input_y))
    model = Sequential()
    model.add(LSTM(64, activation='relu', input_shape=(look_back,1),return_sequences=True))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    num_epochs = 3
    model.fit(x=data_input_x,y=data_input_y, epochs=num_epochs, verbose=1,batch_size=batch_size)

    T = 8
    for j in range(1, T + 1):
        p = -j * 14
        K = look_back
        pred = data[0][-K - M + p:-M + p]
        # print(pred)
        for i in range(0, M):
            now_data = np.array(pred[-K:]).reshape(1, K, 1)
            # print("ROUND",i)
            # print(now_data)
            prid_out = model.predict(now_data)
            # print(prid_out[0][0])
            pred = np.append(pred, prid_out[0][0])

        data_train = data_train.reshape(-1)
        data_test = data_test.reshape(-1)

        # print(pred)
        # print(data[0][-K-M+p:p])

        plt.subplot(T, 1, j)
        plt.plot(pred, 'r', label='prediction')
        # plt.subplot(2,1,2)
        plt.plot(data[0][-K - M + p:p], 'b', label='real')
        plt.legend(loc='best')
    plt.show()

