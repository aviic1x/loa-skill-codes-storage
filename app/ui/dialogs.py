import shutil
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from app.db import slugify
from app.paths import get_user_icons_dir, resolve_class_icon


class AddClassDialog(QDialog):
    """Lets the user pick a class to add from the master catalog, instead
    of typing an arbitrary name — keeps the class list limited to real
    Lost Ark classes and makes duplicates impossible."""

    def __init__(self, parent=None, available_names: list[str] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Add Class")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.class_combo = QComboBox()
        self.class_combo.addItems(available_names or [])
        self.class_combo.currentTextChanged.connect(self._refresh_preview)
        form.addRow("Class", self.class_combo)

        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(64, 64)
        self._refresh_preview(self.class_combo.currentText())
        form.addRow("Icon", self.icon_preview)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _refresh_preview(self, name: str):
        icon_filename = f"{slugify(name)}.png" if name else None
        self.icon_preview.setPixmap(
            QIcon(str(resolve_class_icon(icon_filename))).pixmap(QSize(64, 64))
        )

    def get_result(self) -> str:
        return self.class_combo.currentText()


class ClassEditDialog(QDialog):
    def __init__(self, parent=None, name: str = "", icon_filename: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Class")
        self._icon_filename = icon_filename
        self._new_icon_source: Path | None = None

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(name)
        form.addRow("Name", self.name_edit)

        icon_row = QVBoxLayout()
        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(64, 64)
        self._refresh_preview()
        icon_row.addWidget(self.icon_preview)

        choose_btn = QPushButton("Choose icon...")
        choose_btn.clicked.connect(self._choose_icon)
        icon_row.addWidget(choose_btn)
        form.addRow("Icon", icon_row)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _refresh_preview(self):
        path = resolve_class_icon(self._icon_filename)
        self.icon_preview.setPixmap(
            QIcon(str(path)).pixmap(QSize(64, 64))
        )

    def _choose_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose icon", "", "Images (*.png *.jpg *.jpeg *.ico)"
        )
        if path:
            self._new_icon_source = Path(path)
            self.icon_preview.setPixmap(QIcon(path).pixmap(QSize(64, 64)))

    def get_result(self) -> tuple[str, str | None]:
        """Returns (name, icon_filename). Copies a newly chosen icon file
        into the persistent user icons dir, keyed by the class slug."""
        name = self.name_edit.text().strip()
        icon_filename = self._icon_filename
        if self._new_icon_source is not None:
            slug = slugify(name)
            ext = self._new_icon_source.suffix.lower()
            icon_filename = f"{slug}{ext}"
            dest = get_user_icons_dir() / icon_filename
            shutil.copyfile(self._new_icon_source, dest)
        return name, icon_filename


class SkillCodeEditDialog(QDialog):
    def __init__(
        self, parent=None, name: str = "", description: str = "", code: str = ""
    ):
        super().__init__(parent)
        self.setWindowTitle("Skill code")
        self.resize(420, 380)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(name)
        form.addRow("Name", self.name_edit)

        self.description_edit = QPlainTextEdit(description)
        self.description_edit.setFixedHeight(80)
        form.addRow("Description", self.description_edit)

        self.code_edit = QPlainTextEdit(code)
        code_font = self.code_edit.font()
        code_font.setFamily("Consolas")
        self.code_edit.setFont(code_font)
        form.addRow("Code", self.code_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_result(self) -> tuple[str, str, str]:
        return (
            self.name_edit.text().strip(),
            self.description_edit.toPlainText().strip(),
            self.code_edit.toPlainText().strip(),
        )
