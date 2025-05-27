from fasthtml.common import *
from monsterui.all import *
from db import db, Annotation

app, rt = fast_app(hdrs=Theme.blue.headers())

@rt
def index():
    body = []
    unique_inputs = list(db.annotations.rows_where(select='distinct input_id, input'))
    for unique_input in unique_inputs:
        body.append({
            'Input': f"{unique_input['input'][:125]}...",
            'Action': A("Evaluate", 
                        cls=AT.primary, 
                        href=evaluate.to(input_id=unique_input['input_id']))})
    
    return Container(
        H1("Evaluation Index"),
        TableFromDicts(['Input', 'Action'], body))

@rt
def evaluate(input_id:str):
    documents = list(db.annotations.rows_where('input_id=?', [input_id]))
    body = []
    for doc in documents:
        body.append({
            'Output': render_md(doc['document']),
            'Notes': Input(value=doc['notes'], 
                           cls='min-w-96',
                           name='notes',
                           hx_post=update_notes.to(input_id=input_id, document_id=doc['document_id']),
                           hx_trigger='change'),
            'Evaluation': eval_buttons(input_id, doc['document_id'])})
    
    return Container(
        H1("Evaluating Input"),
        Card(render_md(documents[0]['input'].replace('\\n', '\n'))),
        TableFromDicts(['Output', 'Notes', 'Evaluation'], body))    

@rt
def evaluate_doc(input_id:str, document_id:int, eval_type:str):
    db.annotations.update(Annotation(input_id=input_id, document_id=document_id, eval_type=eval_type))
    return eval_buttons(input_id, document_id)

@rt
def update_notes(input_id: str, document_id: int, notes: str):
    record = Annotation(input_id=input_id, document_id=document_id, notes=notes)
    db.annotations.update(record)

def eval_buttons(input_id:str, document_id:int=None):
    target_id = f"#eval-{input_id}-{document_id}" if document_id is not None else f"#eval-{input_id}"
    _annotation = db.annotations[input_id, document_id]
    
    def create_eval_button(label: str):
        """Create an evaluation button with consistent properties."""
        return Button(label,
            hx_post=evaluate_doc.to(input_id=input_id, document_id=document_id, eval_type=label.lower()),
            hx_target=target_id,
            cls=ButtonT.primary if _annotation.eval_type == label.lower() else ButtonT.secondary,
            submit=False)
    
    return DivLAligned(
        create_eval_button("Good"), create_eval_button("Bad"),
        id=target_id[1:])

serve()