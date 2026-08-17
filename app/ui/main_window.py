from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.class_detail_view import ClassDetailView
from app.ui.home_view import HomeView
from app.ui.search_results_view import SearchResultsView

SEARCH_DEBOUNCE_MS = 200


class MainWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("LOA Skill Code Storage")
        self.resize(900, 640)

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)

        top_bar = QHBoxLayout()
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.go_home)
        top_bar.addWidget(self.home_btn)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Cerca per nome o descrizione...")
        self.search_edit.textChanged.connect(self._on_search_text_changed)
        top_bar.addWidget(self.search_edit, stretch=1)
        outer.addLayout(top_bar)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(SEARCH_DEBOUNCE_MS)
        self._search_timer.timeout.connect(self._run_search)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack)

        self.home_view = HomeView(self.conn)
        self.home_view.class_opened.connect(self.go_to_class)

        self.class_detail_view = ClassDetailView(self.conn)
        self.class_detail_view.back_requested.connect(self.go_home)

        self.search_results_view = SearchResultsView(self.conn)
        self.search_results_view.go_to_class_requested.connect(self.go_to_class)

        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.class_detail_view)
        self.stack.addWidget(self.search_results_view)

        self.go_home()

    def go_home(self):
        self.home_view.refresh()
        self.stack.setCurrentWidget(self.home_view)

    def go_to_class(self, class_id: int):
        self.class_detail_view.load(class_id)
        self.stack.setCurrentWidget(self.class_detail_view)

    def go_to_search(self, query: str):
        self.search_results_view.show_results(query)
        self.stack.setCurrentWidget(self.search_results_view)

    def _on_search_text_changed(self, text: str):
        if not text.strip():
            self._search_timer.stop()
            self.go_home()
            return
        self._search_timer.start()

    def _run_search(self):
        query = self.search_edit.text().strip()
        if query:
            self.go_to_search(query)
