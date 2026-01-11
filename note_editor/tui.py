from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, TextArea, ListView, ListItem, Label, Input
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.message import Message
from textual import on
from textual.events import Focus, Blur, Key

from note_manager import NoteManager

class NoteEditor(TextArea):
    BINDINGS = [
        ("ctrl+s", "save", "Save note"),
    ]

    class Save(Message):
        pass

    def compose(self) -> ComposeResult:
        self.saved = True
        return super().compose()

    @on(Focus)
    def show_border(self) -> None:
        self.saved = True
        self.styles.border = ("solid", self.app.theme_variables.get("success"))

    @on(Blur)
    def auto_save(self) -> None:
        self.action_save()
        self.styles.border = ("solid", self.app.theme_variables.get("border-blurred"))

    @on(TextArea.Changed)
    def show_unsaved_border(self) -> None:
        if self.has_focus:
            self.saved = False
            self.styles.border = ("solid", self.app.theme_variables.get("accent"))

    def action_save(self) -> None:
        if not self.saved:
            self.saved = True
            self.post_message(self.Save())
            self.styles.border = ("solid", self.app.theme_variables.get("success"))
    
    def change_note(self, text: str) -> None:
        self.text = text
        self.saved = True

class NewNoteScreen(ModalScreen[str]):  
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Note name", id="note-name")

    @on(Input.Submitted)
    def create_note(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip() or None)

    @on(Key)
    def close_screen(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(None)

class NoteEditorApp(App):
    CSS_PATH = "main.tcss"
    TITLE = "Note Editor"
    BINDINGS = [
        ("ctrl+n", "create_note", "New note"),
        # ("ctrl+q", "create_note", "New note"),
    ]

    def __init__(self) -> None:
        self.notes = NoteManager("../notes")
        self.selected_note = None
        super().__init__()

    def compose(self) -> ComposeResult:
        note_items = [ListItem(Label(name)) for name in self.notes.list_notes()]
        self.note_list = ListView(*note_items, id="note_list")
        self.note_editor = NoteEditor.code_editor("", language="markdown")
        self.viewer = Markdown("", id="markdown_viewer")

        yield Header(icon="●")
        yield Horizontal(
            self.note_list,
            self.note_editor
            # VerticalScroll(self.viewer, id="viewer_container", can_focus=True)
        )
        yield Footer()

    @on(ListView.Selected)
    def select_note(self, event: ListView.Selected) -> None:
        self.note_editor.focus()

    @on(ListView.Highlighted)
    def change_note(self, event: ListView.Highlighted) -> None:
        item = event.item
        if item:
            label = item.query_one(Label)
            self.selected_note = label.content
            self.sub_title = self.selected_note
            # self.viewer.update(self.notes.read_note(self.selected_note))
            self.note_editor.change_note(self.notes.read_note(self.selected_note))
        else:
            self.selected_note = None
            self.sub_title = ""
    
    @on(NoteEditor.Save)
    def save_note(self) -> None:
        self.notes.write_note(self.selected_note, self.note_editor.text)
        self.notify(f"Note saved: {self.selected_note}")
        
    def action_create_note(self) -> None:
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

            self.note_editor.blur()
            self.note_list.focus()
            self.note_list.index = insert_index
            self.note_list.action_select_cursor()

        self.push_screen(NewNoteScreen(), create_note)