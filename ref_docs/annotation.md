To build an annotation app MonsterUI makes that easy.  This is particularly useful for evaluating AI models.

Please reference this simple example for how to build one in an idiomatic way for a text annotation retrieval use-case.  In here there are examples of

- Using `FastLite` for database table creation, storage, and querying
- Using `MonsterUI` in a complete example
- Using idiomatic `FastHTML` routing with `HTMX`


```python
"""Search Evaluation App for querying, annotating, and ranking search results."""

from fasthtml.common import *
from datetime import datetime
from pathlib import Path
from monsterui.all import *

# Import search algorithms - each uses a different retrieval strategy
from search_blog import (vector_search, bm25_search, hybrid_search, search_blog_posts)

# Table schema definitions via fastlite
class Query:
    id: int          # Primary key
    query_text: str  # The actual query text
    created_at: str  # Timestamp when the query was created

class Evaluation:
    id: int              # Primary key
    query_id: int        # Foreign key to Query
    result_id: str       # ID of the evaluated search result
    relevance_score: int # Relevance rating (1-5)
    notes: str           # Evaluator's notes
    created_at: str      # Timestamp when the evaluation was created


# FastLite uses SQLite under the hood but with a simpler API
db_path = Path("search_evaluations.db")
db = database(db_path)
# Create or connect to tables based on class definitions - no SQL or ORM setup needed.  
# This creates a connection, only creating a table if it doesn't exist.
db.queries     = db.create(Query,      pk='id')
db.evaluations = db.create(Evaluation, pk='id')
    
def save_query(query_text):
    """Save a query to the database and return its ID."""
    now = datetime.now().isoformat()
    query = db.queries.insert(Query(query_text=query_text, created_at=now))
    return query.id

def save_evaluation(query_id, result_id, relevance_score, notes):
    """Save an evaluation to the database."""
    now = datetime.now().isoformat()
    # FastLite handles the insertion and returns the object with its ID
    evaluation = db.evaluations.insert(Evaluation(
        query_id=query_id, result_id=result_id, 
        relevance_score=relevance_score, notes=notes, created_at=now))
    return evaluation.id

def get_evaluations_for_query(query_id):
    """Get evaluations for a specific query."""
    # FastLite's query syntax is simpler than SQL but powerful enough for most needs
    evaluations = db.evaluations('query_id=?',[query_id])
    # Sort by relevance to show best results first - key function handles None values
    return sorted(evaluations, key=lambda x: x.relevance_score if x.relevance_score is not None else 0, reverse=True)

def get_evaluation_stats():
    """Get statistics for queries with evaluations."""
    # For complex queries, FastLite allows raw SQL with a simple API
    return db.q(f"""
        SELECT q.id, q.query_text, 
               COUNT(e.id) as eval_count, 
               AVG(e.relevance_score) as avg_score
        FROM query q
        LEFT JOIN evaluation e ON q.id = e.query_id
        GROUP BY q.id
        HAVING eval_count > 0
        ORDER BY q.created_at DESC
    """)

def get_all_evaluations():
    """Get all evaluations with query text."""
    return db.q(f"""
        SELECT q.query_text, e.result_id, e.relevance_score, e.notes, e.created_at
        FROM evaluation e
        JOIN query q ON e.query_id = q.id
        ORDER BY q.id, e.relevance_score DESC
    """)

# FastHTML creates an app that can be served - rt decorator registers routes
app, rt = fast_app(hdrs=Theme.blue.headers(), pico=False, live=True, HighlightJS=True)

def EvalNavBar():
    """Create navigation bar with links to main app sections."""
    return NavBar(
        # FastHTML components map 1:1 with HTML tags
        # A("Search", href="/") -> <a href="/">Search</a>
        A("Search", href="/",              cls=AT.primary),
        A("Evals",  href=view_evaluations, cls=AT.primary),
        # MonsterUI components can be nested to create complex UI elements
        brand=Div(
            H3("Search Evaluation Tool"), 
            Subtitle("Query, annotate, and rank search results")))

def layout(content):
    """Wrap content in consistent page layout with navigation."""
    return Div(EvalNavBar(), Container(content))

def search_form(query=""):
    """Create search form with query input and search options."""
    # Local function to reduce repetition when creating options
    def _Option(label, selected=False):
        return Option(label, value=label.lower(), selected=selected)
    
    return Card(
        Form(
            # MonsterUI's Label* components combine labels with inputs for cleaner UI
            LabelInput("Search Query", id="query", placeholder="Enter your search query...", value=query),
            
            LabelSelect(
                # An Option component is used to create a dropdown option
                _Option("Rerank", selected=True),
                # We can use common python patterns to create a list of options
                *map(_Option, ("Vector", "BM25", "Hybrid Search")),
                label="Search Method", id="search_method"),
            
            LabelInput("Number of Results", type="number", id="top_k",min="1", max="20", value="5"),
            
            # ButtonT.primary is an enum for styling - w-full makes button full width
            # This is combining MonsterUI styles with tailwind classes giving lots of control over the style
            Button("Search", cls=(ButtonT.primary,'w-full')),
            
            # HTMX attributes enable dynamic updates without full page reloads
            # Make a POST request to the search route and update the #search-results div with the response
            hx_post=search, hx_target="#search-results"))

@rt
def search(query: str = "", search_method: str = "vector", top_k: int = 5):
    """Execute search and return formatted results."""
    if not query: return Card(P("Please enter a search query", cls=TextT.error))
    
    # Avoid duplicate queries in the database by checking if it exists first
    existing_queries = db.queries('query_text=?',[query])
    query_id = existing_queries[0].id if existing_queries else save_query(query)
    
    match search_method:
        case "vector":  results = vector_search(query).sort_values('vector_score', ascending=False).head(top_k)
        case "bm25":  results = bm25_search(query, vector_search(query)).sort_values('bm25_score', ascending=False).head(top_k)
        case "hybrid":  results = hybrid_search(query, top_k=top_k)
        case 'rerank':  results = search_blog_posts(query, top_k=top_k)
        case _: raise ValueError(f"Invalid search method: {search_method}")

    return Div(
        H2(f"Search Results for: '{query}'"),
        P(f"Method: {search_method.capitalize()}"),
        *[search_result_component(results.iloc[i], query_id) for i in range(len(results))],
        Card(P("No results found", cls=TextT.muted + TextT.italic)) if len(results) == 0 else "")

def search_result_component(result, query_id):
    """Create a card for a search result with evaluation controls."""
    result_id = str(result.name)
    post_title, chunk_title, content = result['post_title'], result['chunk_title'], result['content']
    token_count = result.get('token_count', 0) 
    
    # Visual cues help evaluators quickly assess content length
    if token_count < 1000: token_color = TextT.success     # Green = short, easy to read
    elif token_count < 3000: token_color = TextT.warning   # Yellow = medium length
    else: token_color = TextT.error                        # Red = long, may be too verbose
    
    # Different search methods use different scoring mechanisms
    score = result['rerank_score'] if 'rerank_score' in result else (
        result['combined_score'] if 'combined_score' in result else (
            result['vector_score'] if 'vector_score' in result else (
                result['bm25_score'] if 'bm25_score' in result else 0)))
    
    return Card(Article(
        ArticleTitle(post_title), H4(chunk_title),
        # DivFullySpaced creates a flexbox with items at opposite ends (Layout helpers)
        DivFullySpaced(
            P(f"Score: {score:.4f}", cls=TextT.muted + TextT.sm),
            P(f"Tokens: {token_count}", cls=token_color + TextT.sm)),
        Divider(),
        # render_md converts markdown to HTML and styles it nicely for you
        P(render_md(content)),
        Divider(),
        Form(
            H4("Relevance Rating:", cls=TextT.medium + TextT.sm),
            Div(
                # LabelRadio combines a radio button with its label for better UX
                *[LabelRadio(rating_labels(i), name=f"rating", value=str(i)) for i in range(1, 6)],
                cls="space-y-2"),
            LabelTextArea("Notes:", id=f"notes", placeholder="Add notes about this result...", rows="2", cls='w-full'),
            Button("Save Evaluation", type="button", cls=ButtonT.primary,
                   # HTMX will send the form data to the save_eval endpoint
                   hx_post=save_eval.to(query_id=query_id, result_id=result_id),
                   hx_swap="none"))))

def rating_labels(rating):
    """Convert numeric ratings to descriptive text for better UX."""
    labels = {1: "Not relevant",
              2: "Slightly relevant",
              3: "Moderately relevant",
              4: "Relevant",
              5: "Highly relevant"}
    return f"{rating} - {labels[rating]}"

@rt
def save_eval(query_id:str, result_id:str, rating:int=0, notes:str=""):
    """Save evaluation data from the form."""
    # FastHTML automatically converts form data to function parameters
    save_evaluation(query_id, result_id, rating, notes)

@rt
def index():
    """Render the main search page."""
    return layout(Div(search_form(), Div(id="search-results")))

@rt
def view_evaluations(query_id: int = None):
    """Show either all queries with evaluations or details for a specific query."""
    if not query_id:
        # Overview mode - show all queries with evaluation stats
        queries = get_evaluation_stats()        
        return layout(Card(H2("Queries with Evals"),  AllEvalsTable(queries)))
    else:
        # Detail mode - show evaluations for a specific query
        query = db.queries[query_id]
        evaluations = get_evaluations_for_query(query_id)
        return layout(Div(H4(f"Evals for: '{query.query_text}'", cls='mb-6'), Card(SingleEvalTable(evaluations))))

def AllEvalsTable(queries):
    """Create a table showing all queries with evaluation statistics using TableFromDicts."""
    headers = ["Query", "Evaluations", "Avg. Score", "Actions"]
    
    def create_row(query):
        "Pull data from query and format it for viewing"
        return {
            "Query":       query['query_text'],
            "Evaluations": str(query['eval_count']),
            "Avg. Score":  f"{query['avg_score']:.2f}" if query['avg_score'] else "N/A",
            # Actions uses a link (href) to send to the `view_evaluations` route for the specific query
            "Actions":     A("View Details", href=view_evaluations.to(query_id=query['id']), cls=AT.primary)}
    
    rows = list(map(create_row, queries))
    return TableFromDicts(headers, rows)

def SingleEvalTable(evaluations):
    """Create a table showing evaluations for a single query using TableFromDicts."""
    headers = ["Result ID", "Relevance", "Notes", "Date"]
    
    def create_row(eval):
        "Pull data from an eval and format it for viewing"
        return {
            "Result ID": eval.result_id,
            "Relevance": str(eval.relevance_score),
            "Notes":     eval.notes or "No notes",
            "Date":      eval.created_at}
    
    rows = list(map(create_row, evaluations))
    return TableFromDicts(headers, rows)

# Start the server - FastHTML handles the ASGI setup
serve()
```