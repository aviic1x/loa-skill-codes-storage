from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import db
from app.paths import resolve_class_icon


class SearchResultRow(QFrame):
    go_to_class_requested = Signal(int)

    def __init__(self, row, parent=None):
        super().__init__(parent)
        self.code = row["code"]
        self.class_id = row["class_id"]

        self.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(self)

        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setPixmap(QIcon(str(resolve_class_icon(row["icon_filename"]))).pixmap(QSize(32, 32)))
        layout.addWidget(icon_label)

        text_col = QVBoxLayout()
        title = QLabel(f"{row['name']}  ·  {row['class_name']}")
        title.setStyleSheet("font-weight: bold;")
        text_col.addWidget(title)
        if row["description"]:
            desc = QLabel(row["description"])
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #9aa2b1;")
            text_col.addWidget(desc)
        layout.addLayout(text_col, stretch=1)

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self._copy_code)
        layout.addWidget(self.copy_btn)

        goto_btn = QPushButton("Go to class")
        goto_btn.clicked.connect(lambda: self.go_to_class_requested.emit(self.class_id))
        layout.addWidget(goto_btn)

    def _copy_code(self):
        QApplication.clipboard().setText(self.code)
        self.copy_btn.setText("Copied!")
        QTimer.singleShot(1000, lambda: self.copy_btn.setText("Copy"))


class SearchResultsView(QScrollArea):
    go_to_class_requested = Signal(int)

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWidgetResizable(True)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setAlignment(Qt.AlignTop)
        self.setWidget(self._container)

    def show_results(self, query: str):
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        results = db.search_skill_codes(self.conn, query)
        if not results:
            empty_label = QLabel("No results.")
            empty_label.setStyleSheet("color: #9aa2b1;")
            self._layout.addWidget(empty_label)
            return

        for row in results:
            result_row = SearchResultRow(row, self._container)
            result_row.go_to_class_requested.connect(self.go_to_class_requested.emit)
            self._layout.addWidget(result_row)
