var socket = io();
var grid_size = 0;
var total_mines = 0;

socket.on('hello', function (data) {
    console.log(data)
});

socket.on('game_info', function (data) {
    grid_size = data['grid_size'];
    total_mines = data['total_mines'];
    console.log('grid_size message received')
    console.log(grid_size)
    $('body').prepend('<p>Total Mines: ' + total_mines + '</p><p id="found_mines">Mines Found: 0</p>');
    for (let i = 0; i < grid_size; i++) {
        // $('div#container').append('<div class="board_row" id="board_row' + i + '"></div>');
        $('div#container').append('<div class="board_row" id="board_row' + i + '">');
        for (let j = 0; j < grid_size; j++) {
            $('div#container').append('<span class="node" id="node' + i + '_' + j + '"></span>');
        }
        $('div#container').append('</div>');
    }

    $('span.node').css({"font-family": "monospace", "width": "20px", "display": "inline-block"})
})

socket.on('grid_size', function (data) {
    grid_size = data['grid_size'];
    console.log('grid_size message received')
    console.log(grid_size)
    for (let i = 0; i < grid_size; i++) {
        $('div#container').append('<div id="board_row' + i + '"></div>');
    }
});

socket.on('board_update', function (data) {
        console.log('board_update message received')
        const board = data['board'];
        const found_mines = data['found_mines'];
        console.log(board);

        const stringReducer = (accumulator, currentValue) => {
            return accumulator + currentValue;
        }

        for (let i = 0; i < grid_size; i++) {
            // let divText = board[i].reduce(stringReducer);
            // console.log(divText);
            // $( "div#board_row" + i ).text(divText);
            for (let j = 0; j < grid_size; j++) {
                $("span#node" + i + "_" + j).text(board[i][j]);
            }
        }

        $("p#found_mines").text("Mines Found: " + found_mines);
    }
);