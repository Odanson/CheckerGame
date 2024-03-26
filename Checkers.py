import tkinter as tk

def create_checkerboard(canvas):
    # Draws an 8x8 checkerboard on the canvas
    color1 = "white"
    color2 = "black"
    for row in range(8):
        for col in range(8):
            # Calculate square corners
            x1 = col * 80
            y1 = row * 80
            x2 = x1 + 80
            y2 = y1 + 80
            # Set square color based on position
            color = color1 if (row + col) % 2 == 0 else color2
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

def place_initial_pieces(canvas):
    # Place initial pieces for both players
    for row in range(3):
        for col in range(8):
            # Pieces should be placed on squares of one color
            if (row + col) % 2 != 0:
                create_piece(canvas, row, col, "red")  # Player 1 pieces
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 != 0:
                create_piece(canvas, row, col, "green")  # Player 2 pieces

def create_piece(canvas, row, col, color):
    # Draws a piece on the board
    x1 = col * 80 + 20
    y1 = row * 80 + 20
    x2 = x1 + 40
    y2 = y1 + 40
    canvas.create_oval(x1, y1, x2, y2, fill=color, outline="gray")

def main():
    # Initialize the main window and draw the board and pieces
    root = tk.Tk()
    root.title("Checkers")
    canvas = tk.Canvas(root, width=640, height=640)
    canvas.pack()

    create_checkerboard(canvas)  # Draw the checkerboard
    place_initial_pieces(canvas)  # Place the initial pieces

    root.mainloop()

if __name__ == "__main__":
    main()
