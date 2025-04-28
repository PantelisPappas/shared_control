import torch
import torch.nn as nn
import torch.optim as optim

class ArbiN3(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, hidden_size3, output_size):
        super(ArbiN3, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size1)
        self.bn1 = nn.BatchNorm1d(hidden_size1)
        self.sig1 = nn.Sigmoid()
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)
        self.bn2 = nn.BatchNorm1d(hidden_size2)
        self.sig2 = nn.Sigmoid()
        self.fc3 = nn.Linear(hidden_size2, hidden_size3)
        self.bn3 = nn.BatchNorm1d(hidden_size3)
        self.sig3 = nn.Sigmoid()
        self.fc4 = nn.Linear(hidden_size3, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.bn1(x)
        x = self.sig1(x)
        x = self.fc2(x)
        x = self.bn2(x)
        x = self.sig2(x)
        x = self.fc3(x)
        x = self.bn3(x)
        x = self.sig3(x)
        x = self.fc4(x)

        x = torch.sigmoid(x)

        return x

