# personal-notes-manager-43271-43280

## Note Backend - RESTful CRUD API

### Running Locally

```bash
cd note_backend
pip install -r requirements.txt
python run.py
```
The server will start on port `3001`.

Swagger UI for testing and docs: [http://localhost:3001/docs](http://localhost:3001/docs)

### Example API Requests

#### Create a note
```bash
curl -X POST http://localhost:3001/notes/ -H "Content-Type: application/json" -d '{"title":"My Note","content":"Hello notes"}'
```

#### Get all notes
```bash
curl http://localhost:3001/notes/
```

#### Get a note by id
```bash
curl http://localhost:3001/notes/1
```

#### Update a note
```bash
curl -X PUT http://localhost:3001/notes/1 -H "Content-Type: application/json" -d '{"title":"Updated title"}'
```

#### Delete a note
```bash
curl -X DELETE http://localhost:3001/notes/1
```

### Data Persistance
The backend stores all notes in a file called `notes_data.json` in the `note_backend/app/` directory. Data is preserved while the backend is running, but will reset if the file is deleted.