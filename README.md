# LOA Skill Code Storage

App desktop leggera per salvare gli skill code delle classi di Lost Ark, organizzati per classe, con ricerca globale, classi preferite e copia rapida negli appunti.

## Dati salvati

Tutto (classi e skill code) è salvato in `%APPDATA%\LoaBuilds\loa_builds.db` (SQLite) e sopravvive a riavvii dell'app e del PC. Le icone personalizzate assegnate dall'app vengono copiate in `%APPDATA%\LoaBuilds\icons\`.

## Sviluppo

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Build dell'eseguibile

```
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller LoaBuilds.spec
```

L'eseguibile viene generato in `dist\LOA Skill Code Storage.exe`. È standalone (non richiede Python installato) e può essere copiato/spostato ovunque: i dati restano comunque in `%APPDATA%\LoaBuilds\` (il nome interno della cartella dati non è legato al nome visibile dell'app, per non dover migrare i dati già salvati a ogni rebrand).

## Aggiungere le icone delle classi

Metti i file PNG (uno per classe) nella cartella `icons/` del progetto prima della build, con nome `<slug_classe>.png` (es. `berserker.png`, `gunlancer.png`...). In alternativa puoi assegnare/cambiare l'icona di qualsiasi classe direttamente dall'app (tasto destro su una classe → "Cambia icona"). Finché un'icona non è presente, viene mostrato un placeholder generico.

## Classi preferite

Tasto destro su una classe → "Aggiungi ai preferiti" (o "Rimuovi dai preferiti"). Le classi preferite compaiono in una sezione dedicata in cima alla home, contrassegnate da una stella, e non vengono ripetute nella sezione con tutte le altre classi.
