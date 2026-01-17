import sqlite3
import pandas as pd

DB_PATH = "data/betterchess.db"

columns = [
    "Username",
    "Game_date",
    "Engine_depth",
    "Game_number",
    "Move_number",
    "Move",
    "Move_eval",
    "Best_move",
    "Best_move_eval",
    "Move_eval_diff",
    "Move_accuracy",
    "Move_type",
    "Piece",
    "Move_colour",
    "Castling_type",
    "White_castle_num",
    "Black_castle_num",
    "Move_time",
]

conn = sqlite3.connect(DB_PATH)

pd.DataFrame(columns=columns).to_sql(
    "move_data",
    conn,
    if_exists="replace",
    index=False
)

conn.close()
print("✅ move_data table initialized")
