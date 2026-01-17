"""
User-level orchestration for analysing chess games.

This version is PGN-first:
- Games are loaded from PGN files (via Extract)
- No DB reads for game ingestion
- Database is used only for analysis output (move_data)
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from typing import Tuple
from typing import Optional

import chess.pgn

from betterchess.core.game import Game
from betterchess.utils.extract import Extract
from betterchess.utils.handlers import (
    EnvHandler,
    FileHandler,
    InputHandler,
    RunHandler,
)


@dataclass
class User:
    """Sets up and runs the analysis for all games for a specified user."""

    input_handler: InputHandler
    file_handler: FileHandler
    run_handler: RunHandler
    env_handler: EnvHandler

    def analyse(self) -> None:
        """Extracts user PGNs and runs analysis."""
        self.extract = Extract(
            self.input_handler,
            self.file_handler,
            self.run_handler,
            self.env_handler,
        )

        # PGN-based extraction (in-memory)
        self.extract.run_data_extract(
            self.input_handler.username,
            self.file_handler.path_userlogfile,
            self.run_handler.logger,
        )

        self.run_analysis()

    def run_analysis(self) -> None:
        """Runs Stockfish analysis on all extracted PGN games."""
        all_games = self.extract.games
        tot_games = len(all_games)

        cleandown = Cleandown()
        cleandown.previous_run(
            self.file_handler.path_userlogfile,
            self.file_handler.path_database,
            self.input_handler.username,
            self.env_handler,
        )

        print(f"Analysing users data: {tot_games} games")

        for game_num, chess_game in enumerate(all_games):
            prepare_users = PrepareUsers()
            prepare_users.current_game(
                self.file_handler.path_temp,
                chess_game,
            )

            iter_metadata = {
                "game_num": game_num,
                "tot_games": tot_games,
            }

            game = Game(
                self.input_handler,
                self.file_handler,
                self.run_handler,
                self.env_handler,
                iter_metadata,
            )
            game.run_game_analysis()
            del game


@dataclass
class PrepareUsers:
    """Handles per-run preparation utilities."""

    def current_game(self, path_temp: str, chess_game: chess.pgn.Game) -> None:
        """
        Writes the current game to temp.pgn correctly using python-chess exporter.

        Args:
            path_temp (str): Path to temporary PGN file.
            chess_game (chess.pgn.Game): Game to analyse.
        """
        with open(path_temp, mode="w", encoding="utf-8") as temp_file:
            exporter = chess.pgn.FileExporter(temp_file)
            chess_game.accept(exporter)


@dataclass
class Cleandown:
    """Cleans down the previous run (unfinished analysis cleanup)."""

    def previous_run(
        self,
        path_userlogfile: str,
        path_database: str,
        username: str,
        env_handler: EnvHandler,
    ) -> None:
        """Runs the cleanup of the previous run."""
        game_num = self.get_last_logged_game_num(path_userlogfile)
        if game_num is not None:
            self.clean_sql_table(
                path_database,
                game_num,
                username,
                env_handler,
            )

    def clean_sql_table(
    self,
    path_database: str,
    game_num: int,
    username: str,
    env_handler: EnvHandler,
) -> None:
        if env_handler.db_type == "sqlite":
            conn = sqlite3.connect(path_database)
            curs = conn.cursor()
            sql_query = """
                DELETE FROM move_data
                WHERE Game_number = :game_num
                AND Username = :username
            """
            params = {"game_num": game_num, "username": username}
            try:
                curs.execute(sql_query, params)
                conn.commit()
            except sqlite3.OperationalError:
                # move_data table does not exist yet
                pass
            finally:
                curs.close()
                conn.close()


    def get_last_logged_game_num(self, path_userlogfile: str) -> Optional[int]:
        """
        Safely gets the last logged game number.
        Returns None if no valid game log exists.
        """
        if not self.logfile_not_empty(path_userlogfile):
            return None

        log_list = self.get_game_log_list(path_userlogfile)

        for line in reversed(log_list):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4 and parts[3].isdigit():
                return int(parts[3])

        # No valid game entry found
        return None


    def logfile_not_empty(self, path_userlogfile: str) -> bool:
        """Checks whether logfile contains entries."""
        with open(path_userlogfile, mode="r") as log_file:
            return bool(log_file.readlines())

    def get_game_log_list(self, path_userlogfile: str) -> list:
        """Returns list of logged game entries."""
        game_log_list = []
        with open(path_userlogfile, mode="r") as log_file:
            lines = log_file.readlines()
            self.logfile_line_checker_multi(game_log_list, lines)
        return game_log_list

    def logfile_line_checker_multi(self, game_log_list: list, lines: list[str]) -> None:
        game_log_list.extend(
            line for line in lines if line.count("|") >= 3
        )

