from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import db
from app.paths import resolve_class_icon
from app.ui.dialogs import SkillCodeEditDialog
from app.ui.widgets import SkillCodeCard


class ClassDetailView(QWidget):
    back_requested = Signal()

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.class_id: int | None = None

        outer = QVBoxLayout(self)

        header = QHBoxLayout()
        back_btn = QPushButton("← Home")
        back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(back_btn)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        header.addWidget(self.icon_label)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(self.title_label)
        header.addStretch()

        add_btn = QPushButton("+ Aggiungi skill code")
        add_btn.clicked.connect(self._add_skill_code)
        header.addWidget(add_btn)

        outer.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self._container = QWidget()
        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.addStretch()
        self.scroll.setWidget(self._container)
        outer.addWidget(self.scroll)

    def load(self, class_id: int):
        self.class_id = class_id
        class_row = db.get_class(self.conn, class_id)
        if not class_row:
            return
        self.title_label.setText(class_row["name"])
        self.icon_label.setPixmap(
            QIcon(str(resolve_class_icon(class_row["icon_filename"]))).pixmap(QSize(40, 40))
        )
        self.refresh()

    def refresh(self):
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for skill_code_row in db.list_skill_codes(self.conn, self.class_id):
            card = SkillCodeCard(skill_code_row, self._container)
            card.edit_requested.connect(self._edit_skill_code)
            card.delete_requested.connect(self._delete_skill_code)
            self._list_layout.addWidget(card)

        self._list_layout.addStretch()

    def _add_skill_code(self):
        dialog = SkillCodeEditDialog(self)
        if dialog.exec():
            name, description, code = dialog.get_result()
            if not name or not code:
                return
            db.add_skill_code(self.conn, self.class_id, name, description, code)
            self.refresh()

    def _edit_skill_code(self, skill_code_id: int):
        rows = db.list_skill_codes(self.conn, self.class_id)
        row = next((r for r in rows if r["id"] == skill_code_id), None)
        if not row:
            return
        dialog = SkillCodeEditDialog(
            self, name=row["name"], description=row["description"], code=row["code"]
        )
        if dialog.exec():
            name, description, code = dialog.get_result()
            if not name or not code:
                return
            db.update_skill_code(self.conn, skill_code_id, name, description, code)
            self.refresh()

    def _delete_skill_code(self, skill_code_id: int):
        answer = QMessageBox.question(
            self,
            "Elimina skill code",
            "Eliminare questo skill code?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            db.delete_skill_code(self.conn, skill_code_id)
            self.refresh()
