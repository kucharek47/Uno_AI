import random
import torch
import torch.nn as nn
from collections import deque

from torch import optim


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


class agent_dqn:
    def __init__(self, wejscie, wyjscie):
        self.wejscie = wejscie
        self.wyjscie = wyjscie
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.spadek_epsilon = 0.995
        self.gamma = 0.95

        self.siec_glowna = siec_neuronowa(wejscie, wyjscie)
        self.siec_celu = siec_neuronowa(wejscie, wyjscie)
        self.siec_celu.load_state_dict(self.siec_glowna.state_dict())
        self.siec_celu.eval()

        self.optymalizator = optim.Adam(self.siec_glowna.parameters(), lr=0.001)
        self.funkcja_straty = nn.MSELoss()
        self.pamiec = pamiec_doswiadczen(10000)

    def wybierz_akcje(self, stan):
        if random.random() <= self.epsilon:
            return random.randrange(self.wyjscie)

        stan_tensor = torch.FloatTensor(stan).unsqueeze(0)
        with torch.no_grad():
            wartosci_akcji = self.siec_glowna(stan_tensor)
        return torch.argmax(wartosci_akcji[0]).item()

    def ucz_sie(self, wielkosc_probki):
        if self.pamiec.wielkosc() < wielkosc_probki:
            return

        probka = self.pamiec.pobierz_probke(wielkosc_probki)

        stany = torch.FloatTensor([p[0] for p in probka])
        akcje = torch.LongTensor([p[1] for p in probka])
        nagrody = torch.FloatTensor([p[2] for p in probka])
        nastepne_stany = torch.FloatTensor([p[3] for p in probka])
        konce = torch.FloatTensor([p[4] for p in probka])

        aktualne_q = self.siec_glowna(stany).gather(1, akcje.unsqueeze(1)).squeeze(1)

        nastepne_q = self.siec_celu(nastepne_stany).max(1)[0]
        oczekiwane_q = nagrody + (self.gamma * nastepne_q * (1 - konce))

        strata = self.funkcja_straty(aktualne_q, oczekiwane_q.detach())

        self.optymalizator.zero_grad()
        strata.backward()
        self.optymalizator.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.spadek_epsilon

    def aktualizuj_cel(self):
        self.siec_celu.load_state_dict(self.siec_glowna.state_dict())