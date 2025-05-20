from fasthtml.common import *
from monsterui.all import *
import pandas as pd
from db import db, Annotation

app, rt = fast_app(hdrs=Theme.blue.headers())

@rt
def index():
    header = ['Input', 'Action']
    body = []
    unique_inputs = list(db.annotations.rows_where(select='distinct input_id, input'))

    for unique_input in unique_inputs:
        body.append({
            'Input': f"{unique_input['input'][:125]}...",
            'Action': A("Evaluate", 
                        cls=('uk-btn', ButtonT.primary), 
                        href=evaluate.to(input_id=unique_input['input_id']))
        })
    
    return Container(
        H1("Evaluation Index"),
        TableFromDicts(header, body)
    )

@rt
def evaluate(input_id:str):
    _row = list(db.annotations.rows_where('input_id=?', [input_id]))

    
    header = ['Output', 'Notes', 'Evaluation']
    body = []
    for doc in _row:
        body.append({
            'Output': render_md(doc['document']),
            'Notes': Input(value=doc['notes'], cls='w-full min-w-96 border border-gray-300 rounded p-2',
                           name='notes',
                           hx_post=update_notes.to(
                               input_id=input_id, 
                               document_id=doc['document_id']),
                           hx_trigger='change'),
            'Evaluation': eval_buttons(input_id, doc['document_id'])
        })
    
    notes = _row[0].get('notes', '') if 'notes' in _row[0] else ''
    return Container(
        H1("Evaluating Input"),
        Card(render_md(_row[0]['input'].replace('\\n', '\n'))),
        TableFromDicts(header, body),
        A("Back to Index", href="/", cls=('uk-btn', ButtonT.secondary))
    )

@rt
def evaluate_doc(input_id:str, document_id:int, eval_type:str):
    db.annotations.update(Annotation(input_id=input_id, document_id=document_id, eval_type=eval_type))
    return eval_buttons(input_id, document_id)

@rt
def update_notes(input_id: str, document_id: int, notes: str):
    db.annotations.update(Annotation(input_id=input_id, document_id=document_id, notes=notes))
    return Textarea(notes, name='notes', hx_post=update_notes.to(input_id=input_id), hx_trigger='change', cls='w-full min-h-24')

def eval_buttons(input_id:str, document_id:int=None):
    target_id = f"#eval-{input_id}-{document_id}" if document_id is not None else f"#eval-{input_id}"
    _annotation = db.annotations[input_id, document_id]
    
    return DivLAligned(
        Button("Good", 
            hx_post=evaluate_doc.to(input_id=input_id, document_id=document_id, eval_type='good'),
            hx_target=target_id,
            cls=ButtonT.primary if _annotation.eval_type == 'good' else ButtonT.secondary,
            submit=False
        ),
        Button("Bad",
            hx_post=evaluate_doc.to(input_id=input_id, document_id=document_id, eval_type='bad'),
            hx_target=target_id,
            cls=ButtonT.primary if _annotation.eval_type == 'bad' else ButtonT.secondary,
            submit=False
        ),
        id=target_id[1:] 
    )

serve()