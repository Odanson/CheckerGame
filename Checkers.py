import tkinter as tk
import time

# Global variables for managing the game state
board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board
player_turn = "R"  # Red starts
selected_piece = None  # No piece selected initially
possible_moves = []  # To track valid moves for the selected piece
move_history = []  # To track the history of moves for undo functionality

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
    update_turn_label()

# Global dictionary to hold the canvas item IDs
piece_ids = {}

def draw_board():
    """Clears and redraws the entire board and pieces based on the current game state."""
    global piece_ids
    canvas.delete("all")  # Clear the canvas
    piece_ids.clear()  # Clear the old IDs
    for row in range(8):
        for col in range(8):
            x1, y1 = col * 80, row * 80
            x2, y2 = x1 + 80, y1 + 80
            fill = "black" if (row + col) % 2 == 0 else "white"
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="gray")
            piece = board[row][col]
            if piece:
                color = "red" if piece == "R" else "green"
                # Create the piece and store its ID in the piece_ids dictionary
                piece_id = canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill=color)
                piece_ids[(row, col)] = piece_id


def on_canvas_click(event):
    global selected_piece, player_turn, possible_moves
    col, row = event.x // 80, event.y // 80  # Convert click position to board coordinates

    # Handle case where a selected piece is making a continued capture
    if selected_piece and (row, col) in possible_moves:
        move_piece(selected_piece, (row, col))  # Execute the move
        draw_board()
        # After moving, check if there are further captures available from the new position
        if any(abs(row - r) == 2 for r, _ in find_possible_moves((row, col))):
            # If more captures are available, update the possible moves and keep the piece selected
            possible_moves = find_possible_moves((row, col))
            selected_piece = (row, col)  # Update the selected piece to its new position
            highlight_moves(possible_moves)
        else:
            # If no further captures are available, deselect the piece and clear possible moves
            selected_piece = None
            possible_moves = []
            switch_turns()
        return  # Exit the function to avoid re-selecting or deselecting the piece

    # Normal piece selection logic
    if board[row][col] and board[row][col][0].lower() == player_turn.lower():
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
    update_turn_label()

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

def animate_move(from_pos, to_pos, piece_id):
    """Animate the movement of a piece from from_pos to to_pos."""
    piece_id = piece_ids.get(from_pos)
    from_x, from_y = from_pos[1] * 80, from_pos[0] * 80
    to_x, to_y = to_pos[1] * 80, to_pos[0] * 80

def is_valid_position(row, col):
    """Check if the given position is on the board."""
    return 0 <= row < 8 and 0 <= col < 8

def highlight_moves(moves):
    for move in moves:
        row, col = move
        x1, y1 = col * 80, row * 80
        is_capture = selected_piece and abs(selected_piece[0] - row) == 2
        color = 'orange' if is_capture else 'yellow'  # Use a different color for captures
        canvas.create_oval(x1 + 35, y1 + 35, x1 + 45, y1 + 45, fill=color, tags='highlight')

def check_for_victory():
    """Check the board state for a victory condition and display the result."""
    if not player_has_pieces('R'):
        display_victory('Green wins!')
    elif not player_has_pieces('G'):
        display_victory('Red wins!')
    elif not player_has_moves('R') or not player_has_moves('G'):
        display_victory('Draw!')

def player_has_pieces(player):
    """Check if a player has any pieces left."""
    return any(piece is not None and piece.startswith(player) for row in board for piece in row)

def player_has_moves(player):
    """Check if a player has any legal moves left."""
    return any(find_possible_moves((row, col)) for row in range(8) for col in range(8) if board[row][col] and board[row][col].startswith(player))

def display_victory(message):
    """Display the end game message and disable further moves."""
    victory_label.config(text=message)
    canvas.unbind("<Button-1>")  # Disable further moves

def play_again():
    """Reset the game to its initial state and re-enable interactions."""
    reset_game()
    canvas.bind("<Button-1>", on_canvas_click)
    victory_label.config(text="")

def move_piece(from_pos, to_pos):
    global board, player_turn, piece_ids
    row_from, col_from = from_pos
    row_to, col_to = to_pos

    # Retrieve the canvas ID of the piece to move from the dictionary
    piece_id = piece_ids.get(from_pos)

    save_state()  # Save the current state before making changes

    # Animate the piece movement if we have a valid piece ID
    if piece_id:
        animate_move(from_pos, to_pos, piece_id)

    # Proceed with the existing move and capture logic
    board[row_to][col_to] = board[row_from][col_from]
    board[row_from][col_from] = None
    if abs(row_to - row_from) == 2:  # Capture made
        mid_row, mid_col = (row_from + row_to) // 2, (col_from + col_to) // 2
        # Remove the captured piece from the canvas and the piece_ids dictionary
        captured_piece_id = piece_ids.pop((mid_row, mid_col), None)
        if captured_piece_id:
            canvas.delete(captured_piece_id)
        board[mid_row][mid_col] = None

    # Promote to king if applicable and update the piece appearance if needed
    if (player_turn == "R" and row_to == 7) or (player_turn == "G" and row_to == 0):
        board[row_to][col_to] += "K"
        # If you change the appearance for kings, update the piece on the canvas here

    canvas.delete('highlight')  # Clear highlights

    # After moving, check for further captures from the new position
    further_captures = find_possible_moves((row_to, col_to))
    if any(abs(row_to - row) == 2 for (row, _) in further_captures):
        selected_piece = (row_to, col_to)
        possible_moves = further_captures
        highlight_moves(possible_moves)
    else:
        switch_turns()
        check_for_victory()

    # Update the piece_ids dictionary for the new position
    piece_ids[to_pos] = piece_id
    if from_pos in piece_ids:
        del piece_ids[from_pos]


def save_state():
    """Saves the current game state."""
    global move_history
    state = ([row[:] for row in board], player_turn)
    move_history.append(state)

def undo_move():
    """Reverts the board to the previous state."""
    global board, player_turn
    if move_history:
        move_history.pop()  # Remove the current state
        if move_history:
            board, player_turn = move_history.pop()
            draw_board()
            update_turn_label()
        else:
            print("No more moves to undo.")
    else:
        print("No moves have been made yet.")

def reset_game():
    """Resets the game to its initial state."""
    global board, move_history, player_turn, selected_piece, possible_moves
    board = [[None for _ in range(8)] for _ in range(8)]
    player_turn = "R"
    selected_piece = None
    possible_moves = []
    move_history = []
    initialize_board()
    draw_board()

def update_turn_label():
    """Updates the turn label to display the current player's turn."""
    turn_text = "Red's Turn" if player_turn == "R" else "Green's Turn"
    turn_label.config(text=turn_text)

def animate_move(from_pos, to_pos, piece_id):
    """Animate the movement of a piece from from_pos to to_pos."""
    from_x, from_y = from_pos[1] * 80 + 40, from_pos[0] * 80 + 40  # Center of the square
    to_x, to_y = to_pos[1] * 80 + 40, to_pos[0] * 80 + 40  # Center of the target square

    # Calculate the pixel distance to move
    x_distance = to_x - from_x
    y_distance = to_y - from_y

    # Calculate the number of steps for the animation
    steps = 20
    x_step = x_distance / steps
    y_step = y_distance / steps

    for _ in range(steps):
        canvas.move(piece_id, x_step, y_step)
        canvas.update()
        time.sleep(0.02)  # Adjust for smoother or faster animation


# Setup the game window and canvas
root = tk.Tk()
root.title("Checkers")
canvas = tk.Canvas(root, width=640, height=640)
canvas.pack()
canvas.bind("<Button-1>", on_canvas_click)

# Define turn label before initializing the board or drawing the initial setup
turn_label = tk.Label(root, text="", font=('Helvetica', 16))
turn_label.pack()

# Now that turn_label is defined, you can initialize the board
initialize_board()  # This function now can safely call update_turn_label

# Add undo/reset buttons after the board has been initialized
undo_button = tk.Button(root, text="Undo Move", command=undo_move)
undo_button.pack()

reset_button = tk.Button(root, text="Reset Game", command=reset_game)
reset_button.pack()

# Display victory status
victory_label = tk.Label(root, text="", font=('Helvetica', 16))
victory_label.pack()

# Play again button (you can choose to only show it after the game is over or always visible)
play_again_button = tk.Button(root, text="Play Again", command=play_again)
play_again_button.pack()

root.mainloop()
