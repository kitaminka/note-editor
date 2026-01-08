import os

class NoteManager:
    def __init__(self, notes_dir):
        self.notes_dir = notes_dir

    def list_notes(self) -> list[str]:
        return [file.removesuffix(".md") for file in os.listdir(self.notes_dir) if file.endswith(".md")]
    
    def read_note(self, name) -> str:
        with open(f"{self.notes_dir}/{name}.md", encoding="utf-8") as f:
            return f.read()
    
    def write_note(self, name, content) -> None:
        with open(f"{self.notes_dir}/{name}.md", "w") as f:
            f.write(content)