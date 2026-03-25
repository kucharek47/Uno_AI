import random


class karta:
    def __init__(self, kolor, wartosc):
        self.kolor = kolor
        self.wartosc = wartosc

    def __str__(self):
        return f"{self.kolor} {self.wartosc}" if self.kolor else self.wartosc


class talia:
    def __init__(self):
        self.karty = []
        self.buduj()

    def buduj(self):
        kolory = ['czerwony', 'zielony', 'niebieski', 'zolty']
        wartosci = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'stop', 'zmiana_kierunku', '+2']
        specjalne = ['zmiana_koloru', '+4']

        for kolor in kolory:
            self.karty.append(karta(kolor, '0'))
            for wartosc in wartosci[1:]:
                self.karty.append(karta(kolor, wartosc))
                self.karty.append(karta(kolor, wartosc))

        for _ in range(4):
            for specjalna in specjalne:
                self.karty.append(karta(None, specjalna))

    def tasuj(self):
        random.shuffle(self.karty)

    def dobierz(self):
        return self.karty.pop() if self.karty else None


class gracz:
    def __init__(self, id_gracza):
        self.id_gracza = id_gracza
        self.reka = []
        self.zglasza_uno = False

    def dobierz_karte(self, k):
        self.reka.append(k)
        self.zglasza_uno = False

    def rzuc_karte(self, indeks):
        return self.reka.pop(indeks)


class gra:
    def __init__(self, liczba_graczy):
        self.talia_gry = talia()
        self.talia_gry.tasuj()
        self.gracze = [gracz(i) for i in range(liczba_graczy)]
        self.stos = []
        self.aktualny_gracz = 0
        self.kierunek = 1
        self.aktualny_kolor = None
        self.aktualna_kara = 0
        self.ranking = []
        self.logi = []

        self.rozdaj()
        self.rozpocznij()

    def dodaj_log(self, wiadomosc):
        self.logi.append(wiadomosc)

    def pobierz_karte(self):
        k = self.talia_gry.dobierz()
        if not k:
            if len(self.stos) > 1:
                ostatnia_karta = self.stos.pop()
                self.talia_gry.karty = self.stos
                self.talia_gry.tasuj()
                self.stos = [ostatnia_karta]
                k = self.talia_gry.dobierz()
                self.dodaj_log("Przetasowano stos do nowej talii.")
        return k

    def rozdaj(self):
        for _ in range(7):
            for g in self.gracze:
                nowa_karta = self.pobierz_karte()
                if nowa_karta:
                    g.dobierz_karte(nowa_karta)
        self.dodaj_log("Rozdano karty graczom.")

    def rozpocznij(self):
        pierwsza_karta = self.pobierz_karte()
        while pierwsza_karta and pierwsza_karta.wartosc in ['zmiana_koloru', '+4']:
            self.talia_gry.karty.insert(0, pierwsza_karta)
            self.talia_gry.tasuj()
            pierwsza_karta = self.pobierz_karte()

        if pierwsza_karta:
            self.stos.append(pierwsza_karta)
            self.aktualny_kolor = pierwsza_karta.kolor
            self.dodaj_log(f"Gra rozpoczeta. Pierwsza karta: {pierwsza_karta}")

    def nastepny_gracz(self):
        if len(self.ranking) >= len(self.gracze) - 1:
            return

        self.aktualny_gracz = (self.aktualny_gracz + self.kierunek) % len(self.gracze)
        while self.gracze[self.aktualny_gracz].id_gracza in self.ranking:
            self.aktualny_gracz = (self.aktualny_gracz + self.kierunek) % len(self.gracze)

    def waliduj_ruch(self, k):
        if self.aktualna_kara > 0:
            return k.wartosc in ['+2', '+4']

        if k.kolor is None:
            return True

        if k.kolor == self.aktualny_kolor:
            return True

        if self.stos[-1].wartosc == k.wartosc:
            return True

        return False

    def krzycz_uno(self, id_gracza):
        if len(self.ranking) >= len(self.gracze) - 1:
            return False

        if id_gracza != self.aktualny_gracz:
            return False

        g = self.gracze[id_gracza]
        g.zglasza_uno = True
        self.dodaj_log(f"Gracz {id_gracza} krzyczy UNO!")
        return True

    def zagraj_karte(self, id_gracza, indeks_karty, wybrany_kolor=None):
        if len(self.ranking) >= len(self.gracze) - 1:
            return False

        if id_gracza != self.aktualny_gracz:
            return False

        g = self.gracze[id_gracza]
        k = g.reka[indeks_karty]

        if not self.waliduj_ruch(k):
            self.dodaj_log(f"Gracz {id_gracza} probowal wykonac nielegalny ruch: {k}")
            return False

        k = g.rzuc_karte(indeks_karty)
        self.stos.append(k)

        info_kolor = f" (wybrano: {wybrany_kolor})" if wybrany_kolor else ""
        self.dodaj_log(f"Gracz {id_gracza} rzucil: {k}{info_kolor}")

        if len(g.reka) > 1:
            g.zglasza_uno = False

        if len(g.reka) == 0:
            self.ranking.append(id_gracza)
            self.dodaj_log(f"Gracz {id_gracza} konczy na miejscu {len(self.ranking)}")
            if len(self.ranking) == len(self.gracze) - 1:
                for ost in self.gracze:
                    if ost.id_gracza not in self.ranking:
                        self.ranking.append(ost.id_gracza)
                        self.dodaj_log(f"Gracz {ost.id_gracza} przegrywa (ostatnie miejsce)")
                        break

        if k.kolor:
            self.aktualny_kolor = k.kolor
        else:
            self.aktualny_kolor = wybrany_kolor

        self.zastosuj_efekt(k)

        if len(self.ranking) < len(self.gracze) - 1:
            self.nastepny_gracz()

        return True

    def zastosuj_efekt(self, k):
        aktywni = len(self.gracze) - len(self.ranking)
        if k.wartosc == 'zmiana_kierunku':
            self.kierunek *= -1
            self.dodaj_log("Zmiana kierunku gry.")
            if aktywni == 2:
                self.nastepny_gracz()
        elif k.wartosc == 'stop':
            self.dodaj_log("Zablokowano kolejke nastepnego gracza.")
            self.nastepny_gracz()
        elif k.wartosc in ['+2', '+4']:
            wartosc_kary = int(k.wartosc[1:])
            self.aktualna_kara += wartosc_kary
            self.dodaj_log(f"Kara wzrasta. Do dobrania: {self.aktualna_kara} kart.")

    def rozlicz_kare(self, id_gracza, uzyj_ratunku=False):
        if len(self.ranking) >= len(self.gracze) - 1:
            return False

        if id_gracza != self.aktualny_gracz or self.aktualna_kara == 0:
            return False

        g = self.gracze[id_gracza]

        if uzyj_ratunku:
            self.dodaj_log(f"Gracz {id_gracza} szuka karty ratunkowej.")
            nowa_karta = self.pobierz_karte()
            if nowa_karta:
                g.dobierz_karte(nowa_karta)
                self.dodaj_log(f"Gracz {id_gracza} dociagnal: {nowa_karta}")

            if nowa_karta and nowa_karta.wartosc in ['+2', '+4']:
                self.dodaj_log(f"Gracz {id_gracza} znalazl ratunek!")
                return True

            for _ in range(self.aktualna_kara - 1):
                k = self.pobierz_karte()
                if k:
                    g.dobierz_karte(k)
            self.dodaj_log(f"Brak ratunku. Gracz {id_gracza} przyjal lacznie {self.aktualna_kara} kart kary.")
            self.aktualna_kara = 0
            self.nastepny_gracz()
            return False

        self.dodaj_log(f"Gracz {id_gracza} akceptuje kare {self.aktualna_kara} kart.")
        for _ in range(self.aktualna_kara):
            k = self.pobierz_karte()
            if k:
                g.dobierz_karte(k)

        self.aktualna_kara = 0
        self.nastepny_gracz()
        return True

    def dobierz_z_talii(self, id_gracza):
        if len(self.ranking) >= len(self.gracze) - 1:
            return False

        if id_gracza != self.aktualny_gracz or self.aktualna_kara > 0:
            return False

        g = self.gracze[id_gracza]
        nowa_karta = self.pobierz_karte()
        if nowa_karta:
            g.dobierz_karte(nowa_karta)
            self.dodaj_log(f"Gracz {id_gracza} dobral karte ze stosu.")

        self.nastepny_gracz()
        return True

    def zglos_brak_uno(self, id_celu):
        if len(self.ranking) >= len(self.gracze) - 1:
            return False

        g = self.gracze[id_celu]
        if len(g.reka) == 1 and not g.zglasza_uno:
            self.dodaj_log(f"Zlapano gracza {id_celu} na braku UNO. Dostaje 2 karty.")
            for _ in range(2):
                nowa_karta = self.pobierz_karte()
                if nowa_karta:
                    g.dobierz_karte(nowa_karta)
            return True
        return False


class srodowisko_uno:
    def __init__(self, liczba_graczy):
        self.liczba_graczy = liczba_graczy
        self.silnik = gra(liczba_graczy)
        self.kary_lokalne = {
            'nielegalny_ruch': -10,
            'zrzucenie_karty': 25,
            'dobranie_karty': -10,
            'wymuszenie_kary': 75,
            'poprawne_uno': 50,
            'zlapany_brak_uno': 75,
            'zapomniane_uno': -100
        }

    def _karta_na_indeks(self, k):
        if k.kolor is None:
            if k.wartosc == 'zmiana_koloru':
                return 52
            if k.wartosc == '+4':
                return 53

        kolory = ['czerwony', 'zielony', 'niebieski', 'zolty']
        wartosci = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'stop', 'zmiana_kierunku', '+2']

        baza = kolory.index(k.kolor) * 13
        offset = wartosci.index(k.wartosc)
        return baza + offset

    def pobierz_stan(self, id_gracza):
        stan = []
        g = self.silnik.gracze[id_gracza]

        reka_wektor = [0] * 54
        for k in g.reka:
            idx = self._karta_na_indeks(k)
            reka_wektor[idx] += 1
        stan.extend(reka_wektor)

        stos_wektor = [0] * 54
        if self.silnik.stos:
            idx = self._karta_na_indeks(self.silnik.stos[-1])
            stos_wektor[idx] = 1
        stan.extend(stos_wektor)

        kolory = ['czerwony', 'zielony', 'niebieski', 'zolty']
        kolor_wektor = [0] * 4
        if self.silnik.aktualny_kolor in kolory:
            kolor_wektor[kolory.index(self.silnik.aktualny_kolor)] = 1
        stan.extend(kolor_wektor)

        stan.append(self.silnik.aktualna_kara)
        stan.append(self.silnik.kierunek)

        for i in range(1, self.liczba_graczy):
            idx_przeciwnika = (id_gracza + i) % self.liczba_graczy
            przeciwnik = self.silnik.gracze[idx_przeciwnika]
            stan.append(len(przeciwnik.reka))
            stan.append(1 if przeciwnik.zglasza_uno else 0)

        return stan

    def oblicz_nagrode_koncowa(self, miejsce):
        if miejsce == self.liczba_graczy:
            return -1000

        if self.liczba_graczy > 2:
            wspolczynnik = -500
            baza = 1500
            return wspolczynnik * miejsce + baza

        return 1000

    def resetuj(self):
        self.silnik = gra(self.liczba_graczy)
        return self.pobierz_stan(self.silnik.aktualny_gracz)

    def _znajdz_indeks_karty(self, id_gracza, id_typu_karty):
        g = self.silnik.gracze[id_gracza]
        for i, k in enumerate(g.reka):
            if self._karta_na_indeks(k) == id_typu_karty:
                return i
        return -1

    def _dekoduj_akcje(self, id_gracza, numer_akcji):
        if numer_akcji < 52:
            indeks = self._znajdz_indeks_karty(id_gracza, numer_akcji)
            return 'zagraj', indeks, None, None

        elif numer_akcji < 56:
            indeks = self._znajdz_indeks_karty(id_gracza, 52)
            kolory = ['czerwony', 'zielony', 'niebieski', 'zolty']
            return 'zagraj', indeks, kolory[numer_akcji - 52], None

        elif numer_akcji < 60:
            indeks = self._znajdz_indeks_karty(id_gracza, 53)
            kolory = ['czerwony', 'zielony', 'niebieski', 'zolty']
            return 'zagraj', indeks, kolory[numer_akcji - 56], None

        elif numer_akcji == 60:
            return 'dobierz', None, None, None

        elif numer_akcji == 61:
            return 'krzycz_uno', None, None, None

        elif numer_akcji < 65:
            offset = (numer_akcji - 61)
            id_celu = (id_gracza + offset) % self.liczba_graczy
            return 'zglos_brak_uno', None, None, id_celu

        return None, None, None, None

    def wykonaj_krok(self, id_gracza, numer_akcji):
        nagroda = 0
        kara_poczatkowa = self.silnik.aktualna_kara
        ilosc_kart_przed = len(self.silnik.gracze[id_gracza].reka)

        typ_akcji, indeks_karty, wybrany_kolor, id_celu = self._dekoduj_akcje(id_gracza, numer_akcji)

        if typ_akcji == 'zagraj':
            if indeks_karty == -1:
                nagroda += self.kary_lokalne['nielegalny_ruch']
                return self.pobierz_stan(id_gracza), nagroda, False

            sukces = self.silnik.zagraj_karte(id_gracza, indeks_karty, wybrany_kolor)
            if not sukces:
                nagroda += self.kary_lokalne['nielegalny_ruch']
                return self.pobierz_stan(id_gracza), nagroda, False

            nagroda += self.kary_lokalne['zrzucenie_karty']
            if self.silnik.aktualna_kara > kara_poczatkowa:
                nagroda += self.kary_lokalne['wymuszenie_kary']

        elif typ_akcji == 'dobierz':
            if self.silnik.aktualna_kara > 0:
                self.silnik.rozlicz_kare(id_gracza, uzyj_ratunku=True)
            else:
                self.silnik.dobierz_z_talii(id_gracza)
            nagroda += self.kary_lokalne['dobranie_karty']

        elif typ_akcji == 'krzycz_uno':
            if ilosc_kart_przed <= 2:
                self.silnik.krzycz_uno(id_gracza)
                nagroda += self.kary_lokalne['poprawne_uno']
            else:
                nagroda += self.kary_lokalne['nielegalny_ruch']

        elif typ_akcji == 'zglos_brak_uno':
            sukces = self.silnik.zglos_brak_uno(id_celu)
            if sukces:
                nagroda += self.kary_lokalne['zlapany_brak_uno']
            else:
                nagroda += self.kary_lokalne['nielegalny_ruch']

        ilosc_kart_po = len(self.silnik.gracze[id_gracza].reka)
        if ilosc_kart_po > ilosc_kart_przed + 1:
            nagroda += self.kary_lokalne['zapomniane_uno']

        czy_koniec = False
        if id_gracza in self.silnik.ranking:
            miejsce = self.silnik.ranking.index(id_gracza) + 1
            nagroda += self.oblicz_nagrode_koncowa(miejsce)
            czy_koniec = True

        if len(self.silnik.ranking) >= self.liczba_graczy - 1:
            ostatni = [g.id_gracza for g in self.silnik.gracze if g.id_gracza not in self.silnik.ranking]
            if id_gracza in ostatni:
                nagroda += self.oblicz_nagrode_koncowa(self.liczba_graczy)
                czy_koniec = True

        return self.pobierz_stan(id_gracza), nagroda, czy_koniec