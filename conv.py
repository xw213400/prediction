#!/usr/bin/python

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim

class Conv(nn.Module):
    def __init__(self, nfeatures, ni, no):
        super(Conv, self).__init__()
        self.entryblock = nn.Conv1d(7, nfeatures, 3, stride=1, padding=1, bias=False)
        self.rbconv = nn.Conv1d(nfeatures, nfeatures, 3, stride=1, padding=1, bias=False)
        self.classifier = nn.Conv1d(nfeatures, 2, 1, stride=1)
        self.fc = nn.Linear(ni, no)
        self.ni = ni
        self.no = no

    def forward(self, x):
        out = self.entryblock(x)
        out = F.relu(self.rbconv(out) + out)
        out = F.relu(self.rbconv(out) + out)
        out = self.classifier(out)
        out = out.view(-1, self.ni * 2)
        out = self.fc(out)

        return out