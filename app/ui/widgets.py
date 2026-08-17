from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)

from app.paths import resolve_class_icon


class ClassTile(QToolButton):
    clicked_id = Signal(int)
    rename_requested = Signal(int)
    change_icon_requested = Signal(int)
    delete_requested = Signal(int)
    favorite_toggled = Signal(int)

    def __init__(self, class_row, parent=None):
        super().__init__(parent)
        self.class_id = class_row["id"]
        self.is_favorite = bool(class_row["is_favorite"])
        label = f"★ {class_row['name']}" if self.is_favorite else class_row["name"]
        self.setText(label)
        self.setIcon(QIcon(str(resolve_class_icon(class_row["icon_filename"]))))
        self.setIconSize(QSize(64, 64))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setFixedSize(112, 112)
        self.setCursor(Qt.PointingHandCursor)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clicked.connect(lambda: self.clicked_id.emit(self.class_id))
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        favorite_action = menu.addAction(
            "Remove from favorites" if self.is_favorite else "Add to favorites"
        )
        menu.addSeparator()
        rename_action = menu.addAction("Rename")
        icon_action = menu.addAction("Change icon")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.mapToGlobal(pos))
        if action == favorite_action:
            self.favorite_toggled.emit(self.class_id)
        elif action == rename_action:
            self.rename_requested.emit(self.class_id)
        elif action == icon_action:
            self.change_icon_requested.emit(self.class_id)
        elif action == delete_action:
            self.delete_requested.emit(self.class_id)


class AddClassTile(QToolButton):
    clicked_add = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("+ Add\nclass")
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setFixedSize(112, 112)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QToolButton { border: 2px dashed #5a6072; border-radius: 10px; color: #9aa2b1; }"
            "QToolButton:hover { border-color: #7c8299; color: #ffffff; }"
        )
        self.clicked.connect(self.clicked_add.emit)


class SkillCodeCard(QFrame):
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, skill_code_row, parent=None):
        super().__init__(parent)
        self.skill_code_id = skill_code_row["id"]
        self.code = skill_code_row["code"]

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("SkillCodeCard")

        layout = QVBoxLayout(self)

        name_label = QLabel(skill_code_row["name"])
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(name_label)

        if skill_code_row["description"]:
            desc_label = QLabel(skill_code_row["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #9aa2b1;")
            layout.addWidget(desc_label)

        button_row = QHBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self._copy_code)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.skill_code_id))
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.skill_code_id))

        button_row.addWidget(self.copy_btn)
        button_row.addWidget(edit_btn)
        button_row.addWidget(delete_btn)
        button_row.addStretch()
        layout.addLayout(button_row)

    def _copy_code(self):
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(self.code)
        self.copy_btn.setText("Copied!")
        QTimer.singleShot(1000, lambda: self.copy_btn.setText("Copy"))
