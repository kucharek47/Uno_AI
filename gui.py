import pygame
import sys
from gra_w_uno import srodowisko_uno
from bot import agent_dqn

def uruchom_gui():
    pygame.init()
    w = 1200
    h = 800
    okno = pygame.display.set_mode((w, h))
    pygame.display.set_caption("UNO vs AI")

    czcionka = pygame.font.SysFont("arial", 28, bold=True)
    czcionka_mala = pygame.font.SysFont("arial", 18, bold=True)

    max_graczy = 5
    srodowisko = srodowisko_uno(max_graczy)
    wielkosc_wejscia = 170 + (max_graczy - 1) * 3
    wielkosc_wyjscia = 63 + max_graczy

    agent = agent_dqn(wielkosc_wejscia, wielkosc_wyjscia)
    try:
        agent.wczytaj_model("model_uno_v10.pth")
    except Exception:
        pass
    agent.epsilon = 0.0

    kolory = {
        'czerwony': (220, 50, 50),
        'zielony': (50, 180, 50),
        'niebieski': (50, 50, 220),
        'zolty': (230, 200, 0),
        None: (40, 40, 40),
        'tlo': (20, 80, 40),
        'stol': (30, 110, 50),
        'bialy': (255, 255, 255),
        'czarny': (0, 0, 0)
    }

    zegar = pygame.time.Clock()
    ostatni_ruch = 0
    wybor_koloru_indeks = None

    btn_uno = pygame.Rect(w - 150, h - 150, 120, 40)
    btn_koniec = pygame.Rect(w - 150, h - 90, 120, 40)

    def rysuj_karte(x, y, k, ukryta=False):
        rect = pygame.Rect(x, y, 80, 120)
        if ukryta:
            pygame.draw.rect(okno, kolory[None], rect, border_radius=8)
            pygame.draw.rect(okno, kolory['bialy'], rect, 2, border_radius=8)
            tekst = czcionka.render("UNO", True, kolory['bialy'])
            okno.blit(tekst, (x + 10, y + 45))
        else:
            c = kolory[k.kolor]
            pygame.draw.rect(okno, c, rect, border_radius=8)
            pygame.draw.rect(okno, kolory['bialy'], rect, 2, border_radius=8)
            wartosc = str(k.wartosc)
            if wartosc == 'zmiana_kierunku': wartosc = "<->"
            elif wartosc == 'zmiana_koloru': wartosc = "KOLOR"
            tekst = czcionka_mala.render(wartosc, True, kolory['bialy'])
            okno.blit(tekst, (x + 5, y + 5))
            okno.blit(tekst, (x + 5, y + 95))
        return rect

    dziala = True
    while dziala:
        okno.fill(kolory['tlo'])
        pygame.draw.ellipse(okno, kolory['stol'], (150, 100, w - 300, h - 350))

        czy_koniec = len(srodowisko.silnik.ranking) > 0
        id_gracza = srodowisko.silnik.aktualny_gracz

        if not czy_koniec and id_gracza != 0:
            obecny_czas = pygame.time.get_ticks()
            if obecny_czas - ostatni_ruch > 1500:
                stan = srodowisko.pobierz_stan(id_gracza)
                maska = srodowisko.pobierz_maske_akcji(id_gracza)
                akcja = agent.wybierz_akcje(stan, maska)
                srodowisko.wykonaj_krok(id_gracza, akcja)
                ostatni_ruch = pygame.time.get_ticks()

        pozycje_botow = [(80, h // 2 - 100), (w // 3, 40), (2 * w // 3, 40), (w - 160, h // 2 - 100)]
        for i in range(1, srodowisko.liczba_graczy):
            x, y = pozycje_botow[i - 1]
            karty_bota = len(srodowisko.silnik.gracze[i].reka)
            tekst_bota = czcionka.render(f"Bot {i}", True, kolory['bialy'])
            okno.blit(tekst_bota, (x, y - 35))
            for j in range(karty_bota):
                przesuniecie = min(20, 100 / max(1, karty_bota))
                rysuj_karte(x + j * przesuniecie, y, None, True)

        stos_x = w // 2 - 100
        stos_y = h // 2 - 120
        if srodowisko.silnik.stos:
            rysuj_karte(stos_x, stos_y, srodowisko.silnik.stos[-1])

        talia_rect = rysuj_karte(stos_x + 120, stos_y, None, True)

        if srodowisko.silnik.aktualny_kolor:
            pygame.draw.circle(okno, kolory[srodowisko.silnik.aktualny_kolor], (w // 2, h // 2 + 50), 30)

        reka_rects = []
        reka = srodowisko.silnik.gracze[0].reka
        szerokosc_reki = len(reka) * 90
        start_x = w // 2 - szerokosc_reki // 2
        if start_x < 50: start_x = 50
        odstep = min(90, (w - 100) / max(1, len(reka)))

        for i, k in enumerate(reka):
            x = start_x + i * odstep
            r = rysuj_karte(x, h - 180, k)
            reka_rects.append((r, i))

        pygame.draw.rect(okno, kolory['niebieski'], btn_uno, border_radius=5)
        okno.blit(czcionka_mala.render("KRZYCZ UNO", True, kolory['bialy']), (btn_uno.x + 5, btn_uno.y + 10))

        pygame.draw.rect(okno, kolory['czerwony'], btn_koniec, border_radius=5)
        okno.blit(czcionka_mala.render("ZAKONCZ TURE", True, kolory['bialy']), (btn_koniec.x + 5, btn_koniec.y + 10))

        kolory_btn = []
        if wybor_koloru_indeks is not None:
            cx, cy = w // 2, h // 2 - 10
            d_c = pygame.Rect(cx - 100, cy, 40, 40)
            d_z = pygame.Rect(cx - 50, cy, 40, 40)
            d_n = pygame.Rect(cx, cy, 40, 40)
            d_y = pygame.Rect(cx + 50, cy, 40, 40)
            pygame.draw.rect(okno, kolory['czerwony'], d_c)
            pygame.draw.rect(okno, kolory['zielony'], d_z)
            pygame.draw.rect(okno, kolory['niebieski'], d_n)
            pygame.draw.rect(okno, kolory['zolty'], d_y)
            kolory_btn = [(d_c, 'czerwony'), (d_z, 'zielony'), (d_n, 'niebieski'), (d_y, 'zolty')]

        status = f"Tura: {'Ciebie' if id_gracza == 0 else f'Bota {id_gracza}'}"
        if czy_koniec:
            status = "WYGRANA!" if srodowisko.silnik.ranking[0] == 0 else f"WYGRAL BOT {srodowisko.silnik.ranking[0]}"
        tekst_status = czcionka.render(status, True, kolory['bialy'])
        okno.blit(tekst_status, (20, 20))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                dziala = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not czy_koniec and id_gracza == 0:
                x, y = event.pos
                maska = srodowisko.pobierz_maske_akcji(0)

                if wybor_koloru_indeks is not None:
                    for rect, kolor_w in kolory_btn:
                        if rect.collidepoint(x, y):
                            k = reka[wybor_koloru_indeks]
                            baza = 52 if k.wartosc == 'zmiana_koloru' else 56
                            offset = ['czerwony', 'zielony', 'niebieski', 'zolty'].index(kolor_w)
                            id_akcji = baza + offset
                            if maska[id_akcji] == 1:
                                srodowisko.wykonaj_krok(0, id_akcji)
                            wybor_koloru_indeks = None
                            break
                else:
                    if btn_uno.collidepoint(x, y) and maska[61] == 1:
                        srodowisko.wykonaj_krok(0, 61)
                    elif btn_koniec.collidepoint(x, y) and maska[62] == 1:
                        srodowisko.wykonaj_krok(0, 62)
                    elif talia_rect.collidepoint(x, y) and maska[60] == 1:
                        srodowisko.wykonaj_krok(0, 60)
                    else:
                        for rect, indeks in reversed(reka_rects):
                            if rect.collidepoint(x, y):
                                k = reka[indeks]
                                if k.kolor is None:
                                    wybor_koloru_indeks = indeks
                                else:
                                    id_akcji = srodowisko._karta_na_indeks(k)
                                    if maska[id_akcji] == 1:
                                        srodowisko.wykonaj_krok(0, id_akcji)
                                break

        zegar.tick(30)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    uruchom_gui()