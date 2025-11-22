from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, TextArea, ListView, ListItem, Label, Placeholder
from textual.containers import Horizontal, Vertical

class NoteEditorApp(App):
    CSS_PATH = "main.tcss"
    TITLE = "Note Editor"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            ListView(
                ListItem(Label("Note 1")),
                ListItem(Label("Note 2")),
                ListItem(Label("Note 3")),
            ),
            TextArea.code_editor("**dsfadsfd**", language="markdown")
            # Markdown(EXAMPLE_MARKDOWN),
            # Placeholder(label="Editor"),
        )
        yield Footer()

if __name__ == "__main__":
    app = NoteEditorApp()
    app.run()