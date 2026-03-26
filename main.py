import os
from gra_w_uno import srodowisko_uno
from bot import agent_dqn


def main():
    liczba_graczy = 5
    epizody = 5000
    path = "model_uno_v10.pth"
    startowy_epizod = 0

    wielkosc_wejscia = 170 + (liczba_graczy - 1) * 3
    wielkosc_wyjscia = 63 + liczba_graczy

    agent = agent_dqn(wielkosc_wejscia, wielkosc_wyjscia)
    srodowisko = srodowisko_uno(liczba_graczy)
    zapisane_logi = []

    if os.path.exists(path):
        startowy_epizod = agent.wczytaj_model(path)
        print(f"Wznowiono trening od epizodu {startowy_epizod}. Epsilon: {agent.epsilon:.2f}")

    for epizod in range(startowy_epizod, epizody):
        srodowisko.resetuj()
        suma_nagrod = [0] * liczba_graczy
        licznik_krokow = 0
        kroki_pierwszego = None

        ostatni_stan = {}
        ostatnia_akcja = {}
        ostatnia_nagroda = {}

        while len(srodowisko.silnik.ranking) < 1 and licznik_krokow < 1000:
            id_gracza = srodowisko.silnik.aktualny_gracz
            stan = srodowisko.pobierz_stan(id_gracza)
            maska = srodowisko.pobierz_maske_akcji(id_gracza)

            akcja = agent.wybierz_akcje(stan, maska)
            nastepny_stan, nagroda, czy_koniec = srodowisko.wykonaj_krok(id_gracza, akcja)

            suma_nagrod[id_gracza] += nagroda

            if id_gracza in ostatni_stan:
                agent.pamiec.dodaj(ostatni_stan[id_gracza], ostatnia_akcja[id_gracza], ostatnia_nagroda[id_gracza],
                                   stan, False)

            if czy_koniec:
                agent.pamiec.dodaj(stan, akcja, nagroda, stan, True)
                if id_gracza in ostatni_stan:
                    del ostatni_stan[id_gracza]

                kroki_pierwszego = licznik_krokow

                for inny_id, o_stan in ostatni_stan.items():
                    ilosc_kart = len(srodowisko.silnik.gracze[inny_id].reka)
                    kara = -100 * ilosc_kart
                    suma_nagrod[inny_id] += kara
                    agent.pamiec.dodaj(o_stan, ostatnia_akcja[inny_id], ostatnia_nagroda[inny_id] + kara, o_stan, True)

                ostatni_stan.clear()
                break
            else:
                ostatni_stan[id_gracza] = stan
                ostatnia_akcja[id_gracza] = akcja
                ostatnia_nagroda[id_gracza] = nagroda

            agent.ucz_sie(64)
            licznik_krokow += 1

        if licznik_krokow >= 1000 and len(srodowisko.silnik.ranking) == 0:
            for inny_id, o_stan in ostatni_stan.items():
                ilosc_kart = len(srodowisko.silnik.gracze[inny_id].reka)
                kara = -100 * ilosc_kart
                suma_nagrod[inny_id] += kara
                agent.pamiec.dodaj(o_stan, ostatnia_akcja[inny_id], ostatnia_nagroda[inny_id] + kara, o_stan, True)
            ostatni_stan.clear()

        agent.aktualizuj_cel()

        if agent.epsilon > agent.epsilon_min:
            agent.epsilon *= agent.spadek_epsilon

        wyniki = [(i, suma_nagrod[i]) for i in range(liczba_graczy)]
        wyniki_posortowane = sorted(wyniki, key=lambda x: x[1], reverse=True)
        punkty_str = ", ".join([f"G{id_g}: {pkt}" for id_g, pkt in wyniki_posortowane])

        kroki_wypis = kroki_pierwszego if kroki_pierwszego is not None else "Brak"

        print(
            f"Epizod: {epizod + 1}, Kroki do 1. miejsca: {kroki_wypis}, Kroki calkowite: {licznik_krokow}, Punkty: [{punkty_str}], Epsilon: {agent.epsilon:.2f}")

        nazwa_pliku = f"log_epizod_{epizod + 1}.txt"
        with open(nazwa_pliku, "w", encoding="utf-8") as plik:
            plik.write(f"--- Epizod: {epizod + 1} ---\n")
            plik.write(f"Punkty: {punkty_str}\n")
            plik.write(f"Kroki do 1. miejsca: {kroki_wypis}\n")
            plik.write(f"Kroki calkowite: {licznik_krokow}\n\n")
            for log in srodowisko.silnik.logi:
                plik.write(log + "\n")

        zapisane_logi.append(nazwa_pliku)
        if len(zapisane_logi) > 3:
            stary_plik = zapisane_logi.pop(0)
            if os.path.exists(stary_plik):
                os.remove(stary_plik)

        if (epizod + 1) % 5 == 0:
            agent.zapisz_model(path, epizod + 1)
            print("Zapisano postęp nauki.")


if __name__ == "__main__":
    main()