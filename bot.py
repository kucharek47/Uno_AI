import random
import math
import torch
import torch.nn as nn
from collections import deque
from torch import optim

class siec_neuronowa(nn.Module):
    def __init__(self, wejscie, wyjscie):
        super(siec_neuronowa, self).__init__()
        self.warstwa_1 = nn.Linear(wejscie, 256)
        self.aktywacja_1 = nn.ReLU()
        self.warstwa_2 = nn.Linear(256, 128)
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
        self.epsilon_min = 0.1
        self.spadek_epsilon = 0.998
        self.gamma = 0.95

        self.urzadzenie = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.siec_glowna = siec_neuronowa(wejscie, wyjscie).to(self.urzadzenie)
        self.siec_celu = siec_neuronowa(wejscie, wyjscie).to(self.urzadzenie)
        self.siec_celu.load_state_dict(self.siec_glowna.state_dict())
        self.siec_celu.eval()

        self.optymalizator = optim.Adam(self.siec_glowna.parameters(), lr=0.001)
        self.funkcja_straty = nn.MSELoss()
        self.pamiec = pamiec_doswiadczen(10000)

    def wybierz_akcje(self, stan, maska):
        legalne_akcje = [i for i, m in enumerate(maska) if m == 1]
        if not legalne_akcje:
            return 60

        if random.random() <= self.epsilon:
            return random.choice(legalne_akcje)

        stan_tensor = torch.FloatTensor(stan).unsqueeze(0).to(self.urzadzenie)
        with torch.no_grad():
            wartosci_akcji = self.siec_glowna(stan_tensor)[0]

        for i in range(len(maska)):
            if maska[i] == 0:
                wartosci_akcji[i] = -math.inf

        return torch.argmax(wartosci_akcji).item()

    def ucz_sie(self, wielkosc_probki):
        if self.pamiec.wielkosc() < wielkosc_probki:
            return

        probka = self.pamiec.pobierz_probke(wielkosc_probki)

        stany = torch.FloatTensor([p[0] for p in probka]).to(self.urzadzenie)
        akcje = torch.LongTensor([p[1] for p in probka]).to(self.urzadzenie)
        nagrody = torch.FloatTensor([p[2] for p in probka]).to(self.urzadzenie)
        nastepne_stany = torch.FloatTensor([p[3] for p in probka]).to(self.urzadzenie)
        konce = torch.FloatTensor([p[4] for p in probka]).to(self.urzadzenie)

        aktualne_q = self.siec_glowna(stany).gather(1, akcje.unsqueeze(1)).squeeze(1)
        nastepne_q = self.siec_celu(nastepne_stany).max(1)[0]
        oczekiwane_q = nagrody + (self.gamma * nastepne_q * (1 - konce))

        strata = self.funkcja_straty(aktualne_q, oczekiwane_q.detach())

        self.optymalizator.zero_grad()
        strata.backward()
        self.optymalizator.step()

    def aktualizuj_cel(self):
        self.siec_celu.load_state_dict(self.siec_glowna.state_dict())

    def zapisz_model(self, path, epizod):
        stan_nauki = {
            'model_state_dict': self.siec_glowna.state_dict(),
            'epsilon': self.epsilon,
            'epizod': epizod
        }
        torch.save(stan_nauki, path)

    def wczytaj_model(self, path):
        punkt_kontrolny = torch.load(path)
        self.siec_glowna.load_state_dict(punkt_kontrolny['model_state_dict'])
        self.siec_celu.load_state_dict(self.siec_glowna.state_dict())
        self.epsilon = punkt_kontrolny.get('epsilon', 1.0)
        return punkt_kontrolny.get('epizod', 0)