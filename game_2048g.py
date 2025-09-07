#!/usr/bin/env python3
"""
2048 terminal game (Python 3.8+)

Author: ChatGPT
"""

import curses
import random
import sys
import time

# ----------------------------------------
# 盤面（4x4）の操作
# ----------------------------------------
SIZE = 4  # 盤面サイズ

def new_game():
    """新しいゲームを初期化"""
    board = [[0] * SIZE for _ in range(SIZE)]
    add_random_tile(board)
    add_random_tile(board)
    return board

def add_random_tile(board):
    """空セルに 2 か 4 をランダムで追加"""
    empty = [(r, c) for r in range(SIZE)
             for c in range(SIZE) if board[r][c] == 0]
    if not empty:
        return
    r, c = random.choice(empty)
    board[r][c] = 4 if random.random() < 0.1 else 2

def compress(row):
    """行を左へ詰める（0 を除外）"""
    new_row = [v for v in row if v != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row

def merge(row):
    """左に詰めた行で隣り合う同じ数字をマージ"""
    for i in range(SIZE - 1):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            row[i + 1] = 0
    return row

def move_left(board):
    """左移動"""
    moved = False
    new_board = []
    for row in board:
        compressed = compress(row)
        merged = merge(compressed)
        final = compress(merged)
        if final != row:
            moved = True
        new_board.append(final)
    return new_board, moved

def transpose(board):
    """行↔列"""
    return [list(row) for row in zip(*board)]

def reverse(board):
    """各行を反転"""
    return [list(reversed(row)) for row in board]

def move(board, direction):
    """
    direction: 'up', 'down', 'left', 'right'
    Returns: (new_board, moved_bool)
    """
    if direction == 'left':
        return move_left(board)
    elif direction == 'right':
        rev = reverse(board)
        moved_board, moved = move_left(rev)
        return reverse(moved_board), moved
    elif direction == 'up':
        trans = transpose(board)
        moved_board, moved = move_left(trans)
        return transpose(moved_board), moved
    elif direction == 'down':
        trans = transpose(board)
        rev = reverse(trans)
        moved_board, moved = move_left(rev)
        return transpose(reverse(moved_board)), moved
    else:
        return board, False

def won(board):
    """2048 が出たら True"""
    return any(2048 in row for row in board)

def lost(board):
    """全セル埋まり、かつ移動不可能なら False"""
    if any(0 in row for row in board):
        return False
    # すべての隣接セルをチェック
    for r in range(SIZE):
        for c in range(SIZE):
            if r + 1 < SIZE and board[r][c] == board[r + 1][c]:
                return False
            if c + 1 < SIZE and board[r][c] == board[r][c + 1]:
                return False
    return True

# ----------------------------------------
# 描画
# ----------------------------------------
def draw_board(stdscr, board, score, best):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "2048 (Python Terminal)"
    stdscr.addstr(0, (w - len(title)) // 2, title, curses.A_BOLD)

    # スコア表示
    score_str = f"Score: {score}  Best: {best}"
    stdscr.addstr(1, (w - len(score_str)) // 2, score_str)

    # ボード描画
    cell_width = 6
    start_y = 3
    start_x = (w - cell_width * SIZE) // 2

    for r in range(SIZE):
        for c in range(SIZE):
            val = board[r][c]
            if val == 0:
                text = " ".center(cell_width)
            else:
                text = str(val).center(cell_width)
            y = start_y + r * 2
            x = start_x + c * cell_width
            # 背景色を値に応じて変える（簡易的に）
            if val == 0:
                color = curses.color_pair(0)
            elif val <= 4:
                color = curses.color_pair(1)
            elif val <= 16:
                color = curses.color_pair(2)
            elif val <= 64:
                color = curses.color_pair(3)
            elif val <= 256:
                color = curses.color_pair(4)
            elif val <= 1024:
                color = curses.color_pair(5)
            else:
                color = curses.color_pair(6)

            stdscr.addstr(y, x, text, color | curses.A_BOLD)

    # ガイド
    help_str = "Use arrow keys or WASD. R = restart, Q = quit."
    stdscr.addstr(start_y + SIZE * 2 + 1, (w - len(help_str)) // 2, help_str, curses.A_DIM)
    stdscr.refresh()

# ----------------------------------------
# Curses 初期化
# ----------------------------------------
def init_colors():
    curses.start_color()
    curses.use_default_colors()
    # 色パレット: 0=黒, 1=緑, 2=黄, 3=青, 4=マゼンタ, 5=赤, 6=白
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)

# ----------------------------------------
# メインループ
# ----------------------------------------
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)   # 非ブロッキング入力
    stdscr.keypad(True)    # キーコード取得
    init_colors()

    board = new_game()
    score = 0
    best = 0

    while True:
        draw_board(stdscr, board, score, best)

        if won(board):
            stdscr.addstr(2, 0, "You won! Press 'r' to restart or 'q' to quit.", curses.A_BLINK)
        elif lost(board):
            stdscr.addstr(2, 0, "Game Over! Press 'r' to restart or 'q' to quit.", curses.A_BLINK)

        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break  # Ctrl-C で終了

        if key == -1:
            time.sleep(0.05)
            continue

        direction = None
        if key in (curses.KEY_LEFT, ord('a'), ord('A')):
            direction = 'left'
        elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
            direction = 'right'
        elif key in (curses.KEY_UP, ord('w'), ord('W')):
            direction = 'up'
        elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
            direction = 'down'
        elif key in (ord('q'), ord('Q')):
            break
        elif key in (ord('r'), ord('R')):
            board = new_game()
            score = 0
            continue

        if direction:
            new_board, moved = move(board, direction)
            if moved:
                board = new_board
                add_random_tile(board)
                # スコアは合体したセルの和
                score = sum(cell for row in board for cell in row if cell > 0)
                if score > best:
                    best = score

    # 退避メッセージ
    stdscr.nodelay(False)
    stdscr.addstr(SIZE * 2 + 6, 0, "Thanks for playing! Press any key to exit.")
    stdscr.getch()

# ----------------------------------------
# エントリポイント
# ----------------------------------------
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error:
        print("Curses error: Make sure your terminal supports colors.")
        sys.exit(1)
