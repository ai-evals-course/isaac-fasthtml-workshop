import argparse
import ast
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Optional

import flet as ft
import pandas as pd


@dataclass
class Annotation:
    input_id: str
    document_id: int
    input: Optional[str] = None
    document: Optional[str] = None
    notes: Optional[str] = None
    eval_type: Optional[str] = None


class Database:
    def __init__(self, db_path: str = "eval.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                input_id TEXT,
                document_id INTEGER,
                input TEXT,
                document TEXT,
                notes TEXT,
                eval_type TEXT,
                PRIMARY KEY (input_id, document_id)
            )
        """)
        conn.close()

    @contextmanager
    def cursor(self):
        """Context manager for database operations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def transaction(func):
        """Decorator that injects a database cursor into the wrapped method."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.cursor() as cursor:
                return func(self, cursor, *args, **kwargs)
        return wrapper

    @transaction
    def has_data(self, cursor):
        cursor.execute("SELECT COUNT(*) FROM annotations")
        count = cursor.fetchone()[0]
        return count > 0
    
    @transaction
    def get_unique_inputs(self, cursor):
        cursor.execute("SELECT DISTINCT input_id, input FROM annotations order by input_id asc")
        results = cursor.fetchall()
        return [{"input_id": r[0], "input": r[1]} for r in results]
    
    @transaction
    def get_documents_by_input(self, cursor, input_id: str):
        cursor.execute("SELECT * FROM annotations WHERE input_id = ? order by document_id asc", (input_id,))
        results = cursor.fetchall()
        return [{"input_id": r[0], "document_id": r[1], "input": r[2], 
                "document": r[3], "notes": r[4], "eval_type": r[5]} for r in results]
    
    @transaction
    def update_annotation(self, cursor, annotation: Annotation):
        cursor.execute(
            "SELECT 1 FROM annotations WHERE input_id = ? AND document_id = ?",
            (annotation.input_id, annotation.document_id))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("""
                UPDATE annotations 
                SET notes = COALESCE(?, notes), eval_type = COALESCE(?, eval_type)
                WHERE input_id = ? AND document_id = ?
            """, (annotation.notes, annotation.eval_type, annotation.input_id, annotation.document_id))
        else:
            cursor.execute("""
                INSERT INTO annotations (input_id, document_id, input, document, notes, eval_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (annotation.input_id, annotation.document_id, annotation.input, 
                    annotation.document, annotation.notes, annotation.eval_type))

    @transaction
    def reset_db(self, cursor):
        """delete all annotations"""
        cursor.execute("DELETE FROM annotations")


    def load_traces(self, csv_path: str = "ds.csv"):
        """Populate annotations table with traces from CSV data."""
        self.reset_db()
        
        try:
            # Load CSV data
            df = pd.read_csv(csv_path, index_col='example_id')
            total_docs = 0
            
            for example_id in df.index.unique():
                row = df.loc[example_id]
                try:
                    # Parse the output column which contains a list of dictionaries
                    documents = ast.literal_eval(row['output'])
                    
                    for doc in documents:
                        annotation = Annotation(
                            input_id=example_id,
                            document_id=doc['anki_id'],
                            input=row['input'],
                            document=doc['document'],
                            eval_type='',
                            notes=''
                        )
                        self.update_annotation(annotation)
                        total_docs += 1
                except (ValueError, SyntaxError, KeyError) as e:
                    print(f"Error processing row {example_id}: {e}")
                    continue
            
            print(f"Successfully populated {len(df)} input examples with {total_docs} documents")
            return True
            
        except FileNotFoundError:
            print(f"Error: {csv_path} file not found")
            return False
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return False


class EvaluationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.current_input_id = None
        self.setup_page()
        self.show_index()
        self.eval_buttons = {}
    
    def setup_page(self):
        self.page.title = "Evaluation App"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        # prevent stacking animation on route changes
        n=ft.PageTransitionTheme.NONE
        self.page.theme = ft.Theme(page_transitions=ft.PageTransitionsTheme(
            android=n, ios=n, macos=n, linux=n, windows=n
        ))
    
    def show_index(self):
        self.page.clean()
        title = ft.Text("Evaluation Index", size=32, weight=ft.FontWeight.BOLD)
        unique_inputs = self.db.get_unique_inputs()
        rows = [title]
        for inp in unique_inputs:
            truncated_input = inp["input"][:125] + "..." if len(inp["input"]) > 125 else inp["input"]
            
            evaluate_btn = ft.ElevatedButton("Evaluate", 
                color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600,
                on_click=lambda e, input_id=inp["input_id"]: self.show_evaluate(input_id),
            )
            rows.append(ft.ListTile(title=ft.Text(truncated_input),trailing=evaluate_btn))
            rows.append(ft.Divider(height=1, color=ft.Colors.GREY_300))
        
        self.page.add(ft.Column(rows))
        self.page.update()
    
    def show_evaluate(self, input_id: str):
        self.current_input_id = input_id
        self.page.clean()
        documents = self.db.get_documents_by_input(input_id)
        if not documents:
            self.page.add(ft.Text("No documents found"))
            return

        header = ft.Row([
            ft.ElevatedButton( "← Back to Index",
                on_click=lambda e: self.show_index(), color=ft.Colors.WHITE, bgcolor=ft.Colors.GREY_600),
            ft.Text("Evaluating Input", size=28, weight=ft.FontWeight.BOLD)
        ])
        
        input_card = ft.Card(
            content=ft.Container(
                content=ft.Text(documents[0]["input"].replace("\\n", "\n"),size=14),
                padding=20
            ),
            margin=ft.margin.only(bottom=20)
        )

        rows = [header, input_card]

        for doc in documents:
            # Notes input with responsive width
            notes_input = ft.TextField(
                value=doc["notes"] or "", multiline=True, min_lines=2, max_lines=4, expand=True,
                on_change=lambda e, d_id=doc["document_id"]: self.update_notes(d_id, e.control.value)
            )
            
            # Evaluation buttons
            eval_buttons = self.create_eval_buttons(doc["document_id"], doc["eval_type"])

            rows.append(ft.ResponsiveRow([
                ft.Column(col={"sm": 5}, controls=[
                    ft.Text(doc["document"][:200] + "..." if len(doc["document"]) > 200 else doc["document"])
                ]),
                ft.Column(col={"sm": 4}, controls=[notes_input]),
                ft.Column(col={"sm": 3}, controls=[eval_buttons]),
            ]))
        
        self.page.add(ft.Column(rows, expand=True))
        self.page.update()
    
    def create_eval_buttons(self, document_id: int, current_eval: str):
        good_btn = ft.ElevatedButton("Good",
            on_click=lambda e: self.evaluate_doc(document_id, "good"), color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_600 if current_eval == "good" else ft.Colors.GREY_400
        )
        
        bad_btn = ft.ElevatedButton("Bad",
            on_click=lambda e: self.evaluate_doc(document_id, "bad"), color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_600 if current_eval == "bad" else ft.Colors.GREY_400
        )
        button_row = ft.Row([good_btn, bad_btn], spacing=10)
        # store ref to eval_buttons so that they are easy to select for updating
        self.eval_buttons[document_id] = {'good': good_btn, 'bad': bad_btn}
        
        return button_row
    
    def evaluate_doc(self, document_id: int, eval_type: str):
        annotation = Annotation(input_id=self.current_input_id, document_id=document_id, eval_type=eval_type)
        self.db.update_annotation(annotation)
        
        # Update only the buttons for this document_id
        if hasattr(self, 'eval_buttons') and document_id in self.eval_buttons:
            buttons = self.eval_buttons[document_id]
            
            # Reset both buttons to default state
            buttons['good'].bgcolor = ft.Colors.GREY_400
            buttons['bad'].bgcolor = ft.Colors.GREY_400
            
            # Highlight the selected button
            if eval_type == "good":
                buttons['good'].bgcolor = ft.Colors.GREEN_600
            elif eval_type == "bad":
                buttons['bad'].bgcolor = ft.Colors.RED_600
            
            # Update the page to reflect changes
            self.page.update()
    
    def update_notes(self, document_id: int, notes: str):
        annotation = Annotation(input_id=self.current_input_id, document_id=document_id, notes=notes)
        self.db.update_annotation(annotation)


def main(page: ft.Page):
    app = EvaluationApp(page)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluation App')
    parser.add_argument('--csv', default='../fasthtml_app/ds.csv', 
                       help='Path to CSV file for populating annotations (default: ../fasthtml_app/ds.csv)')
    args = parser.parse_args()

    db = Database()
    if not db.has_data():
        # Expand ~ to home directory if used
        csv_path = os.path.expanduser(args.csv)
        db.load_traces(csv_path)
    
    ft.app(target=main)