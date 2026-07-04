# Anki


##  To anki

* anki with board animation

```sh
make anki
```

* anki without board, txt only

```sh
make anki-txt
```

* modify css to anki-chess-opening.css

  `Tools -> Manage Note Types -> Add -> Select "Add: Basic" -> Name as "Chess Opening" -> Select "Chess Opening" -> Cards -> Modify Front, Back and Styling`

* import to anki


## chess url handler

```sh

cp -v bin/chess_url_handler.py bin/chess-url-handler.desktop ~/.local/share/applications/

xdg-mime default chess-url-handler.desktop x-scheme-handler/chess

```

