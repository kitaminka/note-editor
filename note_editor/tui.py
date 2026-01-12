from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, TextArea, ListView, ListItem, Label, Input
from textual.containers import Horizontal, VerticalScroll, HorizontalScroll
from textual.screen import ModalScreen
from textual.message import Message
from textual import on
from textual.binding import Binding
from textual.events import Focus, Blur, Key

from note_manager import NoteManager

class NoteEditor(TextArea):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save note"),
    ]

    class Save(Message):
        pass

    class Saved(Message):
        pass

    def compose(self) -> ComposeResult:
        self.saved_state = True
        return super().compose()

    @on(Focus)
    def show_border(self) -> None:
        if self.saved_state:
            self.styles.border = ("solid", self.app.theme_variables.get("success"))
        else:
            self.styles.border = ("solid", self.app.theme_variables.get("accent"))

    @on(Blur)
    def auto_save(self) -> None:
        self.action_save()
        self.styles.border = ("solid", self.app.theme_variables.get("border-blurred"))

    @on(TextArea.Changed)
    def show_unsaved_border(self) -> None:
        if self.has_focus:
            self.saved_state = False
            self.styles.border = ("solid", self.app.theme_variables.get("accent"))

    @on(Saved)
    def saved_handler(self) -> None:
        self.saved_state = True
        if self.has_focus:
            self.styles.border = ("solid", self.app.theme_variables.get("success"))
        else:
            self.styles.border = ("solid", self.app.theme_variables.get("border-blurred"))

    def action_save(self) -> None:
        self.post_message(self.Save())
    
    def change_note(self, text: str) -> None:
        self.text = text
        self.saved_state = True

class InputScreen(ModalScreen[str]):
    def __init__(self, placeholder: str | None = None, initial_value: str | None = None) -> None:
        self.placeholder = placeholder
        self.initial_value = initial_value
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Input(placeholder=self.placeholder, value=self.initial_value)

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
        Binding("ctrl+n", "create_note", "New note"),
        Binding("ctrl+r", "delete_selected_note", "Delete selected note"),
        Binding("ctrl+q", "save_quit", "Save and quit"),
        Binding("f2", "rename_selected_note", "Rename selected note"),
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
    
    def on_mount(self) -> None:
        self.no_note()

    @on(ListView.Selected)
    def select_note(self, event: ListView.Selected) -> None:
        self.note_editor.focus()

    @on(ListView.Highlighted)
    def change_note(self, event: ListView.Highlighted) -> None:
        item = event.item
        if item:
            label = item.query_one(Label)
            self.selected_note = label
            # self.viewer.update(self.notes.read_note(self.selected_note.content))
            try:
                note_text = self.notes.read_note(self.selected_note.content)
            except FileNotFoundError:
                self.no_note()
                self.notify(f"Note {self.selected_note.content} does not exist.", severity="error")
                return
            self.note_editor.disabled = False
            self.sub_title = self.selected_note.content
            self.note_editor.change_note(note_text)
        else:
            self.no_note()
    
    def no_note(self) -> None:
        self.note_editor.disabled = True
        self.selected_note = None
        self.sub_title = ""
        self.note_editor.change_note("")

    @on(NoteEditor.Save)
    def save_selected_note(self) -> None:
        if not self.selected_note:
            return
        try:
            self.notes.write_note(self.selected_note.content, self.note_editor.text)
        except FileNotFoundError:
            self.notify(f"Note {self.selected_note.content} does not exist.", severity="error")
            return
        if not self.note_editor.saved_state:
            self.notify(f"Note saved: {self.selected_note.content}")
        self.note_editor.post_message(NoteEditor.Saved())
        
    def action_save_quit(self) -> None:
        self.save_selected_note()
        self.exit()

    def action_create_note(self) -> None:
        def create_note(name: str | None) -> None:
            if not name:
                return
            try:
                self.notes.create_note(name)
            except FileExistsError:
                self.notify("A note with this name already exists.", severity="warning")
                return

            with self.app.batch_update():
                self.save_selected_note()
                self.note_list.append(ListItem(Label(name)))
                self.note_list.index = len(self.note_list.children) - 1
                self.note_list.focus()
                self.note_list.action_select_cursor()

        self.push_screen(InputScreen("Note name"), create_note)

    def action_rename_selected_note(self) -> None:
        def rename_note(new_name: str | None):
            if new_name == self.selected_note.content:
                return
            try:
                self.notes.rename_note(self.selected_note.content, new_name)
            except FileNotFoundError:
                self.notify(f"Note {self.selected_note.content} does not exist.", severity="error")
            except FileExistsError:
                self.notify(f"Note {new_name} already exists.", severity="error")
            self.selected_note.content = new_name
            self.notify(f"Note renamed to {new_name}")

        self.push_screen(InputScreen("Note name", self.selected_note.content), rename_note)
    
    def action_delete_selected_note(self) -> None:
        with self.app.batch_update():
            self.note_list.pop(self.note_list.index)
            self.note_list.focus()
            self.notes.delete_note(self.selected_note.content)