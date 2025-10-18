try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    # Symulacja RPi.GPIO, żeby kod działał nda Windows (na laborce mozna usunac)
    class GPIO:
        BCM = BOARD = OUT = IN = HIGH = LOW = None

        @staticmethod
        def setmode(mode): print(f"[GPIO SIM] setmode({mode})")

        @staticmethod
        def setup(pin, mode): print(f"[GPIO SIM] setup(pin={pin}, mode={mode})")

        @staticmethod
        def output(pin, value): print(f"[GPIO SIM] output(pin={pin}, value={value})")

        @staticmethod
        def cleanup(): print("[GPIO SIM] cleanup()")

        @staticmethod
        def setwarnings(flag): print("[GPIO SIM] setwarnings(flag)")
from time import sleep
from enum import Enum

# STAŁE
DATA = 20
LE = 22
CLK = 21
OE1 = 23
OE2 = 24
OE3 = 25
SW1 = 26
SW2 = 27

CZAS_ZIELONE = 10   # czas trwania światła zielonego
CZAS_ZOLTE = 2      # czas trwania światła żółtego
CZAS_MIGANIE = 0.2  # interwał między mignęciami na światłach dla pieszych
CZAS_GOTOWOSC = 1   # czas trwania światła czerwone+żółte

CZERWONE = 1,  # światło czerwone
ZOLTE = 2,  # światło zółte
ZIELONE = 3,  # światło zielone
STRZALKA = 4,  # śtrzałka warunkowa
GOTOWOSC = 5,  # światło czerwone+zolte
OFF = 6  # światło wyłączone


wszystkie = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]  # numery sygnalizatorow
rejestr = [0] * 48  # reprezentacja rejestru 48-bitowego

# czerwone[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym
czerwone = [20, 24, 22, 27, 15, 16, 30, 0, 4, 12, 8, 47, 32, 7, 44, 38, 41, 36]
# zolte[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym (jeśli sygnalizator nie ma zółtego swiatla to -1)
zolte = [-1, -1, -1, -1, -1, 17, 29, 1, -1, -1, 9, 46, 33, -1, -1, -1, -1, -1]
# zielone[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym
zielone = [21, 25, 23, 26, 14, 18, 28, 2, 5, 13, 10, 45, 34, 6, 43, 39, 42, 37]
# strzalka[numer_sygnalizatora] = nr_bitu_w_rejestrze_48-bitowym (jeśli sygnalizator nie ma strzałki to -1)
strzalka = [-1, -1, -1, -1, -1, 19, -1, 3, -1, -1, 11, -1, 35, -1, -1, -1, -1, -1]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(DATA, GPIO.OUT)
GPIO.setup(LE, GPIO.OUT)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(OE1, GPIO.OUT)
GPIO.setup(OE2, GPIO.OUT)
GPIO.setup(OE3, GPIO.OUT)

GPIO.output(SW1, GPIO.IN)
GPIO.output(SW2, GPIO.IN)

GPIO.output(22, GPIO.LOW)

GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.HIGH)
GPIO.output(25, GPIO.HIGH)


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
    indeks_czerwone = czerwone[nr_sygnalizatora]
    indeks_zolte = zolte[nr_sygnalizatora]
    indeks_zielone = zielone[nr_sygnalizatora]
    indeks_strzalka = strzalka[nr_sygnalizatora]

    # wyłączamy wszystkie światła
    rejestr[indeks_czerwone] = 0
    if indeks_zolte >= 0:
        rejestr[indeks_zolte] = 0
    rejestr[indeks_zielone] = 0
    if indeks_strzalka >= 0:
        rejestr[indeks_czerwone] = 0

    if stan == OFF:
        return

    # ustawiamy odpowiednie światło jako włączone
    if stan == CZERWONE:
        rejestr[indeks_czerwone] = 1
    elif stan == ZOLTE:
        if indeks_zolte >= 0:
            rejestr[indeks_zolte] = 1
    elif stan == ZIELONE:
        rejestr[indeks_zielone] = 1
    elif stan == STRZALKA:
        if indeks_strzalka >= 0:
            rejestr[indeks_strzalka] = 1
    elif stan == GOTOWOSC:
        if indeks_zolte >= 0:
            rejestr[indeks_zolte] = 1
            rejestr[indeks_czerwone] = 1
    return

# funkcja ustawia 'stan' na sygnalizatorach, których numery znajdują się w tablicy 'sygnalizatory'
def ustaw_sygnaliaztory(sygnalizatory, stan):
    for sygnalizator in sygnalizatory:
        ustaw_swiatlo(sygnalizator, stan)
    return

# funkcja wywołuje miganie zielonych świateł na sygnalizatorach znajdujących się w tablicty 'sygnalizatory'
def migaj(sygnalizatory):
    powtorzenia = CZAS_ZOLTE // (2 * CZAS_MIGANIE)
    for _ in range(powtorzenia):
        ustaw_sygnaliaztory(sygnalizatory, OFF)
        zapal()
        sleep(CZAS_MIGANIE)
        ustaw_sygnaliaztory(sygnalizatory, ZIELONE)
        zapal()
        sleep(CZAS_MIGANIE)
    return 

# pojedyńczy obieg symulacji świateł drogowych
def symuluj_swiatla():
    ustaw_sygnaliaztory(wszystkie, CZERWONE)

    ustaw_sygnaliaztory([7, 10], GOTOWOSC)
    zapal()
    sleep(CZAS_GOTOWOSC)
    ustaw_sygnaliaztory([0, 1, 2, 3, 7, 10, 14, 15, 16, 17], ZIELONE)
    ustaw_sygnaliaztory([5, 12], STRZALKA)
    zapal()

    sleep(CZAS_ZIELONE)

    ustaw_sygnaliaztory([5, 12], CZERWONE)
    ustaw_sygnaliaztory([7, 10], ZOLTE)
    migaj([0, 1, 2, 3, 14, 15, 16, 17])

    ustaw_sygnaliaztory([0, 1, 2, 3, 7, 10, 14, 15, 16, 17], CZERWONE)
    ustaw_sygnaliaztory([5, 12], GOTOWOSC)
    zapal()

    sleep(CZAS_GOTOWOSC)
    ustaw_sygnaliaztory([4, 5, 8, 9, 12, 13], ZIELONE)
    zapal()

    sleep(CZAS_ZIELONE)

    ustaw_sygnaliaztory([5, 12], ZOLTE)
    migaj([4, 8, 9, 13])

    ustaw_sygnaliaztory([4, 5, 8, 9, 12, 13], CZERWONE)
    ustaw_sygnaliaztory([6, 11], GOTOWOSC)
    zapal()

    sleep(CZAS_GOTOWOSC)
    ustaw_sygnaliaztory([6, 11], ZIELONE)
    ustaw_sygnaliaztory([7, 10], STRZALKA)
    zapal()

    sleep(CZAS_ZIELONE)

    ustaw_sygnaliaztory([7, 10], CZERWONE)
    ustaw_sygnaliaztory([6, 11], ZOLTE)
    zapal()
    sleep(CZAS_ZOLTE)

    ustaw_sygnaliaztory([6, 11], CZERWONE)
    zapal()

    return


def main():
    while True:
        symuluj_swiatla()


if __name__ == "__main__":
    main()
