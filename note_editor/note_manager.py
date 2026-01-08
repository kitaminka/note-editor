import os

class NoteManager:
    def __init__(self, path):
        self.path = path

    def list_notes(self) -> list[str]:
        return [file.removesuffix(".md") for file in os.listdir(self.path) if file.endswith(".md")]