import torch
import torch.nn as nn
import torch.optim as optim

class siec_neuronowa(nn.Module):
    def __init__(self, wielkosc_wejscia, wielkosc_wyjscia):
        super(siec_neuronowa, self).__init__()
        self.warstwa_pierwsza = nn.Linear(wielkosc_wejscia, 128)
        self.aktywacja_pierwsza = nn.ReLU()
        self.warstwa_druga = nn.Linear(128, 128)
        self.aktywacja_druga = nn.ReLU()
        self.warstwa_wyjsciowa = nn.Linear(128, wielkosc_wyjscia)

    def forward(self, x):
        x = self.warstwa_pierwsza(x)
        x = self.aktywacja_pierwsza(x)
        x = self.warstwa_druga(x)
        x = self.aktywacja_druga(x)
        x = self.warstwa_wyjsciowa(x)
        return x