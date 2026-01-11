#!/usr/bin/env bash
pyinstaller --onefile --console note_editor/main.py --add-data "note_editor/main.tcss:." --collect-all textual_markdown --name "note-editor"