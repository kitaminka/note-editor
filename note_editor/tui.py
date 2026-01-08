from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, TextArea, ListView, ListItem, Label, Placeholder
from textual.containers import Horizontal, Vertical

from note_manager import NoteManager

class NoteEditorApp(App):
    CSS_PATH = "main.tcss"
    TITLE = "Note Editor"

    def __init__(self):
        super().__init__()
        self.notes = NoteManager("../notes")

    def compose(self) -> ComposeResult:
        note_items = [ListItem(Label(name)) for name in self.notes.list_notes()]
        self.editor = TextArea.code_editor("", language="markdown")
        self.list_view = ListView(*note_items, id="notes")

        yield Header()
        yield Horizontal(
            self.list_view,
            self.editor,
        )
        yield Footer()
    
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        label = item.query_one(Label)
        self.editor.text = f"{label.content} loaded!"

if __name__ == "__main__":
    app = NoteEditorApp()
    app.run()