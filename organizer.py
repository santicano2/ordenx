"""Logica de organizacion de archivos por extension."""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    extension: str
    destination: str

    def normalized_extension(self) -> str:
        extension = self.extension.split(",", maxsplit=1)[0].strip().lower()
        return extension if extension.startswith(".") else f".{extension}"

    def normalized_extensions(self) -> list[str]:
        extensions = []
        for extension in self.extension.split(","):
            normalized = extension.strip().lower()
            if normalized:
                extensions.append(
                    normalized if normalized.startswith(".") else f".{normalized}"
                )
        return extensions


@dataclass(frozen=True)
class MovePreview:
    source: Path
    destination: Path | None
    status: str


def recommended_rules() -> list[Rule]:
    return [
        Rule("pdf", "Documentos/PDF"),
        Rule("doc, docx, odt, rtf", "Documentos/Word"),
        Rule("xls, xlsx, ods, csv", "Documentos/Excel"),
        Rule("txt, md, log", "Documentos/Texto"),
        Rule("jpg, jpeg, png, gif, webp, svg", "Imagenes"),
        Rule("mp4, mov, avi, mkv", "Videos"),
        Rule("mp3, wav, flac, m4a", "Musica"),
        Rule("zip, rar, 7z, tar, gz", "Comprimidos"),
    ]


def legacy_recommended_rules() -> list[Rule]:
    return [
        Rule("pdf, doc, docx, txt, rtf", "Documentos"),
        Rule("jpg, jpeg, png, gif, webp, svg", "Imagenes"),
        Rule("mp4, mov, avi, mkv", "Videos"),
        Rule("mp3, wav, flac, m4a", "Musica"),
        Rule("zip, rar, 7z, tar, gz", "Comprimidos"),
        Rule("xlsx, csv, ods", "Planillas"),
    ]


def with_recommended_rules(rules: list[Rule]) -> list[Rule]:
    if not rules:
        return recommended_rules()

    combined = list(rules)
    covered_extensions = {
        extension
        for rule in combined
        for extension in rule.normalized_extensions()
    }

    for recommended in recommended_rules():
        missing_extensions = [
            extension
            for extension in recommended.normalized_extensions()
            if extension not in covered_extensions
        ]
        if missing_extensions:
            combined.append(Rule(", ".join(missing_extensions), recommended.destination))
            covered_extensions.update(missing_extensions)

    return combined


def load_rules(path: Path) -> list[Rule]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    return [Rule(str(item["extension"]), str(item["destination"])) for item in data]


def save_rules(path: Path, rules: list[Rule]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {"extension": rule.extension, "destination": rule.destination}
        for rule in rules
    ]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_source_folder(path: Path) -> Path | None:
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    source_folder = data.get("source_folder")
    return Path(source_folder) if source_folder else None


def save_source_folder(path: Path, source_folder: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"source_folder": str(source_folder)}, indent=2),
        encoding="utf-8",
    )


def preview_moves(source_dir: Path, rules: list[Rule]) -> list[MovePreview]:
    rules_by_extension = {
        extension: rule
        for rule in rules
        for extension in rule.normalized_extensions()
    }
    previews = []

    for source in sorted(source_dir.iterdir(), key=lambda item: item.name.lower()):
        if not source.is_file():
            continue

        rule = rules_by_extension.get(source.suffix.lower())
        if rule is None:
            previews.append(MovePreview(source, None, "sin regla"))
            continue

        destination = source_dir / rule.destination / source.name
        status = "conflicto" if destination.exists() else "listo"
        previews.append(MovePreview(source, destination, status))

    return previews


def apply_moves(previews: list[MovePreview]) -> int:
    moved_count = 0

    for preview in previews:
        if preview.status != "listo" or preview.destination is None:
            continue
        if preview.destination.exists():
            continue

        preview.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(preview.source), str(preview.destination))
        moved_count += 1

    return moved_count