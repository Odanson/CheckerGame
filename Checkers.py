import tkinter as tk

# Global variables for managing the game state
board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board
player_turn = "R"  # Red starts
selected_piece = None  # No piece selected initially
possible_moves = []  # To track valid moves for the selected piece

def initialize_board():
    """Initialize the game board with pieces for both players."""
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "R"  # Initialize red pieces
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "G"  # Initialize green pieces

def draw_board():
    """Clears and redraws the entire board and pieces based on the current game state."""
    canvas.delete("all")  # Clear the canvas
    for row in range(8):
        for col in range(8):
            x1, y1 = col * 80, row * 80
            x2, y2 = x1 + 80, y1 + 80
            fill = "black" if (row + col) % 2 == 0 else "white"
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="gray")
            piece = board[row][col]
            if piece:
                color = "red" if piece == "R" else "green"
                canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill=color)


def on_canvas_click(event):
    global selected_piece, player_turn, possible_moves
    col, row = event.x // 80, event.y // 80  # Convert click position to board coordinates

    if (row, col) in possible_moves:  # If a valid move is selected
        move_piece(selected_piece, (row, col))  # Move the piece
        draw_board()  # Redraw the board with the new state
        selected_piece = None  # Deselect the piece
        possible_moves = []  # Clear possible moves
        switch_turns()  # Switch turns after a successful move
    elif board[row][col] and board[row][col][0].lower() == player_turn.lower():
        selected_piece = (row, col)  # Select the piece
        possible_moves = find_possible_moves(selected_piece)  # Find possible moves for the selected piece
        highlight_moves(possible_moves)  # Highlight possible moves
    else:
        selected_piece = None  # Deselect if clicked outside
        possible_moves = []
        draw_board()  # Redraw to remove highlights


def switch_turns():
    global player_turn
    player_turn = "G" if player_turn == "R" else "R"  # Toggle player turn


def find_possible_moves(pos):
    global board, player_turn
    row, col = pos
    captures = []  # Store capture moves
    standard_moves = []  # Store standard moves
    directions = [(-1, -1), (-1, 1)]  # Diagonal forward directions for regular pieces

    piece = board[row][col]
    if piece and piece.endswith("K"):  # If the piece is a king, add backward directions
        directions += [(1, -1), (1, 1)]

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        # Position after the capture
        jump_row, jump_col = new_row + dr, new_col + dc

        # Check for captures first
        if is_valid_position(new_row, new_col) and board[new_row][new_col] \
           and board[new_row][new_col][0].lower() != player_turn.lower() \
           and is_valid_position(jump_row, jump_col) and board[jump_row][jump_col] is None:
            captures.append((jump_row, jump_col))
        elif is_valid_position(new_row, new_col) and board[new_row][new_col] is None:
            standard_moves.append((new_row, new_col))

    # Prioritize captures if available, otherwise return standard moves
    return captures if captures else standard_moves


def is_valid_position(row, col):
    """Check if the given position is on the board."""
    return 0 <= row < 8 and 0 <= col < 8


def highlight_moves(moves):
    for move in moves:
        row, col = move
        x1, y1 = col * 80, row * 80
        canvas.create_oval(x1 + 35, y1 + 35, x1 + 45, y1 + 45, fill='yellow', tags='highlight')



def move_piece(from_pos, to_pos):
    global board, player_turn
    row_from, col_from = from_pos
    row_to, col_to = to_pos

    # Move the piece
    board[row_to][col_to] = board[row_from][col_from]
    board[row_from][col_from] = None

    # Handle capture
    if abs(row_to - row_from) == 2 and abs(col_to - col_from) == 2:
        mid_row, mid_col = (row_from + row_to) // 2, (col_from + col_to) // 2
        board[mid_row][mid_col] = None  # Remove the captured piece

    # Promote to king if the piece reaches the opposite side
    if (player_turn == "R" and row_to == 7) or (player_turn == "G" and row_to == 0):
        board[row_to][col_to] += "K"  # Append "K" to indicate a King

    # Clear any move highlights
    canvas.delete('highlight')

    # Additional logic can be added here if needed xxxxxxxxxxx


# Setup the game window and canvas
root = tk.Tk()
root.title("Checkers")
canvas = tk.Canvas(root, width=640, height=640)
canvas.pack()
canvas.bind("<Button-1>", on_canvas_click)

# Initialize the board and draw the initial setup
initialize_board()
draw_board()

root.mainloop()
