"""Logica inicial de OrdenX para organizar archivos por extension."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
	extension: str
	destination: str

	def normalized_extension(self) -> str:
		extension = self.extension.strip().lower()
		return extension if extension.startswith(".") else f".{extension}"


@dataclass(frozen=True)
class MovePreview:
	source: Path
	destination: Path | None
	status: str


def preview_moves(source_dir: Path, rules: list[Rule]) -> list[MovePreview]:
	rules_by_extension = {
		rule.normalized_extension(): rule for rule in rules
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


def main() -> None:
	"""Punto de entrada de OrdenX."""


if __name__ == "__main__":
	main()