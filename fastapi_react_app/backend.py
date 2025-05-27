from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Annotation(BaseModel):
    input_id: str
    document_id: int
    input: str
    document: str
    notes: str = ""
    eval_type: str = ""

class UpdateNotes(BaseModel):
    notes: str

class UpdateEval(BaseModel):
    eval_type: str

def get_db():
    conn = sqlite3.connect('./eval.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/inputs")
def get_inputs():
    conn = get_db()
    cursor = conn.execute("SELECT DISTINCT input_id, input FROM annotation ORDER BY input_id")
    results = []
    for row in cursor.fetchall():
        results.append({
            "input_id": row["input_id"],
            "input": row["input"][:125] + "..." if len(row["input"]) > 125 else row["input"]
        })
    conn.close()
    return results

@app.get("/api/evaluate/{input_id}")
def get_evaluation_data(input_id: str):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM annotation WHERE input_id = ? ORDER BY document_id", (input_id,))
    rows = cursor.fetchall()
    if not rows:
        conn.close()
        raise HTTPException(status_code=404, detail="Input not found")
    
    results = []
    for row in rows:
        results.append({
            "input_id": row["input_id"],
            "document_id": row["document_id"],
            "document": row["document"],
            "notes": row["notes"] or "",
            "eval_type": row["eval_type"] or ""
        })
    
    conn.close()
    return {"input": rows[0]["input"], "documents": results}

@app.put("/api/evaluate/{input_id}/{document_id}/notes")
def update_notes(input_id: str, document_id: int, update: UpdateNotes):
    conn = get_db()
    cursor = conn.execute("UPDATE annotation SET notes = ? WHERE input_id = ? AND document_id = ?", 
                         (update.notes, input_id, document_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Annotation not found")
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/api/evaluate/{input_id}/{document_id}/eval")
def update_evaluation(input_id: str, document_id: int, update: UpdateEval):
    conn = get_db()
    cursor = conn.execute("UPDATE annotation SET eval_type = ? WHERE input_id = ? AND document_id = ?", 
                         (update.eval_type, input_id, document_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Annotation not found")
    conn.commit()
    conn.close()
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 