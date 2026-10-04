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

* modify css to anki/chess-opening.css

  `Tools -> Manage Note Types -> Add -> Select "Add: Basic" -> Name as "Chess Opening" -> Select "Chess Opening" -> Cards -> Modify Front, Back and Styling`

  * Front

  ```html
  <div class="card">{{Front}}</div>
  ```

  * Back

  ```html
  {{Back}}

  <!-- Dependencies -->
  <script src="jquery-3.5.1.js"></script>
  <script src="chess-1.4.0.js"></script>
  <script src="chessboard-1.0.0.js"></script>

  <script src="chess-opening.js"></script>
  ```

  * Styling

  ```css
  @import url("chessboard-1.0.0.css");
  @import url("chess-opening.css");
  ```
* Add field `pgn` to `Chess Opening`

* import to anki

* Debug Anki UI

  ```sh
  QTWEBENGINE_REMOTE_DEBUGGING=9222 anki
  ```
  * Then open `chrome://inspect/#devices` in Chrome/Chromium

## chess url handler

```sh
cp -v bin/chess_url_handler.py bin/chess-url-handler.desktop ~/.local/share/applications/
xdg-mime default chess-url-handler.desktop x-scheme-handler/chess
```

