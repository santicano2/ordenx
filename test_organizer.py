import tempfile
import unittest
from pathlib import Path

from organizer import Rule, apply_moves, preview_moves


class OrganizerTests(unittest.TestCase):
    def test_preview_classifies_by_extension(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "factura.PDF").write_text("pdf", encoding="utf-8")
            (root / "notas.txt").write_text("txt", encoding="utf-8")

            previews = preview_moves(root, [Rule("pdf", "Documentos/PDF")])

            self.assertEqual([preview.status for preview in previews], ["listo", "sin regla"])
            self.assertEqual(
                previews[0].destination,
                root / "Documentos" / "PDF" / "factura.PDF",
            )

    def test_preview_reports_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "factura.pdf").write_text("new", encoding="utf-8")
            destination = root / "Documentos" / "factura.pdf"
            destination.parent.mkdir()
            destination.write_text("old", encoding="utf-8")

            previews = preview_moves(root, [Rule("pdf", "Documentos")])

            self.assertEqual(previews[0].status, "conflicto")

    def test_apply_moves_creates_destination_and_preserves_unmatched(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "factura.pdf"
            unmatched = root / "notas.txt"
            source.write_text("pdf", encoding="utf-8")
            unmatched.write_text("txt", encoding="utf-8")

            previews = preview_moves(root, [Rule("pdf", "Documentos")])
            moved_count = apply_moves(previews)

            self.assertEqual(moved_count, 1)
            self.assertFalse(source.exists())
            self.assertTrue((root / "Documentos" / "factura.pdf").exists())
            self.assertTrue(unmatched.exists())


if __name__ == "__main__":
    unittest.main()
