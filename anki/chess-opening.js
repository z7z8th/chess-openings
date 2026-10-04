
(function () {

    // Initialize the logic engine and the visual board
    // import { Chess } from './chess-1.4.0.js'
    const board_id = "chess-board"
    var $board = $(`#${board_id}`)
    var squareClass = 'square-55d63'
    var squareToHighlight = null
    var colorToHighlight = null
    const interval = 800; // Time per move in milliseconds


    // Sample PGN string
    const pgnString = $('pgn').text();

    function getHistoryMoves(pgnString) {
        const game = new Chess();
        // Load PGN into chess.js
        game.reset();
        console.log(`pgn\n${pgnString}`)

        game.loadPgn(pgnString)
        if (!game.pgn()) {
            console.error("Invalid PGN provided");
            return;
        }

        const history = game.history({ verbose: true });

        return history;
    }

    const history = getHistoryMoves(pgnString);
    if (!history.length) {
        return
    }

    let currentStep = 0;

    function onMoveEnd() {
        if (!squareToHighlight || !colorToHighlight)
            return;
        $board.find('.square-' + squareToHighlight)
            .addClass('highlight-' + colorToHighlight)
    }

    const board = Chessboard(board_id, {
        position: 'start',
        onMoveEnd: onMoveEnd
    });
    board.resize()
    $(window).resize(board.resize)

    function moveToNext() {
        if (currentStep >= history.length) {
            //   clearInterval(timer);
            setTimeout(startAnimation, 1500);
            return;
        }
        let move = history[currentStep];

        // props for onMoveEnd
        color = move.color === 'w' ? 'white' : 'black'
        $board.find('.' + squareClass).removeClass(`highlight-${color}`)
        $board.find('.square-' + move.from).addClass(`highlight-${color}`)
        squareToHighlight = move.to
        colorToHighlight = color

        // board.position(fen, useAnimation)
        board.position(move.after, true);
        currentStep++;
        setTimeout(moveToNext, interval);
    }


    let timer = null;

    function startAnimation() {
        currentStep = 0;

        if (timer) clearInterval(timer);

        // board.reset();
        $board.find('.' + squareClass).removeClass(`highlight-white highlight-black`)
        squareToHighlight = null;
        colorToHighlight = null;
        board.start();

        // board.position(history[0].before, false);
        timer = setTimeout(moveToNext, interval);
    }

    startAnimation();

})();
