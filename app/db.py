from fasthtml.common import *
import pandas as pd

###
### Create Annotation Table
###

class Annotation:
    input_id: str
    document_id: int
    input: str
    document: str
    notes: str
    eval_type: str

db = Database('eval.db')
db.annotations = db.create(Annotation, pk=('input_id', 'document_id'), transform=True)

###
### Populate Annotations Table
###

def populate_annotations():
    """Populate annotations table from CSV data."""
    db['annotation'].delete_where()
    db.annotations = db.create(Annotation, pk=('input_id', 'document_id'), transform=True)
    df = pd.read_csv("ds.csv", index_col='example_id')
    for example_id in df.index.unique():
        row = df.loc[example_id]
        for doc in eval(row['output']):
            db.annotations.insert(
                Annotation(
                input_id=example_id,
                document_id=doc['anki_id'],
                input=row['input'],
                document=doc['document'],
                eval_type='',
                notes=''))

if __name__ == "__main__":
    populate_annotations()
