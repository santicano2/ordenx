"""Ventana principal de OrdenX."""

import json
import re
from pathlib import Path

from organizer import (
    MovePreview,
    Rule,
    apply_moves,
    load_rules,
    load_source_folder,
    legacy_recommended_rules,
    preview_moves,
    recommended_rules,
    save_rules,
    save_source_folder,
    with_recommended_rules,
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
    QComboBox,
    QVBoxLayout,
    QWidget,
)


CATEGORY_EXTENSIONS = {
    "PDFs": "pdf",
    "Words": "doc, docx, odt, rtf",
    "Excels": "xls, xlsx, ods, csv",
    "Presentaciones": "ppt, pptx, odp, key",
    "Textos": "txt, md, log",
    "Imagenes": "jpg, jpeg, png, gif, webp, svg",
    "Videos": "mp4, mov, avi, mkv",
    "Musica": "mp3, wav, flac, m4a",
    "Comprimidos": "zip, rar, 7z, tar, gz",
    "Ejecutables": "exe, msi, bat, cmd, sh, appimage, dmg, pkg",
}


def validate_rule(extension: str, destination: str) -> str | None:
    extensions = [item.strip() for item in extension.split(",") if item.strip()]
    if not extensions:
        return "Agrega al menos una extension"
    if any(not re.fullmatch(r"\.?[A-Za-z0-9][A-Za-z0-9_-]*", item) for item in extensions):
        return "La extension solo puede contener letras, numeros, guion o guion bajo"

    destination_path = Path(destination)
    if not destination.strip():
        return "Completa la carpeta destino"
    if destination_path.is_absolute() or ".." in destination_path.parts:
        return "El destino debe ser una subcarpeta dentro de Descargas"
    if any(not part.strip() for part in destination_path.parts):
        return "El destino contiene una carpeta vacia"
    return None


class MainWindow(QMainWindow):
    def __init__(self, rules_path: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("OrdenX")
        self.resize(760, 520)
        self.rules_path = rules_path or Path.home() / ".ordenx" / "rules.json"
        self.settings_path = self.rules_path.with_name("settings.json")
        try:
            loaded_rules = load_rules(self.rules_path)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            loaded_rules = []
        if loaded_rules == legacy_recommended_rules():
            loaded_rules = recommended_rules()
        self.rules: list[Rule] = with_recommended_rules(loaded_rules)
        if self.rules != loaded_rules:
            save_rules(self.rules_path, self.rules)
        self.previews: list[MovePreview] = []

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Selecciona la carpeta Descargas")
        self.folder_input.setReadOnly(True)
        saved_folder = load_source_folder(self.settings_path)
        if saved_folder is not None:
            self.folder_input.setText(str(saved_folder))

        select_button = QPushButton("Elegir carpeta")
        select_button.clicked.connect(self.select_folder)
        analyze_button = QPushButton("Analizar carpeta")
        analyze_button.clicked.connect(self.analyze_folder)

        self.status_label = QLabel("Aún no seleccionaste una carpeta")

        self.extension_input = QComboBox()
        self.extension_input.setEditable(True)
        self.extension_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.extension_input.addItems(list(CATEGORY_EXTENSIONS))
        self.extension_input.setCurrentText("")
        self.extension_input.lineEdit().setPlaceholderText("Categoria o extensiones personalizadas")
        self.destination_input = QComboBox()
        self.destination_input.setEditable(True)
        self.destination_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.destination_input.addItems(
            [
                "Documentos",
                "Documentos/PDF",
                "Documentos/Planillas",
                "Imagenes",
                "Videos",
                "Musica",
                "Comprimidos",
                "Programas",
            ]
        )
        self.destination_input.setCurrentText("")
        self.destination_input.lineEdit().setPlaceholderText("Ej: Documentos/PDF")
        add_rule_button = QPushButton("Agregar regla")
        add_rule_button.clicked.connect(self.add_rule)
        edit_rule_button = QPushButton("Guardar edicion")
        edit_rule_button.clicked.connect(self.edit_selected_rule)
        remove_rule_button = QPushButton("Eliminar seleccionada")
        remove_rule_button.clicked.connect(self.remove_selected_rule)
        self.rules_list = QListWidget()
        self.rules_list.currentRowChanged.connect(self.load_selected_rule)
        self.refresh_rules_list()

        rule_row = QHBoxLayout()
        rule_row.addWidget(self.extension_input)
        rule_row.addWidget(self.destination_input)
        rule_row.addWidget(add_rule_button)
        rule_row.addWidget(edit_rule_button)
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
            save_source_folder(self.settings_path, Path(folder))
            self.status_label.setText("Carpeta seleccionada correctamente")

    def add_rule(self) -> None:
        extension = self.extension_input.currentText().strip()
        destination = self.destination_input.currentText().strip()
        error = validate_rule(extension, destination)
        if error:
            self.status_label.setText(error)
            return

        extension = CATEGORY_EXTENSIONS.get(extension, extension)
        rule = Rule(extension, destination)
        if any(
            set(existing.normalized_extensions()) & set(rule.normalized_extensions())
            for existing in self.rules
        ):
            self.status_label.setText("Ya existe una regla para esa extension")
            return

        self.rules.append(rule)
        save_rules(self.rules_path, self.rules)
        self.refresh_rules_list()
        self.extension_input.setCurrentText("")
        self.destination_input.setCurrentText("")
        self.status_label.setText("Regla agregada")

    def refresh_rules_list(self) -> None:
        self.rules_list.clear()
        for rule in self.rules:
            category = next(
                (
                    name
                    for name, extensions in CATEGORY_EXTENSIONS.items()
                    if extensions == rule.extension
                ),
                rule.extension,
            )
            self.rules_list.addItem(
                f"{category}  ->  {rule.destination}"
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

    def load_selected_rule(self, row: int) -> None:
        if row < 0 or row >= len(self.rules):
            return
        rule = self.rules[row]
        category = next(
            (
                name
                for name, extensions in CATEGORY_EXTENSIONS.items()
                if extensions == rule.extension
            ),
            rule.extension,
        )
        self.extension_input.setCurrentText(category)
        self.destination_input.setCurrentText(rule.destination)

    def edit_selected_rule(self) -> None:
        selected_row = self.rules_list.currentRow()
        if selected_row < 0:
            self.status_label.setText("Selecciona una regla para editarla")
            return

        extension = self.extension_input.currentText().strip()
        destination = self.destination_input.currentText().strip()
        error = validate_rule(extension, destination)
        if error:
            self.status_label.setText(error)
            return

        extension = CATEGORY_EXTENSIONS.get(extension, extension)
        edited_rule = Rule(extension, destination)
        for index, existing in enumerate(self.rules):
            if index != selected_row and (
                set(existing.normalized_extensions())
                & set(edited_rule.normalized_extensions())
            ):
                self.status_label.setText("Ya existe una regla para esa extension")
                return

        self.rules[selected_row] = edited_rule
        save_rules(self.rules_path, self.rules)
        self.refresh_rules_list()
        self.rules_list.setCurrentRow(selected_row)
        self.status_label.setText("Regla editada")

    def analyze_folder(self) -> None:
        folder = self.folder_input.text().strip()
        if not folder:
            self.status_label.setText("Selecciona una carpeta antes de analizar")
            return
        source_dir = Path(folder)
        if not source_dir.is_dir():
            self.status_label.setText("La carpeta seleccionada ya no existe")
            return
        if not self.rules:
            self.status_label.setText("Agrega al menos una regla antes de analizar")
            return

        self.previews = preview_moves(source_dir, self.rules)
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