#!/usr/bin/env bash
pyinstaller --onefile --console note_editor/main.py --add-data "note_editor/main.tcss:." --collect-all tree_sitter_markdown