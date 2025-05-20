To use HTMX with FastHTML you can pass the attributes to the HTML elements (e.g. `Button("Show", hx_get=my_route, hx_target='#my-target')`).  Key things to keep in mind:

In FastHTML routes stringify to the route path so you can be pythonic instead of passing strings.  For example if we have the following routes:

```python
@rt
def my_route(): return "Hello world"

@rt
def my_second_route(my_arg:str): return my_arg
```

In this example `Button("Show", hx_get=my_route)` would translate to `Button("Show", hx_get='/my_route')`.  

For routes that have query or path parameters we can use the `to` method if it's not passed via a form.  For example, `Button("Show", hx_get=my_second_route.to(my_arg="Goodbye"))` would translate to `Button("Show", hx_get='/my_second_route?my_arg=Goodbye')`.

`@rt` by default exposes routes as both a `GET` and a `POST`, which is almost always what I want.

## File Upload Example

```python
from base64 import b64encode
from fasthtml.common import *
from monsterui.all import *

app, rt = fast_app(hdrs=Theme.blue.headers())

@rt
def index():
    inp = Card(
        H3("Drag and drop images here"),
        # HTMX for uploading multiple images
        Input(type="file",name="images", multiple=True, required=True, 
              # Call the upload route on change
              post=upload, hx_target="#image-list", hx_swap="afterbegin", hx_trigger="change",
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

serve()
```

## Cascading DropDown Example

```python
from fasthtml.common import *
from monsterui.all import *
from fasthtml import ft

app, rt = fast_app(hdrs=Theme.blue.headers())

chapters = ['ch1', 'ch2', 'ch3']
lessons = {
    'ch1': ['lesson1', 'lesson2', 'lesson3'],
    'ch2': ['lesson4', 'lesson5', 'lesson6'],
    'ch3': ['lesson7', 'lesson8', 'lesson9']}

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

serve()
```

## Infinite Scroll Example

```python
from fasthtml.common import *
from monsterui.all import *
import uuid

column_names = ('name', 'email', 'id')

def generate_contact(id: int) -> Dict[str, str]:
    return {'name': 'Agent Smith',
            'email': f'void{str(id)}@matrix.com',
            'id': str(uuid.uuid4())
            }

def generate_table_row(row_num: int) -> Tr:
    contact = generate_contact(row_num)
    return Tr(*[Td(contact[key]) for key in column_names])

def generate_table_part(part_num: int = 1, size: int = 20) -> Tuple[Tr]:
    paginated = [generate_table_row((part_num - 1) * size + i) for i in range(size)]
    paginated[-1].attrs.update({
        'get': f'page?idx={part_num + 1}',
        'hx-trigger': 'revealed',
        'hx-swap': 'afterend'})
    return tuple(paginated)

app, rt = fast_app(hdrs=Theme.blue.headers())

@rt
def index():
    return Titled('Infinite Scroll',
                  Div(Table(
                      Thead(Tr(*[Th(key) for key in column_names])),
                      Tbody(generate_table_part(1)))))

@rt
def page(idx:int|None = 0):
    return generate_table_part(idx)
```

## Simple Todo App Example

```python
from fasthtml.common import *
from datetime import date,datetime
from monsterui.all import *

# fast_app is doing a lot of work here.
# It creates a table in the database if it doesn't exist with columns id and title making id the primary key
# it returns a connector object todos
# it returns a model class Todo
app, rt, todos, Todo= fast_app('intermediate_todo.db',hdrs=Theme.slate.headers(),
                               title=str,done=bool,due=date, id=int,pk='id')

def tid(id): return f'todo-{id}'

# Render all the todos ordered by todo due date
def mk_todo_list():  return Grid(*todos(order_by='due'), cols=1)

@app.delete
async def delete_todo(id:int):
    "Delete if it exists, if not someone else already deleted it so no action needed"
    try: todos.delete(id)
    except NotFoundError: pass
    # Because there is no return, the todo will be swapped with None and removed from UI

# patch is a decorator that patches the __ft__ method of the Todo class
# this is used to customize the html representation of the Todo object
@patch
def __ft__(self:Todo):
    # Set color to red if the due date is passed
    dd = datetime.strptime(self.due, '%Y-%m-%d').date()
    due_date = Strong(dd.strftime('%Y-%m-%d'),style= "" if date.today() <= dd else "background-color: red;") 

    # Action Buttons
    _targets = {'hx_target':f'#{tid(self.id)}', 'hx_swap':'outerHTML'}
    done   = CheckboxX(       hx_get   =toggle_done.to(id=self.id).lstrip('/'), **_targets, checked=self.done), 
    delete = Button('delete', hx_delete=delete_todo.to(id=self.id).lstrip('/'), **_targets)
    edit   = Button('edit',   hx_get   =edit_todo  .to(id=self.id).lstrip('/'), **_targets)
    
    # Strike through todo if it is completed
    style = Del if self.done else noop
    
    return Card(DivLAligned(done, 
                            style(Strong(self.title, target_id='current-todo')), 
                            style(P(due_date,cls=TextPresets.muted_sm)),
                            edit,
                            delete),
                id=tid(self.id))

@rt
async def index():
    "Main page of the app"
    return Titled('Todo List',mk_todo_form(),Div(mk_todo_list(),id='todo-list'))

@rt 
async def upsert_todo(todo:Todo):
    # Create/update a todo if there is content
    if todo.title.strip(): todos.insert(todo,replace=True)
    # Reload main page with updated database content
    return mk_todo_list(),mk_todo_form()(hx_swap_oob='true',hx_target='#todo-input',hx_swap='outerHTML')

@rt 
async def toggle_done(id:int):
    "Reverses done boolean in the database and returns the todo (rendered with __ft__)"
    return todos.update(Todo(id=id, done=not todos[id].done))


def mk_todo_form(todo=Todo(title=None, done=False, due=date.today(), id=None), btn_text="Add"):
    """Create a form for todo creation/editing with optional pre-filled values"""
    inputs = [Input(id='new-title', name='title',value=todo.title, placeholder='New Todo'),
              Input(id='new-done',  name='done', value=todo.done,  hidden=True),
              Input(id='new-due',   name='due',  value=todo.due)]

    # If there is an ID use it for editing existing row in db
    if todo.id: inputs.append(Input(id='new-id', name='id', value=todo.id, hidden=True))
        
    return Form(DivLAligned(
        *inputs,
        Button(btn_text, cls=ButtonT.primary, post=upsert_todo,hx_target='#todo-list', hx_swap='innerHTML')),
        id='todo-input', cls='mb-6')

@rt 
async def edit_todo(id:int): return Card(mk_todo_form(todos.get(id), btn_text="Save"))

serve()
```