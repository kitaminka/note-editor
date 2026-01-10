from pathlib import Path

import os

class NoteManager:
    def __init__(self, notes_dir):
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def create_note(self, name: str) -> bool:
        note_path = self.notes_dir / f"{name}.md"
        if note_path.exists():
            return False
        
        note_path.touch()
        return True

    def list_notes(self) -> list[str]:
        return [file.stem for file in self.notes_dir.glob("*.md")]
    
    def read_note(self, name: str) -> str:
        note_path = self.notes_dir / f"{name}.md"
        if note_path.exists():
            return note_path.read_text(encoding="utf-8")
    
    def write_note(self, name: str, content: str) -> None:
        note_path = self.notes_dir / f"{name}.md"
        note_path.write_text(content, encoding="utf-8")