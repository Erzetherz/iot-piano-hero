# Piano-Hero IoT Projekt (Raspberry Pi)

Ein Musik- und Rhythmusspiel nach dem Prinzip „Guitar Hero“, umgesetzt mit einem Raspberry Pi, RGB-LED und kleinem Lautsprecher.  
Die App läuft als Flask-Webserver; gespielt wird im Browser.  
Beim Drücken der Tasten werden LED-Farben geschaltet und Töne über den Lautsprecher ausgegeben.

---

## Motivation

Unsere Motivation war es, ein erstes IoT-Projekt mit dem Raspberry Pi umzusetzen und dabei grundlegende Erfahrungen mit Hard- und Software zu sammeln.  
Zuerst haben wir mit einfachen Bausteinen wie einem Piano aus Tasten und Licht gearbeitet.  
Dabei kam uns die Idee, das Projekt zu einem kleinen Spiel weiterzuentwickeln – ähnlich wie „Guitar Hero“.  
Der Spaßfaktor stand von Anfang an im Vordergrund, gleichzeitig konnten wir praxisnah lernen, wie man Hardware ansteuert und eine Weboberfläche mit dem Raspberry Pi verbindet.

---

## Funktionen

- 8 Tasten: a s d f | j k l ö (ö hat Fallback: ; oder [ auf EN-Keyboards)
- Fallende Noten (Canvas), Preview, Countdown-Start
- BPM-Schieberegler (Tempo) und Timing-Schieberegler (Perfect/Good/Miss)
- 3 Melodien mit echten Tonhöhen: Mario Overworld, Happy Birthday, Ode to Joy
- Autoplay und Playback der eigenen Performance
- RGB-LED blinkt pro Treffer, Lautsprecher spielt die jeweilige Note

---

## Benötigte Hardware

- Raspberry Pi (mit GPIO; getestet: Pi 3/4, Zero 2)
- RGB-LED, gemeinsame Anode (4-Pin)
- NPN-Transistor 2N3904 (Treiber für Lautsprecher)
- Lautsprecher 8 Ω / 1 W
- Widerstände:
  - 1 × 330 Ω (LED Rot)
  - 2 × 1 kΩ (LED Grün/Blau)
  - 1 × 1 kΩ (Basis des Transistors)
  - 1 × 330 Ω (Serie zwischen +5 V und Lautsprecher(+))
- Steckbrett + Jumperkabel
- Netzteil für den Pi

---

## Schaltung / Steckbrett (BCM-Pins)

### RGB-LED (gemeinsame Anode)

- Anode → +3.3 V (Pin 1/17)
- Rot → 330 Ω → GPIO17 (Pin 11)
- Grün → 1 kΩ → GPIO27 (Pin 13)
- Blau → 1 kΩ → GPIO22 (Pin 15)

Hinweis: Gemeinsame Anode an 3.3 V ⇒ GPIO „sinkt“ Strom (LOW = an). Das ist für den Pi sicher.

### Lautsprecher mit 2N3904

- GPIO18 (Pin 12) → 1 kΩ → Basis
- Emitter → GND (Pin 6/9/14 …)
- Kollektor → Lautsprecher (-)
- +5 V (Pin 2/4) → 330 Ω → Lautsprecher (+)

Wichtig: Gemeinsame Masse (GND) verbinden: Pi-GND ↔ LED-GND ↔ Transistor-Emitter.

---

## Software-Requirements

Python 3 + folgende Pakete:

```txt
Flask==3.0.0
RPi.GPIO==0.7.1
```

---

## Installation

```bash
sudo apt update
sudo apt install -y python3-pip git
pip3 install -r requirements.txt
```

## Start

```bash
python3 src/piano_hero.py
```

## Im Browser:

http://<IP-des-ausführenden-Gerätes>:5000

## Steuerung

Tasten: a s d f | j k l ö (Fallbacks ; oder [ für „ö“)

Vorschau (komplette Melodie), Start (Countdown)

BPM und Timing per Slider einstellbar

## Troubleshooting

Start klemmt nach Countdown? Während Countdown keine Änderungen (BPM/Melodie). UI ist gesperrt; notfalls Seite neu laden (F5).

Kein Ton oder leise? Transistor-Schaltung prüfen; duty in tone_env() (25–40 %) anpassen.

LED reagiert nicht? Anode an 3.3 V, Widerstände korrekt, Pins 17/27/22.

ö funktioniert nicht? ; oder [ verwenden.

---

## Technische Details

- **GPIO-Setup**: Pins für RGB-LED (17, 27, 22) und Lautsprecher (18) werden mit PWM initialisiert.  
- **LED-Funktionen**: Kleine Helfer-Funktionen schalten die LED-Farben passend zu den gedrückten Tasten.  
- **Tonerzeugung**: Der Lautsprecher bekommt Töne über PWM mit einer kurzen Hüllkurve (Attack/Sustain/Release), damit die Klänge sauberer sind.  
- **Frequenz-Tabelle (N)**: Enthält Notennamen (z. B. C4, E5) und deren Frequenzen in Hertz. So lassen sich Melodien leichter notieren.  
- **Melodien**: Sind als Listen von (Note, Dauer) gespeichert. `"R"` steht für eine Pause.  
- **Lane-Mapping**: Jede Note wird einer der 8 Tasten (a s d f | j k l ö) zugeordnet.  
- **Sequenz-Umrechnung**: Aus Beats per Minute (BPM) werden Millisekunden berechnet. So weiß das Frontend, wann eine Note erscheint.  
- **Flask-Routen**: Stellen eine kleine API bereit – z. B. `/chart` (liefert die Noten), `/preview` (spielt eine Melodie automatisch ab) oder `/beep` (spielt einen Ton ab).  
- **Frontend (JavaScript)**: Zeichnet mit Canvas die fallenden Noten und prüft die Tastatureingaben.  
- **Scoring**: Timing wird bewertet in Perfect / Good / Miss. Das Zeitfenster kann per Schieberegler eingestellt werden.  
- **Countdown & UI-Lock**: Verhindert, dass das Spiel mehrfach gestartet wird oder sich während des Countdowns verstellt.




