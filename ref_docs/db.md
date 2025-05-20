# fastlite

`fastlite` provides some little quality-of-life improvements for interactive use of the wonderful [sqlite-utils](https://sqlite-utils.datasette.io/) library. It’s likely to be particularly of interest to folks using Jupyter.

## Overview

``` python
from fastlite import *
from fastcore.utils import *
from fastcore.net import urlsave
```

We demonstrate `fastlite`‘s features here using the ’chinook’ sample database.

``` python
url = 'https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite'
path = Path('chinook.sqlite')
if not path.exists(): urlsave(url, path)

db = database("chinook.sqlite")
```

Databases have a `t` property that lists all tables:

``` python
dt = db.t
dt
```

    Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine, MediaType, Playlist, PlaylistTrack, Track, sqlite_stat1, sqlite_stat4

You can use this to grab a single table…:

``` python
artist = dt.artists
artist
```

    <Table artists (does not exist yet)>

``` python
artist = dt.Artist
artist
```

    <Table Artist (ArtistId, Name)>

…or multiple tables at once:

``` python
dt['Artist','Album','Track','Genre','MediaType']
```

    [<Table Artist (ArtistId, Name)>,
     <Table Album (AlbumId, Title, ArtistId)>,
     <Table Track (TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice)>,
     <Table Genre (GenreId, Name)>,
     <Table MediaType (MediaTypeId, Name)>]

You can check if a table is in the database already:

``` python
'Artist' in dt
```

    True

Column work in a similar way to tables, using the `c` property:

``` python
ac = artist.c
ac
```

    ArtistId, Name

Columns, tables, and view stringify in a format suitable for including in SQL statements. That means you can use auto-complete in f-strings.

``` python
qry = f"select * from {artist} where {ac.Name} like 'AC/%'"
print(qry)
```

    select * from "Artist" where "Artist"."Name" like 'AC/%'

You can view the results of a select query using `q`:

``` python
db.q(qry)
```

    [{'ArtistId': 1, 'Name': 'AC/DC'}]

Views can be accessed through the `v` property:

``` python
album = dt.Album

acca_sql = f"""select {album}.*
from {album} join {artist} using (ArtistId)
where {ac.Name} like 'AC/%'"""

db.create_view("AccaDaccaAlbums", acca_sql, replace=True)
acca_dacca = db.q(f"select * from {db.v.AccaDaccaAlbums}")
acca_dacca
```

    [{'AlbumId': 1,
      'Title': 'For Those About To Rock We Salute You',
      'ArtistId': 1},
     {'AlbumId': 4, 'Title': 'Let There Be Rock', 'ArtistId': 1}]

Indexing into a table does a query on primary key:

``` python
dt.Track[1]
```

    Track(TrackId=1, Name='For Those About To Rock (We Salute You)', AlbumId=1, MediaTypeId=1, GenreId=1, Composer='Angus Young, Malcolm Young, Brian Johnson', Milliseconds=343719, Bytes=11170334, UnitPrice=0.99)

There’s a shortcut to select from a table – just call it as a function.  There’s lots of params you can check out, such as `limit`:

``` python
album(limit=2)
```

    [Album(AlbumId=1, Title='For Those About To Rock We Salute You', ArtistId=1),
     Album(AlbumId=2, Title='Balls to the Wall', ArtistId=2)]

Pass a truthy value as `with_pk` and you’ll get tuples of primary keys and records:

``` python
album(with_pk=1, limit=2)
```

    [(1,
      Album(AlbumId=1, Title='For Those About To Rock We Salute You', ArtistId=1)),
     (2, Album(AlbumId=2, Title='Balls to the Wall', ArtistId=2))]

Indexing also uses the dataclass by default:

``` python
album[5]
```

    Album(AlbumId=5, Title='Big Ones', ArtistId=3)



    Not found

The same filtering is done when using the table as a callable:

``` python
album()
```

    [Album(AlbumId=1, Title='For Those About To Rock We Salute You', ArtistId=1),
     Album(AlbumId=4, Title='Let There Be Rock', ArtistId=1)]

## Core design

The following methods accept `**kwargs`, passing them along to the first
`dict` param:

- `create`
- `transform`
- `transform_sql`
- `update`
- `insert`
- `upsert`
- `lookup`

We can access a table that doesn’t actually exist yet:

``` python
cats = dt.cats
cats
```

    <Table cats (does not exist yet)>

We can use keyword arguments to now create that table:

``` python
cats.create(id=int, name=str, weight=float, uid=int, pk='id')
hl_md(cats.schema, 'sql')
```

``` sql
CREATE TABLE [cats] (
   [id] INTEGER PRIMARY KEY,
   [name] TEXT,
   [weight] FLOAT,
   [uid] INTEGER
)
```


Using `**` in `update` here doesn’t actually achieve anything, since we
can just pass a `dict` directly – it’s just to show that it works:

``` python
cat['name'] = "moo"
cat['uid'] = 1
cats.update(**cat)
cats()
```

    [{'id': 1, 'name': 'moo', 'weight': 6.0, 'uid': 2}]

``` python
cats.drop()
cats
```

    <Table cats (does not exist yet)>

You can create a table from a class.

``` python
class Cat: id:int; name:str; weight:float; uid:int
```

``` python
cats = db.create(Cat)
```

``` python
hl_md(cats.schema, 'sql')
```

``` sql
CREATE TABLE [cat] (
   [id] INTEGER PRIMARY KEY,
   [name] TEXT,
   [weight] FLOAT,
   [uid] INTEGER
)
```

``` python
cat = Cat(name='咪咪', weight=9)
cats.insert(cat)
```

    Cat(id=1, name='咪咪', weight=9.0, uid=None)

``` python
cats.drop()
```

## Manipulating data

We try to make the following methods as flexible as possible. Wherever possible, they support Python dictionaries and classes.

### .insert()

Creates a record. In the name of flexibility, we test that dictionaries, dataclasses, and classes all work. Returns an instance of the updated record.

Insert using a dictionary.

``` python
cats.insert({'name': 'Rex', 'weight': 12.2})
```

    Cat(id=1, name='Rex', weight=12.2, uid=UNSET)

Insert using a standard Python class

``` python
cat = cats.insert(Cat(name='Jerry', weight=5.2))
```

Using the standard Python class is preferred

### .update()

Updates a record using a Python dict, dataclasses, and classes all work
and returns an instance of the updated record.

Updating from a Python dict:

``` python
cats.update(dict(id=cat.id, name='Jerry', weight=6.2))
```

    Cat(id=3, name='Jerry', weight=6.2)

Updating using a class:

``` python
cats.update(Cat(id=cat.id, name='Jerry', weight=5.7))
```

    Cat(id=3, name='Jerry', weight=5.7)

Using the standard Python class is preferred

### .delete()

Removing data is done by providing the primary key value of the record.

``` python
# Farewell Jerry!
cats.delete(cat.id)
```

    <Table cat (id, name, weight)>
