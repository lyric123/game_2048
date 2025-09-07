#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2048 1画面対戦型（プレイヤー ↔ コンピュータ）
Python 3.8+ で動作

- コンピュータは自動で動く
- ターン表示は一切出力しない
"""

import curses
import random
import sys
import time

# ---------- 盤面（4x4）の操作 ----------
SIZE = 4

def new_game() -> list:
    board = [[0] * SIZE for _ in range(SIZE)]
    add_random_tile(board)
    add_random_tile(board)
    return board

def add_random_tile(board: list) -> None:
    empty = [(r, c) for r in range(SIZE)
             for c in range(SIZE) if board[r][c] == 0]
    if not empty:
        return
    r, c = random.choice(empty)
    board[r][c] = 4 if random.random() < 0.1 else 2

def compress(row: list) -> list:
    non_zero = [v for v in row if v != 0]
    non_zero += [0] * (SIZE - len(non_zero))
    return non_zero

def merge(row: list) -> list:
    for i in range(SIZE - 1):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            row[i + 1] = 0
    return row

def move_left(board: list) -> tuple:
    moved = False
    new_board = []
    for row in board:
        c = compress(row)
        m = merge(c)
        f = compress(m)
        if f != row:
            moved = True
        new_board.append(f)
    return new_board, moved

def transpose(board: list) -> list:
    return [list(row) for row in zip(*board)]

def reverse(board: list) -> list:
    return [list(reversed(row)) for row in board]

def move(board: list, direction: str) -> tuple:
    if direction == 'left':
        nb, mv = move_left(board)
    elif direction == 'right':
        nb, mv = move_left(reverse(board))
        nb = reverse(nb)
    elif direction == 'up':
        nb, mv = move_left(transpose(board))
        nb = transpose(nb)
    elif direction == 'down':
        nb, mv = move_left(reverse(transpose(board)))
        nb = transpose(reverse(nb))
    else:
        return board, False, 0

    gained = sum(nb[i][j] for i in range(SIZE)
                 for j in range(SIZE) if nb[i][j] > board[i][j])
    return nb, mv, gained

def won(board: list) -> bool:
    return any(2048 in row for row in board)

def lost(board: list) -> bool:
    if any(0 in row for row in board):
        return False
    for r in range(SIZE):
        for c in range(SIZE):
            if r + 1 < SIZE and board[r][c] == board[r + 1][c]:
                return False
            if c + 1 < SIZE and board[r][c] == board[r][c + 1]:
                return False
    return True

# ---------- コンピュータ側の簡易 AI ----------
def computer_choose_move(board: list) -> str | None:
    moves = []
    for d in ('up', 'down', 'left', 'right'):
        _, mv, _ = move(board, d)
        if mv:
            moves.append(d)
    return random.choice(moves) if moves else None

# ---------- 描画 ----------
def draw_board(stdscr, board, score_p, score_c, turn):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title = "2048 1画面対戦 (HJKL: 移動, R: 再開, Q: 終了)"
    stdscr.addstr(0, (w - len(title)) // 2, title, curses.A_BOLD)

    score_str = f"Player: {score_p}   Computer: {score_c}"
    stdscr.addstr(1, (w - len(score_str)) // 2, score_str)

    cell_w = 6
    start_y = 3
    start_x = (w - cell_w * SIZE) // 2

    # 盤面描画
    for r in range(SIZE):
        for c in range(SIZE):
            val = board[r][c]
            txt = (" ".center(cell_w) if val == 0
                   else str(val).center(cell_w))
            y, x = start_y + r * 2, start_x + c * cell_w
            if   val == 0:      color = curses.color_pair(0)
            elif val <= 4:      color = curses.color_pair(1)
            elif val <= 16:     color = curses.color_pair(2)
            elif val <= 64:     color = curses.color_pair(3)
            elif val <= 256:    color = curses.color_pair(4)
            elif val <= 1024:   color = curses.color_pair(5)
            else:               color = curses.color_pair(6)
            stdscr.addstr(y, x, txt, color | curses.A_BOLD)

    # ---------- ヘルプ ----------
    help_msg = "Use HJKL. R=Restart, Q=Quit"
    stdscr.addstr(start_y + SIZE * 2 + 1,
                  (w - len(help_msg)) // 2,
                  help_msg, curses.A_DIM)

    stdscr.refresh()

# ---------- Curses 初期化 ----------
def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)

# ---------- メインループ ----------
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

    board = new_game()
    score_p = score_c = 0
    turn = 'player'            # ここを必ず小文字で管理

    while True:
        draw_board(stdscr, board, score_p, score_c, turn)

        if won(board):
            stdscr.addstr(2, 0, "2048 で勝ちました！", curses.A_BLINK)
        elif lost(board):
            stdscr.addstr(2, 0, "Game Over!", curses.A_BLINK)

        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break

        if key == -1:
            time.sleep(0.05)
            continue

        # ==== プレイヤー入力 ====
        if turn == 'player':
            dir_ = None
            if key in (curses.KEY_LEFT, ord('h'), ord('H')):
                dir_ = 'left'
            elif key in (curses.KEY_RIGHT, ord('l'), ord('L')):
                dir_ = 'right'
            elif key in (curses.KEY_UP,   ord('k'), ord('K')):
                dir_ = 'up'
            elif key in (curses.KEY_DOWN, ord('j'), ord('J')):
                dir_ = 'down'
            elif key in (ord('q'), ord('Q')):
                break
            elif key in (ord('r'), ord('R')):
                board = new_game()
                score_p = score_c = 0
                turn = 'player'
                continue

            if dir_:
                board, mv, gained = move(board, dir_)
                if mv:
                    score_p += gained
                    add_random_tile(board)
                    turn = 'computer'   # 次はコンピュータ

        # ==== コンピュータ側 ====
        else:  # turn == 'computer'
            time.sleep(0.2)
            d = computer_choose_move(board)
            if d:
                board, mv, gained = move(board, d)
                if mv:
                    score_c += gained
                    add_random_tile(board)
            turn = 'player'           # 自動でプレイヤーに戻る

    # ==== 終了 ====
    stdscr.nodelay(False)
    stdscr.clear()
    final_msg = f"Final Score – Player: {score_p} | Computer: {score_c}"
    stdscr.addstr(2, 0, final_msg, curses.A_BOLD)
    stdscr.addstr(4, 0, "Thanks for playing! Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()

# ---------- エントリポイント ----------
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error:
        print("Curses error: 端末がカラーに対応していない可能性があります。")
        sys.exit(1)
