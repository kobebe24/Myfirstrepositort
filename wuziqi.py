import tkinter as tk
from tkinter import messagebox

# 棋盘参数配置
BOARD_SIZE = 15  # 棋盘尺寸（15x15 交点）
CELL_GAP = 40    # 相邻交点间距（像素）
WINDOW_WIDTH = (BOARD_SIZE - 1) * CELL_GAP  # 窗口宽度，基于交点计算
WINDOW_HEIGHT = (BOARD_SIZE - 1) * CELL_GAP # 窗口高度，基于交点计算

# 全局变量：棋盘状态（None=空，'black'=黑棋，'white'=白棋）
board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
is_black_turn = True  # 黑棋先行标记
game_over = False     # 游戏结束标记


def draw_chessboard(canvas):
    """绘制棋盘线（连接交点）"""
    for i in range(BOARD_SIZE):
        # 画竖线：x 坐标固定为 i*CELL_GAP，贯穿上下
        canvas.create_line(i * CELL_GAP, 0, i * CELL_GAP, WINDOW_HEIGHT, fill='black')
        # 画横线：y 坐标固定为 i*CELL_GAP，贯穿左右
        canvas.create_line(0, i * CELL_GAP, WINDOW_WIDTH, i * CELL_GAP, fill='black')


def get_chess_point(event):
    """将鼠标点击坐标转换为棋盘交点坐标（行列）"""
    x = round(event.x / CELL_GAP)  # 换算为交点列索引
    y = round(event.y / CELL_GAP)  # 换算为交点行索引
    # 边界保护：防止点击超出棋盘范围
    x = max(0, min(x, BOARD_SIZE - 1))
    y = max(0, min(y, BOARD_SIZE - 1))
    return x, y  # 返回 (列索引, 行索引)


def draw_chess_piece(canvas, x, y, color):
    """在交点(x,y)处画棋子（椭圆，严格居中）"""
    # 棋子范围：以交点为中心，留出间隙
    x1 = x * CELL_GAP - 15
    y1 = y * CELL_GAP - 15
    x2 = x * CELL_GAP + 15
    y2 = y * CELL_GAP + 15
    canvas.create_oval(x1, y1, x2, y2, fill=color)


def check_five_in_a_row(x, y, color):
    """检查五子连珠（横向、纵向、对角线）"""
    # 1. 横向检查（同一行）
    count = 0
    for col in range(BOARD_SIZE):
        if board[y][col] == color:
            count += 1
            if count == 5:
                return True
        else:
            count = 0

    # 2. 纵向检查（同一列）
    count = 0
    for row in range(BOARD_SIZE):
        if board[row][x] == color:
            count += 1
            if count == 5:
                return True
        else:
            count = 0

    # 3. 主对角线（左上→右下）检查
    count = 0
    start_col = x - min(x, y)
    start_row = y - min(x, y)
    for i in range(min(BOARD_SIZE - start_col, BOARD_SIZE - start_row)):
        if board[start_row + i][start_col + i] == color:
            count += 1
            if count == 5:
                return True
        else:
            count = 0

    # 4. 副对角线（右上→左下）检查
    count = 0
    start_col = x + y
    start_row = 0 if start_col < BOARD_SIZE else start_col - BOARD_SIZE + 1
    start_col = start_col if start_col < BOARD_SIZE else BOARD_SIZE - 1
    for i in range(min(BOARD_SIZE - start_row, start_col + 1)):
        if board[start_row + i][start_col - i] == color:
            count += 1
            if count == 5:
                return True
        else:
            count = 0

    return False  # 未五子连珠


def place_black_chess(event, canvas):
    """左键落黑棋逻辑"""
    global is_black_turn, game_over
    if game_over or not is_black_turn:
        return
    x, y = get_chess_point(event)  # 获取交点坐标
    if board[y][x] is None:  # 空交点才能落子
        draw_chess_piece(canvas, x, y, 'black')
        board[y][x] = 'black'
        if check_five_in_a_row(x, y, 'black'):
            messagebox.showinfo("游戏结束", "黑方获胜！")
            game_over = True
            return
        is_black_turn = False  # 切换白棋回合


def place_white_chess(event, canvas):
    """右键落白棋逻辑"""
    global is_black_turn, game_over
    if game_over or is_black_turn:
        return
    x, y = get_chess_point(event)  # 获取交点坐标
    if board[y][x] is None:  # 空交点才能落子
        draw_chess_piece(canvas, x, y, 'white')
        board[y][x] = 'white'
        if check_five_in_a_row(x, y, 'white'):
            messagebox.showinfo("游戏结束", "白方获胜！")
            game_over = True
            return
        is_black_turn = True  # 切换黑棋回合


def main():
    """初始化游戏窗口"""
    root = tk.Tk()
    root.title("五子棋（线交点落子版）")
    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()
    draw_chessboard(canvas)  # 绘制棋盘线

    # 绑定鼠标事件：左键黑棋，右键白棋
    canvas.bind("<Button-1>", lambda event: place_black_chess(event, canvas))
    canvas.bind("<Button-3>", lambda event: place_white_chess(event, canvas))

    root.mainloop()  # 启动 GUI 循环


if __name__ == "__main__":
    main()