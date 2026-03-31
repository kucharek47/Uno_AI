# Uno AI

Projekt implementujący popularną grę karcianą Uno wraz ze środowiskiem do uczenia ze wzmocnieniem (Reinforcement Learning). Sztuczna inteligencja oparta jest na algorytmie Deep Q-Network (DQN) przy użyciu biblioteki PyTorch. Projekt zawiera również interfejs graficzny napisany w Pygame, który umożliwia grę przeciwko wytrenowanym botom.

## Funkcje

* Kompletny silnik gry Uno z obsługą kart specjalnych (+2, +4, zmiana kierunku, stop, zmiana koloru) oraz mechaniką łączenia kart (combo).
* Agent AI wykorzystujący sieci neuronowe (DQN) do podejmowania decyzji.
* System pamięci doświadczeń (Experience Replay) dla efektywniejszego uczenia bota.
* Interfejs graficzny (GUI) pozwalający na rozgrywkę gracza z botami.
* Skrypt treningowy pozwalający na ciągłe douczanie modelu i zapis jego postępów.

## Skuteczność treningu

Analiza logów z późniejszych etapów nauki potwierdza zdolność modelu do adaptacji i planowania taktycznego. Przykładem jest epizod 5000, w którym bot zagrał pojedynczą kartę dobierania (+2), aby zweryfikować, czy kolejny gracz ma możliwość obrony. Po upewnieniu się o braku zagrożenia, bot bezpiecznie zrzucił dwie pozostałe karty +2 w ramach dozwolonego combo, zmuszając przeciwnika do pobrania 6 kart. Takie zachowanie bezpośrednio podkreśla skuteczność zastosowanego algorytmu i wyuczonej strategii.

## Wymagania

Do uruchomienia projektu wymagane jest środowisko Python oraz instalacja bibliotek zdefiniowanych w pliku requirements.txt. Główne zależności to PyTorch, Pygame i NumPy.

Instalacja:

```bash
pip install -r requirements.txt
```

## Uruchomienie

### Rozgrywka z AI (Interfejs graficzny)

Aby zagrać przeciwko wytrenowanym botom, uruchom skrypt interfejsu graficznego:

```bash
python gui.py
```

### Trening modelu

Aby rozpocząć lub wznowić proces uczenia bota, uruchom główny skrypt:

```bash
python main.py
```

System automatycznie zapisuje postępy w postaci plików tekstowych z przebiegiem epizodów oraz tworzy plik z wagami modelu (np. model_uno_v10.pth).

## Struktura plików

* gra_w_uno.py - Logika gry, definicje kart, talii, graczy oraz środowisko dla bota.
* bot.py - Definicja sieci neuronowej, pamięci doświadczeń oraz klasy agenta DQN.
* gui.py - Implementacja interfejsu graficznego.
* main.py - Skrypt do przeprowadzania symulacji i trenowania sieci neuronowej.
* requirements.txt - Lista wymaganych pakietów.
* model_uno_v10.pth - Zapisany plik z wagami wytrenowanego modelu.