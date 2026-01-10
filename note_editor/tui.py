from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, TextArea, ListView, ListItem, Label
from textual.events import Blur
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.events import Blur

from note_manager import NoteManager

class Editor(TextArea):
    BINDINGS = [
        ("ctrl+s", "save()", "Save note"),
    ]

    class Save(Message):
        def __init__(self, content: str) -> None:
            self.content = content
            super().__init__()

    def on_focus(self) -> None:
        self.styles.border = ("solid", self.app.theme_variables.get("success"))

    def on_blur(self) -> None:
        self.action_save()
        self.styles.border = ("solid", self.app.theme_variables.get("border-blurred"))

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if self.has_focus:
            self.styles.border = ("solid", self.app.theme_variables.get("accent"))

    def action_save(self) -> None:
        self.styles.border = ("solid", self.app.theme_variables.get("success"))
        self.post_message(self.Save(self.text))


class NoteEditorApp(App):
    CSS_PATH = "main.tcss"
    TITLE = "Note Editor"

    def __init__(self):
        super().__init__()
        self.notes = NoteManager("../notes")
        self.selected_note = None

    def compose(self) -> ComposeResult:
        note_items = [ListItem(Label(name)) for name in self.notes.list_notes()]
        self.editor = Editor.code_editor("", language="markdown")
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
        self.selected_note = label.content
        # self.viewer.update(self.notes.read_note(self.selected_note))
        self.editor.load_text(self.notes.read_note(self.selected_note))
    
    def on_editor_save(self, event: Editor.Save):
        self.notes.write_note(self.selected_note, event.content)
        self.notify("Note saved")
    