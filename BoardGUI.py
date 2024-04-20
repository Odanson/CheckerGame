import tkinter
from CheckerGame import *
from tkinter.font import Font


class BoardGUI:
    def __init__(self, game):
        self.game = game
        self.ROWS = 8
        self.COLS = 8
        self.WINDOW_WIDTH = 800  # Adjust window size if needed
        self.WINDOW_HEIGHT = 800
        self.col_width = self.WINDOW_WIDTH / self.COLS
        self.row_height = self.WINDOW_HEIGHT / self.ROWS
        self.initBoard()

    def initBoard(self):
        self.root = tkinter.Tk()
        self.c = tkinter.Canvas(self.root, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT,
                                borderwidth=5, background='white')
        self.c.pack()
        self.board = [[0] * self.COLS for _ in range(self.ROWS)]
        self.tiles = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]

        # Print dark square
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.c.create_rectangle(i * self.row_height, j * self.col_width,
                                            (i + 1) * self.row_height, (j + 1) * self.col_width, fill="gray",
                                            outline="gray")

        # Print grid lines
        for i in range(8):
            self.c.create_line(0, self.row_height * i, self.WINDOW_WIDTH, self.row_height * i, width=2)
            self.c.create_line(self.col_width * i, 0, self.col_width * i, self.WINDOW_HEIGHT, width=2)

        # Place checks on the board
        self.updateBoard()

        # Initialize parameters
        self.checkerSelected = False
        self.clickData = {"row": 0, "col": 0, "checker": None}

        # Register callback function for mouse clicks
        self.c.bind("<Button-1>", self.processClick)

        # make GUI updates board every second
        self.root.after(1000, self.updateBoard)

        self.rules_button = tkinter.Button(self.root, text="Show Rules", command=self.show_rules)
        self.rules_button.pack(side=tkinter.BOTTOM)

        # Help button
        help_button = tkinter.Button(self.root, text="Help", command=self.show_help)
        help_button.pack(side=tkinter.BOTTOM)

    def show_rules(self):
        # Create a top-level window to display the rules
        rules_window = tkinter.Toplevel(self.root)
        rules_window.title("Game Rules")

        # Define custom fonts
        title_font = Font(family="Helvetica", size=16, weight="bold")
        text_font = Font(family="Helvetica", size=12)

        # Title Label
        title_label = tkinter.Label(rules_window, text="Checkers Game Rules", font=title_font, fg='black', bg='white')
        title_label.pack(side=tkinter.TOP, pady=10)  # padding for better spacing

        # Rules Text
        rules_text = tkinter.Text(rules_window, height=15, width=70, font=text_font, wrap=tkinter.WORD, fg='white',
                                  bg='black', padx=10, pady=10, bd=2, relief=tkinter.SUNKEN)
        rules_text.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # Define the rules text
        rules = """
    1. Each player starts with 12 pieces on the three rows closest to them.
    2. Pieces can only move diagonally on dark tiles.
    3. Regular pieces move forward one tile; kings can move forward and backward.
    4. Capture opponent pieces by jumping over them diagonally.
    5. Reach the farthest row to turn a regular piece into a king.
    6. The player with no pieces left or no possible moves loses."""
        rules_text.insert(tkinter.END, rules)
        rules_text.config(state=tkinter.DISABLED, bg="#27333f")

        # Add a button to close the pop-up window with styling
        close_button = tkinter.Button(rules_window, text="Close", command=rules_window.destroy, font=text_font,
                                      relief=tkinter.RAISED, bd=2)
        close_button.pack(side=tkinter.BOTTOM, pady=10)  # padding for better spacing

        # Style the window background
        rules_window.configure(background='white')

        # Center the window on the screen
        self.center_window(rules_window)

    def show_help(self):
        # Create a top-level window to display the help information
        help_window = tkinter.Toplevel(self.root)
        help_window.title("Help")

        # Define custom fonts
        text_font = Font(family="Helvetica", size=12)

        # Title Label
        title_label = tkinter.Label(help_window, text="Help", font=text_font, fg='black', bg='white')
        title_label.pack(side=tkinter.TOP, pady=10)  # padding for better spacing

        # Help Text
        help_text = tkinter.Text(help_window, height=15, width=60, font=text_font, wrap=tkinter.WORD, padx=10,
                                 fg='white', bg='black', pady=10, bd=2, relief=tkinter.SUNKEN)
        help_text.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # Define the help text
        instructions = """How to play:
    1. Click on a piece to select it.
    2. Click on a highlighted square to move the selected piece.
    3. Jump over the opponent's pieces to capture them.

    For more detailed rules, refer to the 'Game Rules' section."""
        help_text.insert(tkinter.END, instructions)
        help_text.config(state=tkinter.DISABLED, bg="#27333f")  # Disable editing of the text widget

        # Add a button to close the pop-up window
        close_button = tkinter.Button(help_window, text="Close", command=help_window.destroy, font=text_font,
                                      relief=tkinter.RAISED, bd=2)
        close_button.pack(side=tkinter.TOP, pady=10)

        # Style the window background
        help_window.configure(background='white')

        # Center the help window on the screen (assuming you have a `center_window` method)
        self.center_window(help_window)

    def center_window(self, win):
        # Update "win" to calculate width and height, so geometry is set correctly
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def startGUI(self):
        self.root.mainloop()

    def pauseGUI(self):
        self.c.bind("<Button-1>", '')

    def resumeGUI(self):
        self.c.bind("<Button-1>", self.processClick)

    # Update the positions of checkers
    def updateBoard(self):
        if self.game.isBoardUpdated():
            newBoard = self.game.getBoard()
            for i in range(len(self.board)):
                for j in range(len(self.board[0])):
                    if self.board[i][j] != newBoard[i][j]:
                        self.board[i][j] = newBoard[i][j]
                        self.c.delete(self.tiles[i][j])
                        self.tiles[i][j] = None

                        # choose different color for different player's checkers
                        if newBoard[i][j] < 0:
                            self.tiles[i][j] = self.c.create_oval(j * self.col_width + 10, i * self.row_height + 10,
                                                                  (j + 1) * self.col_width - 10,
                                                                  (i + 1) * self.row_height - 10,
                                                                  fill="green")
                        elif newBoard[i][j] > 0:
                            self.tiles[i][j] = self.c.create_oval(j * self.col_width + 10, i * self.row_height + 10,
                                                                  (j + 1) * self.col_width - 10,
                                                                  (i + 1) * self.row_height - 10,
                                                                  fill="red")
                        else:  # no checker
                            continue

                        # raise the tiles to highest layer
                        self.c.tag_raise(self.tiles[i][j])

            # tell game logic that GUI has updated the board
            self.game.completeBoardUpdate()

        # make GUI updates board every second
        self.root.after(1000, self.updateBoard)

    # this function checks if the checker belongs to the current player
    # if isPlayerTurn() returns True, then it is player's turn and only
    # postive checkers can be moved. Vice versa.
    def isCurrentPlayerChecker(self, row, col):
        return self.game.isPlayerTurn() == (self.board[row][col] > 0)

    # callback function that process user's mouse clicks
    def processClick(self, event):
        col = int(event.x // self.col_width)
        row = int(event.y // self.row_height)

        # If there is no checker being selected
        if not self.checkerSelected:
            # there exists a checker at the clicked position
            # and the checker belongs to the current player
            if self.board[row][col] != 0 and self.isCurrentPlayerChecker(row, col):
                self.clickData["row"] = row
                self.clickData["col"] = col
                self.clickData["color"] = self.c.itemcget(self.tiles[row][col], 'fill')

                # replace clicked checker with a temporary checker
                self.c.delete(self.tiles[row][col])
                self.tiles[row][col] = self.c.create_oval(col * self.col_width + 10, row * self.row_height + 10,
                                                          (col + 1) * self.col_width - 10,
                                                          (row + 1) * self.row_height - 10,
                                                          fill="yellow")
                self.checkerSelected = True

            else:  # no checker at the clicked postion
                return

        else:  # There is a checker being selected
            # First reset the board
            oldrow = self.clickData["row"]
            oldcol = self.clickData["col"]
            self.c.delete(self.tiles[oldrow][oldcol])
            self.tiles[oldrow][oldcol] = self.c.create_oval(oldcol * self.col_width + 10, oldrow * self.row_height + 10,
                                                            (oldcol + 1) * self.col_width - 10,
                                                            (oldrow + 1) * self.row_height - 10,
                                                            fill=self.clickData["color"])

            # If the destination leads to a legal move
            self.game.move(self.clickData["row"], self.clickData["col"], row, col)
            self.checkerSelected = False
