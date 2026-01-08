from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, TextArea, ListView, ListItem, Label
from textual.containers import Horizontal, VerticalScroll

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
        self.viewer = Markdown("", id="markdown_viewer")
        self.list_view = ListView(*note_items, id="notes")

        yield Header()
        yield Horizontal(
            self.list_view,
            self.editor
            # VerticalScroll(self.viewer, id="viewer_container", can_focus=True)
        )
        yield Footer()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.editor.focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        label = item.query_one(Label)
        # self.viewer.update(self.notes.read_note(label.content))
        self.editor.load_text(self.notes.read_note(label.content))