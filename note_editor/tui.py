from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, TextArea, ListView, ListItem, Label, Input
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.message import Message
from textual import on

from note_manager import NoteManager

class Editor(TextArea):
    BINDINGS = [
        ("ctrl+s", "save", "Save note"),
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

    def on_text_area_changed(self) -> None:
        if self.has_focus:
            self.styles.border = ("solid", self.app.theme_variables.get("accent"))

    def action_save(self) -> None:
        self.styles.border = ("solid", self.app.theme_variables.get("success"))
        self.post_message(self.Save(self.text))

class NewNoteScreen(ModalScreen[str]):  
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Note name", id="note-name")

    @on(Input.Submitted)
    def create_note(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip() or None)

class NoteEditorApp(App):
    CSS_PATH = "main.tcss"
    TITLE = "Note Editor"
    BINDINGS = [
        ("ctrl+n", "create_note", "New note"),
    ]

    def __init__(self):
        super().__init__()
        self.notes = NoteManager("../notes")
        self.selected_note = None

    def compose(self) -> ComposeResult:
        note_items = [ListItem(Label(name)) for name in self.notes.list_notes()]
        self.note_list = ListView(*note_items, id="note_list")
        self.editor = Editor.code_editor("", language="markdown")
        self.viewer = Markdown("", id="markdown_viewer")
        # self.action_update_note_list()

        yield Header()
        yield Horizontal(
            self.note_list,
            self.editor
            # VerticalScroll(self.viewer, id="viewer_container", can_focus=True)
        )
        yield Footer()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.editor.focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if item:
            label = item.query_one(Label)
            self.selected_note = label.content
            # self.viewer.update(self.notes.read_note(self.selected_note))
            self.editor.load_text(self.notes.read_note(self.selected_note))
    
    def on_editor_save(self, event: Editor.Save):
        self.notes.write_note(self.selected_note, event.content)
        self.notify("Note saved")

    def action_create_note(self):
        def create_note(name: str | None) -> None:
            if not name:
                return
            
            created = self.notes.create_note(name)
            if not created:
                self.notify("A note with this name already exists.", severity="warning")
                return
            new_item = ListItem(Label(name))
            current_names = [item.query_one(Label).content for item in self.note_list.children]

            insert_index = len(current_names)
            for i in range(len(current_names)):
                existing_name = current_names[i]
                if name.lower() < existing_name.lower():
                    insert_index = i
                    break
            
            self.note_list.insert(insert_index, [new_item])

            self.note_list.focus()
            self.note_list.index = insert_index
            self.note_list.action_select_cursor()

        self.push_screen(NewNoteScreen(), create_note)