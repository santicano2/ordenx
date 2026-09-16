"""Ventana principal de OrdenX."""

from pathlib import Path

from organizer import (
    MovePreview,
    Rule,
    apply_moves,
    load_rules,
    preview_moves,
    save_rules,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self, rules_path: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("OrdenX")
        self.resize(760, 520)
        self.rules_path = rules_path or Path.home() / ".ordenx" / "rules.json"
        self.rules: list[Rule] = load_rules(self.rules_path)
        self.previews: list[MovePreview] = []

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Selecciona la carpeta Descargas")
        self.folder_input.setReadOnly(True)

        select_button = QPushButton("Elegir carpeta")
        select_button.clicked.connect(self.select_folder)
        analyze_button = QPushButton("Analizar carpeta")
        analyze_button.clicked.connect(self.analyze_folder)

        self.status_label = QLabel("Aún no seleccionaste una carpeta")

        self.extension_input = QLineEdit()
        self.extension_input.setPlaceholderText("Ej: pdf")
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Ej: Documentos/PDF")
        add_rule_button = QPushButton("Agregar regla")
        add_rule_button.clicked.connect(self.add_rule)
        remove_rule_button = QPushButton("Eliminar seleccionada")
        remove_rule_button.clicked.connect(self.remove_selected_rule)
        self.rules_list = QListWidget()
        self.refresh_rules_list()

        rule_row = QHBoxLayout()
        rule_row.addWidget(self.extension_input)
        rule_row.addWidget(self.destination_input)
        rule_row.addWidget(add_rule_button)
        rule_row.addWidget(remove_rule_button)

        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_input)
        folder_row.addWidget(select_button)
        folder_row.addWidget(analyze_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Carpeta de origen"))
        layout.addLayout(folder_row)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Reglas por extension"))
        layout.addLayout(rule_row)
        layout.addWidget(self.rules_list)
        layout.addWidget(QLabel("Vista previa"))
        self.preview_list = QListWidget()
        layout.addWidget(self.preview_list)
        organize_button = QPushButton("Organizar archivos")
        organize_button.clicked.connect(self.organize_files)
        layout.addWidget(organize_button)
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
        if any(
            existing.normalized_extension() == rule.normalized_extension()
            for existing in self.rules
        ):
            self.status_label.setText("Ya existe una regla para esa extension")
            return

        self.rules.append(rule)
        save_rules(self.rules_path, self.rules)
        self.refresh_rules_list()
        self.extension_input.clear()
        self.destination_input.clear()
        self.status_label.setText("Regla agregada")

    def refresh_rules_list(self) -> None:
        self.rules_list.clear()
        for rule in self.rules:
            self.rules_list.addItem(
                f"{rule.normalized_extension()}  ->  {rule.destination}"
            )

    def remove_selected_rule(self) -> None:
        selected_row = self.rules_list.currentRow()
        if selected_row < 0:
            self.status_label.setText("Selecciona una regla para eliminarla")
            return

        self.rules.pop(selected_row)
        save_rules(self.rules_path, self.rules)
        self.refresh_rules_list()
        self.status_label.setText("Regla eliminada")

    def analyze_folder(self) -> None:
        folder = self.folder_input.text().strip()
        if not folder:
            self.status_label.setText("Selecciona una carpeta antes de analizar")
            return
        if not self.rules:
            self.status_label.setText("Agrega al menos una regla antes de analizar")
            return

        self.previews = preview_moves(Path(folder), self.rules)
        self.preview_list.clear()
        for preview in self.previews:
            destination = str(preview.destination) if preview.destination else "Se queda en Descargas"
            self.preview_list.addItem(
                f"[{preview.status}] {preview.source.name} -> {destination}"
            )
        self.status_label.setText(f"Analizados {len(self.previews)} archivos")

    def organize_files(self) -> None:
        ready_count = sum(preview.status == "listo" for preview in self.previews)
        if ready_count == 0:
            self.status_label.setText("No hay archivos listos para mover")
            return

        answer = QMessageBox.question(
            self,
            "Confirmar organizacion",
            f"Se moveran {ready_count} archivos. Quieres continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.status_label.setText("Organizacion cancelada")
            return

        moved_count = apply_moves(self.previews)
        self.previews = []
        self.preview_list.clear()
        self.status_label.setText(f"Se movieron {moved_count} archivos")