import RPi.GPIO as GPIO
from time import sleep
from enum import Enum

# PINY RaspberryPi
DATA = 20
LE = 22
CLK = 21
OE1 = 23
OE2 = 24
OE3 = 25
SW1 = 26
SW2 = 27

CZAS_ZIELONE = 10  # czas trwania światła zielonego
CZAS_ZOLTE = 2  # czas trwania światła żółtego
CZAS_MIGANIE = 0.2  # interwał między mignęciami na światłach dla pieszych
CZAS_GOTOWOSC = 1  # czas trwania światła czerwone+żółte
CZAS_CZERWONE = 3 # czas trwania światła czerwonego na wszystkich sygnalizatorach

SWIATLO_CZERWONE = 1,  # światło czerwone
SWIATLO_ZOLTE = 2,  # światło zółte
SWIATLO_ZIELONE = 3,  # światło zielone
SWIATLO_STRZALKA = 4,  # śtrzałka warunkowa
SWIATLO_GOTOWOSC = 5,  # światło czerwone+zolte
SWIATLO_OFF = 6  # światło wyłączone

INTERWAL = 0.5

PRZYCISK_WCISNETY = 0

SYMULACJA = 1
CHOINKA = 2
MANUALNY = 3

WSZYSTKIE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]  # numery sygnalizatorow
rejestr = [0] * 48  # reprezentacja rejestru 48-bitowego

# CZERWONE[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym
CZERWONE = [20, 24, 22, 27, 15, 16, 30, 0, 4, 12, 8, 47, 32, 7, 44, 38, 41, 36]
# ZOLTE[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym (jeśli sygnalizator nie ma zółtego swiatla to -1)
ZOLTE = [-1, -1, -1, -1, -1, 17, 29, 1, -1, -1, 9, 46, 33, -1, -1, -1, -1, -1]
# ZIELONE[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym
ZIELONE = [21, 25, 23, 26, 14, 18, 28, 2, 5, 13, 10, 45, 34, 6, 43, 39, 42, 37]
# STRZALKA[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym (jeśli sygnalizator nie ma strzałki to -1)
STRZALKA = [-1, -1, -1, -1, -1, 19, -1, 3, -1, -1, 11, -1, 35, -1, -1, -1, -1, -1]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(DATA, GPIO.OUT)
GPIO.setup(LE, GPIO.OUT)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(OE1, GPIO.OUT)
GPIO.setup(OE2, GPIO.OUT)
GPIO.setup(OE3, GPIO.OUT)

GPIO.setup(SW1, GPIO.IN)
GPIO.setup(SW2, GPIO.IN)


# funkcja zapala swiatła na płytce zgodnie z zawartością ustawioną w rejestrze
def zapal():
    GPIO.output(OE1, GPIO.HIGH)
    GPIO.output(OE2, GPIO.HIGH)
    GPIO.output(OE3, GPIO.HIGH)

    for stan in rejestr[::-1]:
        GPIO.output(DATA, stan)
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(CLK, GPIO.HIGH)

    GPIO.output(LE, GPIO.LOW)
    GPIO.output(LE, GPIO.HIGH)

    GPIO.output(OE1, GPIO.LOW)
    GPIO.output(OE2, GPIO.LOW)
    GPIO.output(OE3, GPIO.LOW)
    return


# funkcja ustawia stan światła w rejestrze na podstawie numeru sygnalizatora i podanego stanu
def ustaw_swiatlo(nr_sygnalizatora, stan):
    indeks_czerwone = CZERWONE[nr_sygnalizatora]
    indeks_zolte = ZOLTE[nr_sygnalizatora]
    indeks_zielone = ZIELONE[nr_sygnalizatora]
    indeks_strzalka = STRZALKA[nr_sygnalizatora]

    # wyłączamy wszystkie światła
    rejestr[indeks_czerwone] = 0
    if indeks_zolte >= 0:
        rejestr[indeks_zolte] = 0
    rejestr[indeks_zielone] = 0
    if indeks_strzalka >= 0:
        rejestr[indeks_czerwone] = 0

    if stan == SWIATLO_OFF:
        return

    # ustawiamy odpowiednie światło jako włączone
    if stan == SWIATLO_CZERWONE:
        rejestr[indeks_czerwone] = 1
    elif stan == SWIATLO_ZOLTE:
        if indeks_zolte >= 0:
            rejestr[indeks_zolte] = 1
    elif stan == SWIATLO_ZIELONE:
        rejestr[indeks_zielone] = 1
    elif stan == SWIATLO_STRZALKA:
        if indeks_strzalka >= 0:
            rejestr[indeks_strzalka] = 1
            rejestr[indeks_czerwone] = 1
    elif stan == SWIATLO_GOTOWOSC:
        if indeks_zolte >= 0:
            rejestr[indeks_zolte] = 1
            rejestr[indeks_czerwone] = 1
    return


# funkcja ustawia 'stan' na sygnalizatorach, których numery znajdują się w tablicy 'sygnalizatory'
def ustaw_sygnaliaztory(sygnalizatory, stan):
    for sygnalizator in sygnalizatory:
        ustaw_swiatlo(sygnalizator, stan)
    return


# funkcja wywołuje miganie zielonych świateł na sygnalizatorach znajdujących się w tablicy 'sygnalizatory'
def migaj(sygnalizatory):
    powtorzenia = CZAS_ZOLTE // (2 * CZAS_MIGANIE)
    for _ in range(powtorzenia):
        ustaw_sygnaliaztory(sygnalizatory, SWIATLO_OFF)
        zapal()
        przerwij = czekaj(CZAS_MIGANIE)
        if przerwij:
            return True
        ustaw_sygnaliaztory(sygnalizatory, SWIATLO_ZIELONE)
        zapal()
        przerwij = czekaj(CZAS_MIGANIE)
        if przerwij:
            return True
    return False


def czytaj_przycisk(pin):
    return GPIO.input(pin)

# funkcja czeka przez podany czas chyba, że zostanie przerwana poprzez nacisniecie przycisku
def czekaj(czas):
    powtorzenia = int(czas // INTERWAL)
    for _ in range(powtorzenia):
        sleep(INTERWAL)
        przycisk = czytaj_przycisk(SW1)
        if przycisk == PRZYCISK_WCISNETY:
            return True
    return False

# obieg pojedynczej fazy swiatel
def uruchom_faze_swiatel(samochody, piesi, samochody_strzalka):
    ustaw_sygnaliaztory(samochody, SWIATLO_GOTOWOSC)
    zapal()
    przerwij = czekaj(CZAS_GOTOWOSC)
    if przerwij:
        return True
    ustaw_sygnaliaztory(samochody, SWIATLO_ZIELONE)
    ustaw_sygnaliaztory(piesi, SWIATLO_ZIELONE)
    ustaw_sygnaliaztory(samochody_strzalka, SWIATLO_STRZALKA)
    zapal()
    przerwij = czekaj(CZAS_ZIELONE)
    if przerwij:
        return True
    ustaw_sygnaliaztory(samochody_strzalka, SWIATLO_CZERWONE)
    ustaw_sygnaliaztory(samochody, SWIATLO_ZOLTE)
    zapal()
    przerwij = migaj(piesi)
    if przerwij:
        return True
    ustaw_sygnaliaztory(samochody, SWIATLO_CZERWONE)
    ustaw_sygnaliaztory(piesi, SWIATLO_CZERWONE)
    zapal()
    przerwij = czekaj(CZAS_CZERWONE)
    if przerwij:
        return True

    return False


# pojedyńczy obieg symulacji świateł drogowych
def symuluj_swiatla():
    ustaw_sygnaliaztory(WSZYSTKIE, SWIATLO_CZERWONE)

    samochody = [7, 10]
    piesi = [0, 1, 2, 3, 14, 15, 16, 17]
    samochody_strzalka = [5, 12]
    przerwij = uruchom_faze_swiatel(samochody, piesi, samochody_strzalka)
    if przerwij:
        return CHOINKA

    samochody = [5, 12]
    piesi = [4, 8, 9, 13]
    samochody_strzalka = [7, 10]
    przerwij = uruchom_faze_swiatel(samochody, piesi, samochody_strzalka)
    if przerwij:
        return CHOINKA

    samochody = [6,11]
    piesi = []
    samochody_strzalka = [7,10]
    przerwij = uruchom_faze_swiatel(samochody, piesi, samochody_strzalka)
    if przerwij:
        return CHOINKA

    return SYMULACJA


def choinka():
    for sygnalizator in WSZYSTKIE:
        ustaw_sygnaliaztory(sygnalizator, SWIATLO_ZIELONE)
    zapal()
    status = czekaj(CZAS_ZOLTE)
    if status:
        return MANUALNY
    for sygnalizator in WSZYSTKIE:
        ustaw_sygnaliaztory(sygnalizator, SWIATLO_ZOLTE)
    zapal()
    status = czekaj(CZAS_ZOLTE)
    if status:
        return MANUALNY
    for sygnalizator in WSZYSTKIE:
        ustaw_sygnaliaztory(sygnalizator, SWIATLO_CZERWONE)
    zapal()
    status = czekaj(CZAS_ZOLTE)
    if status:
        return MANUALNY

    return CHOINKA

def manualny():
    wlaczone = 0
    koniec = False
    ustaw_sygnaliaztory(WSZYSTKIE, SWIATLO_OFF)
    zapal()

    while not koniec:
        przycisk = czytaj_przycisk(SW2)
        if przycisk == PRZYCISK_WCISNETY:
            if wlaczone==48:
                wlaczone = 0
            else:
                wlaczone += 1
            rejestr = ([1] * wlaczone) + ([0] * (48 - wlaczone))
            zapal()
        przycisk = czytaj_przycisk(SW1)
        if przycisk == PRZYCISK_WCISNETY:
            koniec = True

    return SYMULACJA

    
    

def main():
    tryb = SYMULACJA
    while True:
        if tryb == SYMULACJA:
            tryb = symuluj_swiatla()
        if tryb == CHOINKA:
            tryb = choinka()
        if tryb == MANUALNY:
            tryb = manualny()


if __name__ == "__main__":
    main()
