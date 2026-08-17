from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import db
from app.ui.dialogs import AddClassDialog, ClassEditDialog
from app.ui.widgets import ClassTile

COLUMNS = 6
SECTION_LABEL_STYLE = "font-weight: bold; font-size: 14px; color: #c7cbd6; margin-top: 6px;"
ADD_CLASS_BUTTON_STYLE = (
    "QPushButton { background-color: #3f6fd1; color: white; font-weight: bold;"
    " padding: 8px 18px; border-radius: 6px; font-size: 13px; }"
    "QPushButton:hover { background-color: #4c7fe6; }"
    "QPushButton:disabled { background-color: #3a3f4b; color: #7c8299; }"
)


class HomeView(QScrollArea):
    class_opened = Signal(int)

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWidgetResizable(True)

        self._container = QWidget()
        outer = QVBoxLayout(self._container)

        header = QHBoxLayout()
        title = QLabel("Your Classes")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        self._add_class_btn = QPushButton("+ Add Class")
        self._add_class_btn.setStyleSheet(ADD_CLASS_BUTTON_STYLE)
        self._add_class_btn.setCursor(Qt.PointingHandCursor)
        self._add_class_btn.clicked.connect(self._open_add_class_dialog)
        header.addWidget(self._add_class_btn)
        outer.addLayout(header)

        self._empty_label = QLabel(
            "No classes yet — click “+ Add Class” above to save your first skill code."
        )
        self._empty_label.setStyleSheet("color: #9aa2b1; margin-top: 12px;")
        outer.addWidget(self._empty_label)

        self._favorites_label = QLabel("★ Favorites")
        self._favorites_label.setStyleSheet(SECTION_LABEL_STYLE)
        self._favorites_grid_widget = QWidget()
        self._favorites_grid = QGridLayout(self._favorites_grid_widget)
        self._favorites_grid.setSpacing(12)
        self._favorites_grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._others_label = QLabel("All Classes")
        self._others_label.setStyleSheet(SECTION_LABEL_STYLE)
        self._others_grid_widget = QWidget()
        self._others_grid = QGridLayout(self._others_grid_widget)
        self._others_grid.setSpacing(12)
        self._others_grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        outer.addWidget(self._favorites_label)
        outer.addWidget(self._favorites_grid_widget)
        outer.addWidget(self._others_label)
        outer.addWidget(self._others_grid_widget)
        outer.addStretch()

        self.setWidget(self._container)
        self.refresh()

    def refresh(self):
        self._clear_grid(self._favorites_grid)
        self._clear_grid(self._others_grid)

        classes = db.list_classes_with_codes(self.conn)
        favorites = [c for c in classes if c["is_favorite"]]
        others = [c for c in classes if not c["is_favorite"]]

        self._empty_label.setVisible(not classes)

        self._favorites_label.setVisible(bool(favorites))
        self._favorites_grid_widget.setVisible(bool(favorites))
        self._populate_grid(self._favorites_grid, self._favorites_grid_widget, favorites)

        self._others_label.setVisible(bool(others))
        self._others_grid_widget.setVisible(bool(others))
        self._others_label.setText("Other Classes" if favorites else "All Classes")
        self._populate_grid(self._others_grid, self._others_grid_widget, others)

        self._add_class_btn.setEnabled(bool(db.list_available_class_names(self.conn)))

    def _clear_grid(self, grid: QGridLayout):
        while grid.count():
            item = grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _populate_grid(self, grid: QGridLayout, grid_widget, classes):
        row = col = 0
        for class_row in classes:
            tile = ClassTile(class_row, grid_widget)
            tile.clicked_id.connect(self.class_opened.emit)
            tile.rename_requested.connect(self._rename_class)
            tile.change_icon_requested.connect(self._change_icon)
            tile.delete_requested.connect(self._delete_class)
            tile.favorite_toggled.connect(self._toggle_favorite)
            grid.addWidget(tile, row, col)
            col += 1
            if col >= COLUMNS:
                col = 0
                row += 1

    def _toggle_favorite(self, class_id: int):
        class_row = db.get_class(self.conn, class_id)
        if not class_row:
            return
        db.set_class_favorite(self.conn, class_id, not bool(class_row["is_favorite"]))
        self.refresh()

    def _open_add_class_dialog(self):
        available = db.list_available_class_names(self.conn)
        if not available:
            QMessageBox.information(
                self,
                "All classes added",
                "Every known class already has a page. Support for new classes "
                "is added in future app updates.",
            )
            return
        dialog = AddClassDialog(self, available)
        if dialog.exec():
            name = dialog.get_result()
            if not name:
                return
            class_id = db.get_or_create_class(self.conn, name)
            self.class_opened.emit(class_id)

    def _rename_class(self, class_id: int):
        class_row = db.get_class(self.conn, class_id)
        if not class_row:
            return
        dialog = ClassEditDialog(self, name=class_row["name"], icon_filename=class_row["icon_filename"])
        if dialog.exec():
            name, icon_filename = dialog.get_result()
            if not name:
                return
            try:
                db.update_class(self.conn, class_id, name=name, icon_filename=icon_filename)
            except Exception:
                QMessageBox.warning(self, "Error", "A class with this name already exists.")
                return
            self.refresh()

    def _change_icon(self, class_id: int):
        self._rename_class(class_id)

    def _delete_class(self, class_id: int):
        class_row = db.get_class(self.conn, class_id)
        if not class_row:
            return
        answer = QMessageBox.question(
            self,
            "Delete class",
            f"Delete '{class_row['name']}'? All of its skill codes will be deleted too.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            db.delete_class(self.conn, class_id)
            self.refresh()
