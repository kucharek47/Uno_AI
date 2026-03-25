import random
import torch
import torch.nn as nn
from collections import deque

class siec_neuronowa(nn.Module):
    def __init__(self, wejscie, wyjscie):
        super(siec_neuronowa, self).__init__()
        self.warstwa_1 = nn.Linear(wejscie, 128)
        self.aktywacja_1 = nn.ReLU()
        self.warstwa_2 = nn.Linear(128, 128)
        self.aktywacja_2 = nn.ReLU()
        self.warstwa_3 = nn.Linear(128, wyjscie)

    def forward(self, x):
        x = self.warstwa_1(x)
        x = self.aktywacja_1(x)
        x = self.warstwa_2(x)
        x = self.aktywacja_2(x)
        return self.warstwa_3(x)

class pamiec_doswiadczen:
    def __init__(self, pojemnosc):
        self.bufor = deque(maxlen=pojemnosc)

    def dodaj(self, stan, akcja, nagroda, nastepny_stan, czy_koniec):
        self.bufor.append((stan, akcja, nagroda, nastepny_stan, czy_koniec))

    def pobierz_probke(self, wielkosc_probki):
        return random.sample(self.bufor, wielkosc_probki)

    def wielkosc(self):
        return len(self.bufor)