# Tactic Extractor

Python scripts to extract tactics from a given pgn file. The code idea is from [https://github.com/clarkerubber/Python-Puzzle-Creator](https://github.com/clarkerubber/Python-Puzzle-Creator). The code is written using the latest `python-chess` version for better use.

## Usage

**Use Python version 3.6 or above**

- First run the below code

```bash
python3 tactic-extractor/main.py --pgn='pgn-file-location' --stockfish='stockfish-location' [-q]
```

- Next run the below code to display the puzzles created

```bash
python3 chessshow.py
```

## Install Requirements :

```bash
pip install -r requirements.txt
```
