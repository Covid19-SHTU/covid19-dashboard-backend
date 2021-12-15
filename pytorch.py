import numpy as np
import torch
from torch import nn
from torch.autograd import Variable
import matplotlib.pyplot as plt


# define LSTM module
class lstm_reg(nn.Module):
    def __init__(self, input_size, hidden_size, output_size=1, num_layers=2):
        super(lstm_reg, self).__init__()

        self.rnn = nn.LSTM(input_size, hidden_size, num_layers)  # rnn
        self.reg = nn.Linear(hidden_size, output_size)  # 回归

    def forward(self, x):
        x, _ = self.rnn(x)  # (seq, batch, hidden)
        s, b, h = x.shape
        x = x.view(s * b, h)  # 转换成线性层的输入格式
        x = self.reg(x)
        x = x.view(s, b, -1)
        return x

def create_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back])
    return np.array(dataX), np.array(dataY)

# use PyTorch to predict future M days data
def pytorch_predict_data(data:list[int], M:int):
    print(data)
    data=np.array(data)
    data=data.astype(np.float32)
    max_v=np.max(data)
    min_v=np.min(data)
    scalar=max_v-min_v
    data=data/scalar
    #data=(data-data.mean())/data.std()
    K=3 # look back number
    data_X,data_Y=create_dataset(data,look_back=K)

    # 划分训练集和测试集，70% 作为训练集
    train_size = int(len(data_X) * 0.7)
    test_size = len(data_X) - train_size
    train_X = data_X[:train_size]
    train_Y = data_Y[:train_size]
    test_X = data_X[train_size:]
    test_Y = data_Y[train_size:]

    train_X = train_X.reshape(-1, 1, 2)
    train_Y = train_Y.reshape(-1, 1, 1)
    test_X = test_X.reshape(-1, 1, 2)

    train_x = torch.from_numpy(train_X)
    train_y = torch.from_numpy(train_Y)
    test_x = torch.from_numpy(test_X)

    net = lstm_reg(2, 4)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-2)

    # start training
    for e in range(200):
        var_x = Variable(train_x)
        var_y = Variable(train_y)
        # 前向传播
        out = net(var_x)
        loss = criterion(out, var_y)
        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (e + 1) % 100 == 0:  # 每 100 次输出结果
            print('Epoch: {}, Loss: {:.5f}'.format(e + 1, loss.data))

    print(data[-K-M-2:])
    pred = data[-K-M:-M]
    for i in range(M):
        now_data=np.array(pred[-K:]).reshape(-1,1,2)
        now_data=torch.from_numpy(now_data)
        var_data=Variable(now_data)
        new_pred=net(var_data)
        new_pred=new_pred.data.numpy()
        #print(new_pred[0][0][0])
        pred=np.append(pred,new_pred[0][0][0])
    print(pred)
    print(data[-M-K:])

    data_X = data_X.reshape(-1, 1, 2)
    data_X = torch.from_numpy(data_X)
    var_data = Variable(data_X)
    pred_test = net(var_data)  # the predict of test data
    pred_test = pred_test.view(-1).data.numpy()
    #print(pred_test)
    #print(data_X)
    plt.subplot(2,1,1)
    plt.plot(pred_test, 'r', label='prediction')
    plt.subplot(2,1,2)
    plt.plot(data, 'b', label='real')
    plt.legend(loc='best')
    plt.show()