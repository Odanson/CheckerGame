from CheckerGame import CheckerGame

if __name__ == "__main__":
    game = None
    try:
        game = CheckerGame()  # Instantiating CheckerGame starts the game and GUI
    except KeyboardInterrupt:
        print("Game was interrupted by the user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if game:
            try:
                # Assuming shutdown() is a method that properly closes the application
                game.shutdown()  # Clean up resources, close windows, etc.
            except Exception as e:
                print(f"Error during shutdown: {e}")
        print("Exiting game. Goodbye!")
