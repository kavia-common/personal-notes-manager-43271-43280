from flask_smorest import Blueprint, abort
from flask.views import MethodView
from marshmallow import Schema, fields, validate
import os
import json
import threading

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../notes_data.json')
DATA_LOCK = threading.Lock()


def _read_notes():
    with DATA_LOCK:
        if not os.path.exists(DATA_PATH):
            return []
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []


def _write_notes(notes):
    with DATA_LOCK:
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)


def _find_note(note_id):
    notes = _read_notes()
    for note in notes:
        if note["id"] == note_id:
            return note
    return None


def _generate_id(notes):
    # Returns an integer with +1 from highest existing id or 1 if no notes
    if not notes:
        return 1
    return max(note["id"] for note in notes) + 1


# Marshmallow schemas
class NoteSchema(Schema):
    id = fields.Int(required=True, description="Unique note ID")
    title = fields.Str(required=True, description="Note title")
    content = fields.Str(required=True, description="Note body text")


class NoteCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1), description="Note title")
    content = fields.Str(required=True, validate=validate.Length(min=1), description="Note body text")


class NoteUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1), description="Note title")
    content = fields.Str(validate=validate.Length(min=1), description="Note body text")


blp = Blueprint(
    "Notes",
    "notes",
    url_prefix="/notes",
    description="CRUD operations for personal notes"
)


@blp.route("/")
class NotesList(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """Get all notes."""
        notes = _read_notes()
        return NoteSchema(many=True).dump(notes), 200

    # PUBLIC_INTERFACE
    @blp.arguments(NoteCreateSchema)
    @blp.response(201, NoteSchema)
    def post(self, new_note_data):
        """Create a new note."""
        notes = _read_notes()
        new_id = _generate_id(notes)
        note = {
            "id": new_id,
            "title": new_note_data["title"],
            "content": new_note_data["content"],
        }
        notes.append(note)
        _write_notes(notes)
        return note


@blp.route("/<int:note_id>")
class NotesDetail(MethodView):
    # PUBLIC_INTERFACE
    @blp.response(200, NoteSchema)
    def get(self, note_id):
        """Get a single note by ID."""
        note = _find_note(note_id)
        if not note:
            abort(404, message=f"Note {note_id} not found.")
        return note

    # PUBLIC_INTERFACE
    @blp.arguments(NoteUpdateSchema)
    @blp.response(200, NoteSchema)
    def put(self, update_data, note_id):
        """Update an existing note by ID."""
        notes = _read_notes()
        for i, note in enumerate(notes):
            if note["id"] == note_id:
                note.update({k: v for k, v in update_data.items() if v is not None})
                notes[i] = note
                _write_notes(notes)
                return note
        abort(404, message=f"Note {note_id} not found.")

    # PUBLIC_INTERFACE
    @blp.response(204)
    def delete(self, note_id):
        """Delete a note by ID."""
        notes = _read_notes()
        notes_out = [note for note in notes if note["id"] != note_id]
        if len(notes_out) == len(notes):
            abort(404, message=f"Note {note_id} not found.")
        _write_notes(notes_out)
        return "", 204

