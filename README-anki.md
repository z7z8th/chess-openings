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

  <div style="display: none;">
    <img src="_bB.png">
    <img src="_bK.png">
    <img src="_bN.png">
    <img src="_bP.png">
    <img src="_bQ.png">
    <img src="_bR.png">
    <img src="_wB.png">
    <img src="_wK.png">
    <img src="_wN.png">
    <img src="_wP.png">
    <img src="_wQ.png">
    <img src="_wR.png">
  </div>

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

