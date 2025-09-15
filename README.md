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
