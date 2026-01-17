import chess.pgn
from pathlib import Path

def load_games_from_user_pgns(username: str):
    base_dir = Path("pgns") / username

    files = {
        "black": base_dir / f"{username}-black.pgn",
        "white": base_dir / f"{username}-white.pgn",
    }

    games = []

    for color, pgn_file in files.items():
        if not pgn_file.exists():
            continue

        with open(pgn_file, encoding="utf-8") as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break

                # annotate game with user's color
                game.user_color = color
                games.append(game)

    return games
