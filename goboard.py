import arcade
import numpy as np
from functools import lru_cache

BOARD_SIZE = 19

BOX_SIZE = 47
MARGIN = 1
TILE_SIZE = BOX_SIZE + MARGIN
TILE_MID = TILE_SIZE // 2


# Do the math to figure out our screen dimensions
SCREEN_SIZE = TILE_SIZE * (1 + BOARD_SIZE)
screen_title = "Go"


@lru_cache(None)
def calc_pos(pos):
    return TILE_SIZE * pos + MARGIN + TILE_SIZE // 2


@lru_cache(None)
def calc_board_pos(pos):
    return pos // TILE_SIZE - 1


def iterate_neighbour(pos):
    x, y = pos
    for x2, y2 in ((x, max(y - 1, 0)), (x, min(y + 1, 19)), (max(x - 1, 0), y), (min(x + 1, 19), y)):
        if -1 < x2 < 19 and -1 < y2 < 19:
            yield (x2, y2)

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title)

        self.shape_list = None
        self.board_shape_list = None
        self.mouse_coords = (0, 0)
        self.mouse_highlight = (0, 0)
        self.grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=bool)
        self.board_state = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_turn = 0
        arcade.set_background_color((210, 180, 110))
        self.recreate_grid()
        self.liberty_arr = np.zeros(self.board_state.shape, dtype=int)

    def recreate_grid(self):
        self.shape_list = arcade.ShapeElementList()
        vertical = [k for k in list(zip([[i*TILE_SIZE+TILE_SIZE, TILE_SIZE] for i in range(BOARD_SIZE+1)], [[i*TILE_SIZE+TILE_SIZE, TILE_SIZE*BOARD_SIZE] for i in range(BOARD_SIZE)])) for k in k]
        horizontal = [k for k in list(zip([[TILE_SIZE, i*TILE_SIZE+TILE_SIZE] for i in range(BOARD_SIZE+1)], [[TILE_SIZE*BOARD_SIZE, i*TILE_SIZE+TILE_SIZE] for i in range(BOARD_SIZE)])) for k in k]
        arcade.create_ellipse(center_x=3*TILE_SIZE+TILE_SIZE, center_y=3*TILE_SIZE+TILE_SIZE, height=4, width=4, color=arcade.color.BLACK)
        for x_point in [3, 9, 15]:
            for y_point in [3, 9, 15]:
                self.shape_list.append(arcade.create_ellipse(center_x=x_point*TILE_SIZE+TILE_SIZE, center_y=y_point*TILE_SIZE+TILE_SIZE, height=4, width=4, color=arcade.color.BLACK))

        self.shape_list.append(arcade.create_lines(point_list=vertical, color=(10, 10, 10), line_width=1))
        self.shape_list.append(arcade.create_lines(point_list=horizontal, color=(10, 10, 10), line_width=1))

    def recreate_board(self):
        self.board_shape_list = arcade.ShapeElementList()
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                if self.board_state[row, column]:
                    if self.board_state[row, column] == 1:
                        colors = [(40, 40, 40), (0, 0, 0)]
                    else:
                        colors = [(240, 240, 240), (200, 200, 200)]
                    curr_shape = arcade.create_ellipse_filled_with_colors(center_x=(column+1)*TILE_SIZE, center_y=(row+1)*TILE_SIZE, width=TILE_MID // 1.5,  height=TILE_MID // 1.5, inside_color=colors[0], outside_color=colors[1])
                    self.board_shape_list.append(curr_shape)

    def on_draw(self):
        arcade.start_render()
        self.shape_list.draw()

        if self.board_shape_list:
            self.board_shape_list.draw()
        if self.check_valid():
            turn = self.current_turn % 2 * 255
            arcade.draw_circle_filled(self.mouse_coords[0], self.mouse_coords[1], TILE_MID // 1.5, (turn, turn, turn, 150))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.check_valid():
            self.board_state[self.mouse_highlight[1], self.mouse_highlight[0]] = self.current_turn % 2 + 1
            self.current_turn += 1
        # self.make_move()

        for row_num, row in enumerate(self.board_state):
            for col_num, col in enumerate(row):
                if col:
                    self.liberty_arr[row_num, col_num] = self.liberties((row_num, col_num))
        for row_num, row in enumerate(self.board_state):
            for col_num, col in enumerate(row):
                if self.liberty_arr[row_num, col_num] == 0:
                    self.board_state[row_num, col_num] = 0

        self.recreate_board()

    def check_valid(self):
        return 19 > self.mouse_highlight[0] > -1 and 19 > self.mouse_highlight[1] > -1 and not self.board_state[self.mouse_highlight[1], self.mouse_highlight[0]]

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_coords = ((x + TILE_MID) // TILE_SIZE * TILE_SIZE, (y + TILE_MID) // TILE_SIZE * TILE_SIZE)
        self.mouse_highlight = (self.mouse_coords[0] // TILE_SIZE - 1, self.mouse_coords[1] // TILE_SIZE - 1)

    def liberties(self, pos):
        seen_pos = {}
        liberty_count = 0
        group_color = self.board_state[pos]
        pos_list = [pos]
        while pos_list:
            pos2 = pos_list.pop()
            if pos2 in seen_pos:
                continue
            seen_pos[pos2] = True
            for pos3 in iterate_neighbour(pos2):
                if pos3 in seen_pos:
                    continue
                if self.board_state[pos3] == 0:
                    liberty_count = liberty_count + 1
                    seen_pos[pos3] = True
                    continue
                if self.board_state[pos3] == group_color:
                    pos_list.append(pos3)
        return liberty_count


def main():
    MyGame(SCREEN_SIZE, SCREEN_SIZE, screen_title)
    arcade.run()


if __name__ == "__main__":
    main()
