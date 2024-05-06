import pyautogui
from stockfish import Stockfish
from collections import namedtuple
import time

Point = namedtuple("Point", ["x", "y"])


class Chessboard:
    def get_initial_board_position(self):
        """Retrieves the initial position of the chessboard by capturing the coordinates
        of the upper left and bottom right corners and checks if the board is black or white.

        Returns:
            Tuple[int, int]: The x and y coordinates of the upper left corner of the chessboard.
            str: The color of the chessboard ("black" or "white").
        """
        return Point(19, 182), Point(785, 948), "black"

    def calculate_centers(
        self, upper_left_corner: Point, lower_right_corner: Point
    ) -> list:
        """Calculate the centers of the squares in a grid.

        Args:
            upper_left_corner (Point): The coordinates of the upper left corner of the grid.
            lower_right_corner (Point): The coordinates of the lower right corner of the grid.

        Returns:
            list: A list of lists containing the coordinates of the centers of the squares in the grid.
        """
        square_width = (lower_right_corner.x - upper_left_corner.x) / 8
        square_height = (lower_right_corner.y - upper_left_corner.y) / 8
        centers = []
        for row in range(8):
            row_coords = []
            for col in range(8):
                x = upper_left_corner.x + (col + 0.5) * square_width
                y = upper_left_corner.y + (row + 0.5) * square_height
                row_coords.append(Point(x, y))
            centers.append(row_coords)
        return centers

    def make_screenshot(
        self, point1: Point, point2: Point, filename="screenshot.png"
    ) -> None:
        """Takes a screenshot of a region defined by the coordinates (x1, y1) and (x2,y2) and saves it to a file.

        Args:
            point1 (Tuple[int, int]): The coordinates of the top-left corner of the region to capture.
            point2 (Tuple[int, int]): The coordinates of the bottom-right corner of the region to capture.
            filename (str, optional): The name of the file to save the screenshot to. Defaults to "screenshot.png".

        Returns:
            None
        """
        x1, y1 = point1
        x2, y2 = point2

        screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        screenshot.save(filename)

    def make_move(self, board_coords: list, move: str) -> None:
        """Simulates the movement of a chess piece on a chessboard using classical algebraic notation.

        Args:
            board_coords (List[List[Point]]): A matrix of Points with the coordinates of the squares on the board.
            move (str): A string representing the move in classical algebraic notation (e.g., "e2e4").

        This function interprets the move in classical algebraic notation and clicks on the corresponding coordinates
        to simulate the movement of a chess piece on a chessboard.
        """
        # Convert the chess move in algebraic notation to screen coordinates
        origin_column = ord(move[0]) - ord("a")
        origin_row = 8 - int(move[1])
        dest_column = ord(move[2]) - ord("a")
        dest_row = 8 - int(move[3])

        # Get the coordinates of origin and destination
        origin = board_coords[origin_row][origin_column]
        destination = board_coords[dest_row][dest_column]

        # Click on the origin and then the destination square
        pyautogui.click(origin.x, origin.y)
        pyautogui.click(destination.x, destination.y)


class ChessEngine:
    def __init__(self, stockfish_path):
        self.stockfish = Stockfish(path=stockfish_path)

    def get_board_from_screenshot(self, board_screenshot_filename: str) -> list:
        """Given the filename of a board screenshot, this function reads the image, processes it to determine
        the position of each chess piece on the board, and returns a list of lists representing the board.
        Each inner list corresponds to a row of the board and contains the piece at that position
        (e.g., "b" for a black bishop, "K" for a white king, "-" for an empty square).

        Args:
            board_screenshot_filename (str): A string representing the filename of the board screenshot.

        Returns:
            list: A list of lists representing the board, where each inner list corresponds to
            a row of the board and contains the piece at that position.
        """
        return [
            ["R", "-", "B", "K", "-", "-", "-", "R"],
            ["-", "P", "P", "-", "P", "-", "-", "-"],
            ["-", "-", "-", "P", "-", "-", "-", "-"],
            ["P", "b", "-", "-", "-", "-", "n", "-"],
            ["-", "-", "-", "-", "P", "-", "-", "-"],
            ["p", "p", "B", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "p", "p"],
            ["-", "k", "-", "r", "-", "-", "-", "r"],
        ]

    def board_to_fen(self, board_pieces: list, color_to_move: str) -> str:
        """Converts a chess board representation to Forsyth-Edwards Notation (FEN).

        Args:
            board_pieces (list): A 2D list representing the chess board. Each elementin the list represents
            a square on the board. The list is indexed starting from the bottom-left corner of the board,
            with the top-left square being at index [0][0] and the bottom-right square being at index [7][7].

        Returns:
            str: The FEN string representing the chess board.
        """

        fen = ""
        for row in range(8, 0, -1):
            empty_counter = 0
            for column in range(1, 9):
                square = board_pieces[8 - row][column - 1]
                if square == "-":
                    empty_counter += 1
                else:
                    if empty_counter > 0:
                        fen += str(empty_counter)
                        empty_counter = 0
                    fen += square
            if empty_counter > 0:
                fen += str(empty_counter)
            fen += "/"

        # Delete the last slash since it's unnecessary
        fen = fen[:-1]

        # Add the necessary additional information to the FEN
        if color_to_move == "black":
            fen += " w - - 0 1"
        else:
            fen += " b - - 0 1"

        return fen

    def calculate_stockfish(self, fen: str):
        """Calculates the best move using Stockfish for a given FEN position.

        Args:
            fen (str): The Forsyth-Edwards Notation representing the chess board position.

        Returns:
            str: The best move suggested by Stockfish based on the input FEN position.
        """
        if self.stockfish.is_fen_valid(fen):
            self.stockfish.set_fen_position(fen)
            return self.stockfish.get_best_move()
        else:
            print("Invalid FEN")
            return None


def main():
    chessboard = Chessboard()
    chess_engine = ChessEngine(stockfish_path="stockfish-windows-x86-64-avx2.exe")

    # Get the initial board position
    upper_left_corner, lower_right_corner, color = (
        chessboard.get_initial_board_position()
    )
    print(f"Got initial chessboard position: {upper_left_corner}, {lower_right_corner}")

    # Calculate the centers of the squares
    square_centers = chessboard.calculate_centers(upper_left_corner, lower_right_corner)
    if color == "black":
        square_centers = [list(reversed(row)) for row in reversed(square_centers)]

    start_time = time.time()
    while time.time() - start_time < 90:
        chessboard.make_screenshot(upper_left_corner, lower_right_corner)
        board = chess_engine.get_board_from_screenshot(
            board_screenshot_filename="screenshot.png"
        )

        # Flip the board if the color is black so we get the notation from the white point of view
        if color == "black":
            print("Starting as black, flipping board")
            board = [list(reversed(row)) for row in reversed(board)]

        fen = chess_engine.board_to_fen(board, color_to_move=color)
        print(f"FEN notation: {fen}")

        best_move = chess_engine.calculate_stockfish(fen)
        if best_move is not None:
            if color == "black":
                print(chess_engine.stockfish.get_board_visual(False))
            else:
                print(chess_engine.stockfish.get_board_visual())

            print(f"Stockfish best move for the current position: {best_move}")
            print("Making move...\n")
            chessboard.make_move(square_centers, best_move)
            print("---------------------------------------------\n")
        else:
            print("Invalid FEN")


if __name__ == "__main__":
    main()
