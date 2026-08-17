# LOA Skill Code Storage

Lightweight desktop app for saving Lost Ark class skill codes, organized by class, with global search, favorite classes, and quick copy to clipboard.

## Saved data

Everything (classes and skill codes) is saved in `%APPDATA%\LoaBuilds\loa_builds.db` (SQLite) and survives app restarts and PC reboots. Custom icons assigned from the app are copied to `%APPDATA%\LoaBuilds\icons\`.

## Development

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Building the executable

```
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller LoaBuilds.spec
```

The executable is generated in `dist\LOA Skill Code Storage.exe`. It's standalone (no Python installation required) and can be copied/moved anywhere: data still lives in `%APPDATA%\LoaBuilds\` (the internal data folder name isn't tied to the app's display name, so already-saved data never needs migrating on a rebrand).

## Adding class icons

Drop PNG files (one per class) into the project's `icons/` folder before building, named `<class_slug>.png` (e.g. `berserker.png`, `gunlancer.png`...). Alternatively, you can assign/change any class's icon directly from the app (right-click a class → "Change icon"). Until an icon is present, a generic placeholder is shown.

## Home screen and adding classes

The home screen only lists classes that already have at least one saved skill code, to keep it readable — it won't clutter your view with the full Lost Ark roster. Use the prominent "+ Add Class" button (top-right, above the class grid) to add a class: pick it from a dropdown of classes you don't have yet (this list comes from a fixed catalog in `app/seed_data.py`, so there's never a duplicate or a made-up name). Picking one takes you straight to its page to save your first skill code; it stays hidden from the home screen until it has at least one.

Classes aren't creatable with an arbitrary name — when a new class is released in-game, the app's catalog (`ALL_CLASSES` in `app/seed_data.py`) needs to be updated and the app re-released.

## Favorite classes

Right-click a class → "Add to favorites" (or "Remove from favorites"). Favorite classes appear in a dedicated section at the top of the home screen, marked with a star, and are not repeated in the section with all the other classes.
