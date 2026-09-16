"""Ventana principal de OrdenX."""

from organizer import Rule
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
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
        self.rules: list[Rule] = []

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Selecciona la carpeta Descargas")
        self.folder_input.setReadOnly(True)

        select_button = QPushButton("Elegir carpeta")
        select_button.clicked.connect(self.select_folder)

        self.status_label = QLabel("Aún no seleccionaste una carpeta")

        self.extension_input = QLineEdit()
        self.extension_input.setPlaceholderText("Ej: pdf")
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Ej: Documentos/PDF")
        add_rule_button = QPushButton("Agregar regla")
        add_rule_button.clicked.connect(self.add_rule)
        self.rules_list = QListWidget()

        rule_row = QHBoxLayout()
        rule_row.addWidget(self.extension_input)
        rule_row.addWidget(self.destination_input)
        rule_row.addWidget(add_rule_button)

        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_input)
        folder_row.addWidget(select_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Carpeta de origen"))
        layout.addLayout(folder_row)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Reglas por extension"))
        layout.addLayout(rule_row)
        layout.addWidget(self.rules_list)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Elegir carpeta")
        if folder:
            self.folder_input.setText(folder)
            self.status_label.setText("Carpeta seleccionada correctamente")

    def add_rule(self) -> None:
        extension = self.extension_input.text().strip()
        destination = self.destination_input.text().strip()
        if not extension or not destination:
            self.status_label.setText("Completa la extension y la carpeta destino")
            return

        rule = Rule(extension, destination)
        self.rules.append(rule)
        self.rules_list.addItem(f"{rule.normalized_extension()}  ->  {rule.destination}")
        self.extension_input.clear()
        self.destination_input.clear()
        self.status_label.setText("Regla agregada")