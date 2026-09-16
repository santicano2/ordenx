"""Ventana principal de OrdenX."""

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OrdenX")
        self.resize(640, 180)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Selecciona la carpeta Descargas")
        self.folder_input.setReadOnly(True)

        select_button = QPushButton("Elegir carpeta")
        select_button.clicked.connect(self.select_folder)

        self.status_label = QLabel("Aún no seleccionaste una carpeta")

        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_input)
        folder_row.addWidget(select_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Carpeta de origen"))
        layout.addLayout(folder_row)
        layout.addWidget(self.status_label)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Elegir carpeta")
        if folder:
            self.folder_input.setText(folder)
            self.status_label.setText("Carpeta seleccionada correctamente")