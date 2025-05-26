from fasthtml.common import *
from monsterui.all import *
import pandas as pd
from starlette.responses import JSONResponse
app, rt = fast_app(hdrs=Theme.blue.headers())

df = pd.read_csv("ds.csv", index_col='example_id')
unique_inputs = df.index.unique()
evaluations = {}

def eval_buttons(example_id:str, doc_idx:int=None):
    target_id = f"#eval-{example_id}-{doc_idx}" if doc_idx is not None else f"#eval-{example_id}"
    eval_key = (doc_idx, example_id) if doc_idx is not None else example_id
    
    return DivLAligned(
        Button("Good", 
            hx_post=evaluate_doc.to(example_id=example_id, eval_type='good'),
            hx_target=target_id,
            cls=ButtonT.primary if evaluations.get(eval_key) == 'good' else ButtonT.secondary,
            submit=False
        ),
        Button("Bad",
            hx_post=evaluate_doc.to(example_id=example_id, eval_type='bad'),
            hx_target=target_id,
            cls=ButtonT.primary if evaluations.get(eval_key) == 'bad' else ButtonT.secondary,
            submit=False
        ),
        id=target_id[1:] 
    )

@rt('/')
def get():
    header = ['Input', 'Action']
    body = []
    for i, example_id in enumerate(unique_inputs):
        body.append({
            'Input': f"{df.loc[example_id]['input'][:125]}...",
            'Action': A("Evaluate", 
                        cls=AT.primary, 
                        href=evaluate.to(example_id=example_id))
        })
    
    return Container(
        A("Download Annotations", href=get_annotations.to(), cls=AT.primary),        
        H1("Evaluation Index"),
        TableFromDicts(header, body)
    )

@rt
def evaluate(example_id:str):
    _row = df.loc[example_id]
    
    header = ['Output', 'Evaluation']
    body = []
    for i, doc in enumerate(eval(_row['output'])):
        body.append({
            'Output': render_md(doc['document']),
            'Evaluation': eval_buttons(example_id, i)
        })
    
    return Container(
        H1("Evaluating Input"),
        render_md(_row['input']),
        TableFromDicts(header, body),
        A("Back to Index", href="/", cls=AT.primary)
    )

@rt
def evaluate_doc(example_id:str, eval_type:str):
    evaluations[example_id] = eval_type
    return eval_buttons(example_id)

@rt
def get_annotations():
    return JSONResponse(evaluations, headers={'Content-Disposition': 'attachment; filename=evaluations.json'})

serve()