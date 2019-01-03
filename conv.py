#!/usr/bin/python

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
import random
import math

ILen = 20
OLen = 1
DEBUG = False


class ConvData:
    def __init__(self, ri, ro):
        self.input = np.zeros((8, ILen), np.float32)
        self.output = np.zeros(OLen, np.float32)

        invopen = 1.0 / ri[0].open

        for i in range(ILen):
            record = ri[i]
            self.input[0][i] = record.time
            self.input[1][i] = (record.open * invopen - 1) * 10
            self.input[2][i] = (record.high * invopen - 1) * 10
            self.input[3][i] = (record.low * invopen - 1) * 10
            self.input[4][i] = (record.close * invopen - 1) * 10
            self.input[5][i] = record.volume
            self.input[6][i] = record.openInterest
            self.input[7][i] = (record.settlement * invopen - 1) * 10

        self.input[5] = self.input[5] / np.sqrt((self.input[5]**2).sum())
        self.input[6] = self.input[6] / np.sqrt((self.input[6]**2).sum())

        invRoOpen = 1.0 / ro[0].open

        for i in range(OLen):
            record = ro[i]
            self.output[i] = (record.close * invRoOpen - 1) * 1000


class Conv(nn.Module):
    def __init__(self, nfeatures):
        super(Conv, self).__init__()
        self.entryblock = nn.Conv1d(
            8, nfeatures, 3, stride=1, padding=1, bias=False)
        self.rbconv = nn.Conv1d(nfeatures, nfeatures, 3,
                                stride=1, padding=1, bias=False)
        self.classifier = nn.Conv1d(nfeatures, 1, 1, stride=1)
        self.fc = nn.Linear(ILen, OLen)

    def forward(self, x):
        out = self.entryblock(x)
        if DEBUG:
            print("========")
            print(x[0][1])
            print(out[0][0])
        out = F.relu(self.rbconv(out) + out)
        out = F.relu(self.rbconv(out) + out)
        out = self.classifier(out)
        out = out.view(-1, ILen)
        out = self.fc(out)

        return out


def train(datas, net, epoch):
    global DEBUG
    criterion = nn.MSELoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    # if torch.cuda.is_available():
    #     criterion = criterion.cuda()

    batch = 32
    N = math.floor(len(datas)/32)

    for e in range(epoch):
        random.shuffle(datas)
        running_loss = 0.0
        i = 0

        while i < N:
            j = 0
            input_data = np.zeros((batch, 8, ILen), np.float32)
            target_data = np.zeros((batch, OLen), np.float32)
            while j < batch:
                data = datas[i*batch+j]
                input_data[j] = data.input
                target_data[j] = data.output
                j += 1

            input_data = torch.tensor(input_data)
            target_data = torch.tensor(target_data)

            optimizer.zero_grad()

            x = Variable(input_data)
            t = Variable(target_data)

            # if torch.cuda.is_available():
            #     x = x.cuda()
            #     t = t.cuda()

            y = net(x)

            loss = criterion(y, t)
            loss.backward()

            optimizer.step()
            running_loss += loss

            i += 1

        print('epoch: %d, loss: %.3f' % (e, running_loss/len(datas)))
