---
description: 
globs: fasthtml_app/**/*
alwaysApply: false
---

# Project Structure

The main file for the project is [main_sqlite.py](mdc:fasthtml_app/main_sqlite.py) It uses MonsterUI for styling.  MonsterUI is a python first UI component library that primarily leverages FrankenUI and Tailwind, but also includes headers and functionality form DaisyUI, Katex, HighlightJS, and others.

You can run the server with the command `python app/main_sqlite.py`, which will start the server on http://localhost:5001.

# Tech Stack

- FastHTML is the web application framework.  It is built on top of starlette and uvicorn.
- MonsterUI is a UI component library designed to work well with FastHTML
- Fastlite is a sqlite library that is a small wrapper on top of sqlite-utils

# Key documentation files:

These are relevant documents that should be referenced while building a FastHTML App.

- [fasthtml.mdc](mdc:.cursor/rules/fasthtml.mdc): Minimal HTMX integration exaples to show how HTMX can be used with fasthtml
- [db.md](mdc:ref_docs/db.md): MiniDataAPI Spec for database operations
- [monsterui_api.md](mdc:ref_docs/monsterui_api.md).md : MonsterUI full API list and idiomatic examples for UI components

# FastHTML examples

Reference these examples when constructing new FastHTML applications.

- [annotation.md](mdc:ref_docs/annotation.md): A siple example of a annotation app to evaluate search results.  
- Adv_app: Example FastHTML To-Do-List application that demonstrates core FastHTML features including authentication, HTMX integration, and database operations. It allows users to create, edit, delete, and reorder todos with markdown support, using SQLite for storage.

# FastHTML Rules

- Use `serve()` directly - no need for uvicorn or separate ASGI server
- Not compatible with FastAPI syntax - FastHTML is for HTML-first apps, not API services
- Define routes with decorators and return HTML components or strings
- Use python FastTags (ie `Div`, `P`) instead of raw HTML where possible
- Use HTMX for interactive features, vanilla JS where needed. No React/Vue/Svelte

# UI Design Elements with MonsterUI

- Use defaults as much as possible, for example `Container` in monsterui already has defaults for margins
- Use `*T` for button styling consistency, for example `ButtonT.destructive` for a red delete button or `ButtonT.primary` for a CTA button
- Use `Label*` functions for forms as much as possible (e.g. `LabelInput`, `LabelRange`) which creates and links both the `FormLabel` and user input appropriately to avoid boiler plate

## Basic Complete App Example

```python
from fasthtml.common import *
from monsterui.all import *

app, rt = fast_app(hdrs=Theme.blue.headers()) # Use MonsterUI blue theme

@rt
def index():
    socials = (('github','https://github.com/AnswerDotAI/MonsterUI'),
               ('twitter','https://twitter.com/isaac_flath/'),
               ('linkedin','https://www.linkedin.com/in/isaacflath/'))
    return Titled("Your First App",
        Card(
            P("Your first MonsterUI app", cls=TextPresets.muted_sm),
            # LabelInput, DivLAigned, and UkIconLink are non-semantic MonsterUI FT Components,
            LabelInput('Email', type='email', required=True),
            footer=DivLAligned(*[UkIconLink(icon,href=url) for icon,url in socials])))
```

## Card and Flex Layout Components Example

```python
def TeamCard(name, role, location="Remote"):
    icons = ("mail", "linkedin", "github")
    return Card(
        DivLAligned(
            DiceBearAvatar(name, h=24, w=24),
            Div(H3(name), P(role))),
        footer=DivFullySpaced(
            DivHStacked(UkIcon("map-pin", height=16), P(location)),
            DivHStacked(*(UkIconLink(icon, height=16) for icon in icons))))
```

## Forms and User Inputs Example

```python
def MonsterForm():
    relationship = ["Parent",'Sibling', "Friend"]
    return Div(
        DivCentered(
            H3("Emergency Contact Form"),
            P("Please fill out the form completely", cls=TextPresets.muted_sm)),
        Form(
            Grid(LabelInput("Name",id='name'),LabelInput("Email",     id='email')),
            H3("Relationship to patient"),
            Grid(*[LabelCheckboxX(o) for o in relationship], cols=4, cls='space-y-3'),
            DivCentered(Button("Submit Form", cls=ButtonT.primary))),
        cls='space-y-4')
```

## Markdown Text Styling Example

```python
render_md("""
# My Document

> Important note here

+ List item with **bold**
+ Another with `code`

```python
def hello():
    print("world")
```
""")
```

## Semantic Text Styling Example

```python
def SemanticText():
    return Card(
        H1("MonsterUI's Semantic Text"),
        P(
            Strong("MonsterUI"), " brings the power of semantic HTML to life with ",
            Em("beautiful styling"), " and ", Mark("zero configuration"), "."),
        Blockquote(
            P("Write semantic HTML in pure Python, get modern styling for free."),
            Cite("MonsterUI Team")),
        footer=Small("Released February 2025"),)
```

# Data Storage

- `fastlite` (SQLite) included and preferred.
- `sqlite-utils` is also a good option and sqlite-utils is compatible with fastlite

## Creating Tables

```python
class Book: isbn: str; title: str; pages: int; userid: int
# The transform arg instructs fastlite to change the db schema when fields change.
# Create only creates a table if the table doesn't exist.
books = db.create(Book, pk='isbn', transform=True)
                
class User: id: int; name: str; active: bool = True
# If no pk is provided, id is used as the primary key.
users = db.create(User, transform=True)
```

## Crud operations

```python
# creating records
user = users.insert(name='Alex',active=False)
# List all records
users()
# Limit, offset, and order results:
users(order_by='name', limit=2, offset=1)
# Filter on the results
users(where="name='Alex'")
# Placeholder for avoiding injection attacks
users("name=?", where_args=('Alex',))
# fetch by primary key
users[user.id]
# Record exists check based on primary key
1 in users
# Updates
user.name='Lauren'
user.active=True
users.update(user)
# Deleting records
users.delete(user.id)
```

# Interactivity

JS can be added via a `Script` tag.  Small scripts should be inline, where larger ones should use a seperate `.js` file.

```python
def index():
    data = {'somedata':'fill me in…'}
    # `Titled` returns a title tag and an h1 tag with the 1st param, along with all other params as HTML in a `Main` parent element.
    return Titled("Chart Demo", Div(id="myDiv"), Script(f"var data = {data}; Plotly.newPlot('myDiv', data);"))
```

However, it is preferred to use HTMX.  See a few examples of how HTMX with FastHTMl and MonsterUI works.

## File Upload Example

```python
@rt
def index():
    inp = Card(
        H3("Drag and drop images here"),
        # HTMX for uploading multiple images
        Input(type="file",name="images", multiple=True, required=True, 
              # Call the upload route on change
              hx_post=upload, hx_target="#image-list", hx_swap="afterbegin", hx_trigger="change",
              # encoding for multipart
              hx_encoding="multipart/form-data",accept="image/*"))

    return DivCentered(inp, H3("👇 Uploaded images 👇"), Div(id="image-list"))

async def ImageCard(image):
    contents = await image.read()
    # Create a base64 string
    img_data = f"data:{image.content_type};base64,{b64encode(contents).decode()}"
    # Create a card with the image
    return Card(H4(image.filename), Img(src=img_data, alt=image.filename))

@rt
async def upload(images: list[UploadFile]):
    # Create a grid filled with 1 image card per image
    return Grid(*[await ImageCard(image) for image in images])
```

## Cascading DropDown Example

```python
def mk_opts(nm, cs):
    return (
        ft.Option(f'-- select {nm} --', disabled='', selected='', value=''),
        *map(ft.Option, cs))

@rt
def get_lessons(chapter: str):
    return ft.Select(*mk_opts('lesson', lessons[chapter]), name='lesson')

@rt
def index():
    chapter_dropdown = ft.Select(
        *mk_opts('chapter', chapters),
        name='chapter',
        hx_get=get_lessons, hx_target='#lessons',
        label='Chapter:')

    return Container(
        DivLAligned(FormLabel("Chapter:", for_="chapter"),chapter_dropdown),
        DivLAligned(
            FormLabel("Lesson:", for_="lesson"),
            Div(id='lessons')),  
        cls='space-y-4')
```



Session data in Websockets
Session data is shared between standard HTTP routes and Websockets. This means you can access, for example, logged in user ID inside websocket handler:
```

from fasthtml.common import *

app = FastHTML(exts='ws')
rt = app.route

@rt('/login')
def get(session):
    session["person"] = "Bob"
    return "ok"

@app.ws('/ws')
async def ws(msg:str, send, session):
    await send(Div(f'Hello {session.get("person")}' + msg, id='notifications'))

serve()
 ```


 ```
 Real-Time Chat App
Let’s put our new websocket knowledge to use by building a simple chat app. We will create a chat app where multiple users can send and receive messages in real time.

Let’s start by defining the app and the home page:

from fasthtml.common import *

app = FastHTML(exts='ws')
rt = app.route

msgs = []
@rt('/')
def home(): return Div(
    Div(Ul(*[Li(m) for m in msgs], id='msg-list')),
    Form(Input(id='msg'), id='form', ws_send=True),
    hx_ext='ws', ws_connect='/ws')

Now, let’s handle the websocket connection. We’ll add a new route for this along with an on_conn and on_disconn function to keep track of the users currently connected to the websocket. Finally, we will handle the logic for sending messages to all connected users.

users = {}
def on_conn(ws, send): users[str(id(ws))] = send
def on_disconn(ws): users.pop(str(id(ws)), None)

@app.ws('/ws', conn=on_conn, disconn=on_disconn)
async def ws(msg:str):
    msgs.append(msg)
    # Use associated `send` function to send message to each user
    for u in users.values(): await u(Ul(*[Li(m) for m in msgs], id='msg-list'))

serve()
 ```




