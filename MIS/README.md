# MIS – Memory Identity Stratified

MIS este un sistem cognitiv stratificat, nu un chatbot simplu. Aplicația implementează bucla:

**Mediu → Percepție → Memorie → Emoție → Identitate → Decizie → Acțiune → Experiență nouă**

și, în conversație:

**Input utilizator → Percepție → Recuperare memorie → Evaluare emoțională → Influență identitară → Decizie → Răspuns → Actualizare memorie**

## Ce face aplicația

- memorează interacțiunile ca **experiențe structurale**;
- menține o stare internă emoțională;
- construiește o identitate din memorie (stabilă, dar evolutivă);
- actualizează scopuri active și prioritizează comportamentul;
- decide tonul/profunzimea/acțiunea înainte de generarea răspunsului.

## Structură proiect

```text
MIS/
├── main.py
├── gui_app.py
├── core/
├── database/
├── config/
├── utils/
├── data/
├── requirements.txt
└── README.md
```

## Instalare și rulare

1. Creează mediu virtual:
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
   - Linux/macOS: `python -m venv .venv && source .venv/bin/activate`
2. Instalează dependențe: `pip install -r requirements.txt`
3. Rulează aplicația: `python main.py`

La prima rulare, baza SQLite este creată automat în `data/mis.db`.

## Construire executabil (.exe)

1. Activează mediul virtual.
2. Rulează:

```bash
pyinstaller --noconfirm --onefile --windowed --name MIS main.py
```

3. Executabilul apare în `dist/MIS.exe`.

## Observații

- Interfața și răspunsurile sunt în limba română.
- Codul intern este în limba engleză.
- `AIConnector` folosește implicit mod simulare (`mock`) și poate fi extins ulterior cu API real.
