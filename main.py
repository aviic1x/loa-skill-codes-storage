import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.db import get_connection, init_db
from app.paths import resource_path
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(resource_path("icons/app.ico"))))

    conn = get_connection()
    init_db(conn)

    window = MainWindow(conn)
    window.show()

    exit_code = app.exec()
    conn.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
