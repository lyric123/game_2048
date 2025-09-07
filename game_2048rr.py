import random
import os
import sys
import copy

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios

SIZE = 4

def init_board():
    board = [[0] * SIZE for _ in range(SIZE)]
    add_random_tile(board)
    add_random_tile(board)
    return board

def print_board(board, score):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"2048 Game (Use H/J/K/L to move, U to undo, R to redo, Q to quit)")
    print(f"Score: {score}\n")
    for row in board:
        print("+------+------+------+------+")
        for val in row:
            print(f"|{val:^6}" if val != 0 else "|      ", end='')
        print("|")
    print("+------+------+------+------+")

def add_random_tile(board):
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if not empty:
        return
    r, c = random.choice(empty)
    board[r][c] = 4 if random.random() < 0.1 else 2

def compress(row):
    new_row = [val for val in row if val != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row

def merge(row):
    score = 0
    for i in range(SIZE - 1):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            score += row[i]
            row[i + 1] = 0
    return row, score

def move_left(board):
    moved = False
    total_score = 0
    new_board = []
    for row in board:
        compressed = compress(row)
        merged, score = merge(compressed)
        final = compress(merged)
        if final != row:
            moved = True
        new_board.append(final)
        total_score += score
    return new_board, moved, total_score

def move_right(board):
    reversed_board = [row[::-1] for row in board]
    new_board, moved, score = move_left(reversed_board)
    return [row[::-1] for row in new_board], moved, score

def transpose(board):
    return [list(row) for row in zip(*board)]

def move_up(board):
    transposed = transpose(board)
    new_board, moved, score = move_left(transposed)
    return transpose(new_board), moved, score

def move_down(board):
    transposed = transpose(board)
    new_board, moved, score = move_right(transposed)
    return transpose(new_board), moved, score

def can_move(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return True
            if c < SIZE - 1 and board[r][c] == board[r][c + 1]:
                return True
            if r < SIZE - 1 and board[r][c] == board[r + 1][c]:
                return True
    return False

def get_key():
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8').lower()
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()

def main():
    board = init_board()
    score = 0

    undo_stack = []
    redo_stack = []
    game_over = False
    is_redoing = False  # ★追加：Redo中フラグ

    while True:
        print_board(board, score)

        if game_over:
            print("Game Over! (Press 'u' to undo, or 'q' to quit)")
        else:
            print("(Use H/J/K/L to move, U to undo, R to redo, Q to quit)")

        key = get_key()

        if key == 'q':
            print("Bye!")
            break

        elif key == 'u':
            if undo_stack:
                redo_stack.append((copy.deepcopy(board), score))
                board, score = undo_stack.pop()
                game_over = not can_move(board)
            is_redoing = False  # ★Undo後はRedo中じゃない
            continue

        elif key == 'r':
            if redo_stack:
                undo_stack.append((copy.deepcopy(board), score))
                board, score = redo_stack.pop()
                is_redoing = True  # ★Redo中
            continue

        if game_over:
            continue

        if key in ('h', 'j', 'k', 'l'):
            direction_map = {
                'h': move_left,
                'l': move_right,
                'k': move_up,
                'j': move_down
            }
            move_func = direction_map[key]

            new_board, moved, gained = move_func(board)
            if moved:
                undo_stack.append((copy.deepcopy(board), score))
                board = new_board
                score += gained
                add_random_tile(board)

                # ★Redo中でないときだけ redo_stack をクリア
                if not is_redoing:
                    redo_stack.clear()
                is_redoing = False  # ★通常の移動後はフラグリセット
            else:
                continue

        if not can_move(board):
            game_over = True

if __name__ == "__main__":
    main()
