# Better Chess (Fork)

> **Note**  
> This repository is a fork of the original **BetterChess** project by **Aidan Inceer**.  
> It includes significant architectural and analytical extensions while preserving
> the original MIT license and attribution.

---

## Overview

Better Chess enables bulk analysis of chess games using the Stockfish engine to extract
move-level and game-level insights.

This fork focuses on **robustness, extensibility, and offline analysis** by introducing
a **PGN-first data pipeline** and a stable SQLite-based storage layer.

---

## Architectural Changes in This Fork

### 1. PGN-First Analysis Pipeline

**Original Design**
- Games fetched directly from the chess.com API
- Dependent on external API availability

**Updated Design**
- Games loaded directly from local PGN files
- Supports separate PGNs for White and Black games
- Enables fully offline and reproducible analysis

Example structure:
```txt
pgns/
└── ozil_33/
    ├── ozil_33-white.pgn
    └── ozil_33-black.pgn
```

## 2. SQLite as Default Persistence Layer

- SQLite is the default database backend
- Move-level and game-level data stored persistently
- Enables fast querying and downstream analytics

### Tables

- `move_data`
- `game_data`

---

## 3. Explicit Schema Management

- Database schema initialized once per project
- Schema aligned exactly with Pandas DataFrames
- Prevents runtime insert and column mismatch errors
- No schema mutations during analysis execution

---

## 4. Robust Engine and Edge-Case Handling

- Defensive handling of missing clock data in PGNs
- Safe evaluation parsing for mate scores
- Engine fallback logic for endgame and forced-mate scenarios
- Prevents crashes during large batch runs

---

## 5. Clean Dependency Injection

- `FileHandler`, `EnvHandler`, `RunHandler`, and `InputHandler` are initialized once
- No repeated re-instantiation inside move or game loops
- Clear separation of responsibilities across modules

---

## Extracted Move-Level Features

Each analysed move includes:

- Engine evaluation
- Best-move comparison
- Evaluation loss
- Accuracy score
- Move classification
- Piece type
- Move colour
- Castling information
- Time spent per move (when available)

---

## Installation and Setup

### Requirements

- Python `3.9`
- Stockfish (local binary)

### Environment Setup

```sh
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root:

```conf
# Database
DB_TYPE=sqlite

# Stockfish configuration
stockfish_folder=stockfish-windows-x86-64-avx2
stockfish_exe_file=stockfish-windows-x86-64-avx2.exe
```

# Running the Project
Run the application:

```
python main.py
```


### Options

- `run` – Analyse PGN games  
- `manage` – Inspect or reset the database

---

## Intended Use Cases

- Personal chess improvement and self-analysis  
- Feature generation for machine learning projects  
- Longitudinal performance tracking  
- Portfolio demonstration of real-world data pipelines  

---

## Credits

### Original Author

- **Aidan Inceer**  
- Repository: https://github.com/AidanInceer/BetterChess  
- License: MIT  

### Fork Maintainer

- **Prasad Jagadale**

#### Contributions in this fork

- PGN-first ingestion architecture  
- SQLite-first persistence layer  
- Schema-safe ETL pipeline  
- Engine robustness improvements  
- Extended move-level analytics  

---

## License

This project is licensed under the **MIT License**.  
All original license terms and attributions are preserved.


