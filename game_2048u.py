import random
import os
import sys
import copy  # ← Undo用に deepcopy を使う

# --- OS別リアルタイム入力用 ---
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

def print_board(board):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("2048 Game (Use H/J/K/L to move, U to undo, Q to quit)\n")  # ← 表示文も更新
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
    for i in range(SIZE - 1):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            row[i + 1] = 0
    return row

def move_left(board):
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

def move_right(board):
    reversed_board = [row[::-1] for row in board]
    new_board, moved = move_left(reversed_board)
    return [row[::-1] for row in new_board], moved

def transpose(board):
    return [list(row) for row in zip(*board)]

def move_up(board):
    transposed = transpose(board)
    new_board, moved = move_left(transposed)
    return transpose(new_board), moved

def move_down(board):
    transposed = transpose(board)
    new_board, moved = move_right(transposed)
    return transpose(new_board), moved

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

# --- Enter不要のキー取得 ---
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
    prev_board = None  # ← Undo用の1つ前の盤面

    while True:
        print_board(board)
        key = get_key()

        if key == 'q':
            print("Bye!")
            break
        elif key == 'u':
            if prev_board:
                board = prev_board
                prev_board = None  # 連続Undoを防ぐ
            continue  # 再描画
        elif key in ('h', 'j', 'k', 'l'):
            # 移動前に盤面を保存（deepcopyを使う）
            prev_board = copy.deepcopy(board)

            if key == 'k':
                board, moved = move_up(board)
            elif key == 'j':
                board, moved = move_down(board)
            elif key == 'h':
                board, moved = move_left(board)
            elif key == 'l':
                board, moved = move_right(board)

            if moved:
                add_random_tile(board)
            else:
                prev_board = None  # 動いていなければUndo不要
        else:
            continue  # 無効なキーは無視

        if not can_move(board):
            print_board(board)
            print("Game Over!")
            break

if __name__ == "__main__":
    main()

