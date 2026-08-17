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

## Favorite classes

Right-click a class → "Add to favorites" (or "Remove from favorites"). Favorite classes appear in a dedicated section at the top of the home screen, marked with a star, and are not repeated in the section with all the other classes.
