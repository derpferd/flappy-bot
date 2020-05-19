from typing import NamedTuple
from CYLGame import GridGame, MessagePanel, StatusPanel, MapPanel, PanelBorder, PanelPadding, GameLanguage
from CYLGame.Player import DefaultGridPlayer
from CYLGame.Game import ConstMapping


class Pipe(NamedTuple):
    x: int
    y: int

    def shift(self):
        return Pipe(self.x-1, self.y)


class FlappyBird(GridGame):
    MAP_WIDTH = 40
    MAP_HEIGHT = 35
    SCREEN_WIDTH = 40
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "Flappy Robot"

    EMPTY = ' '
    PLAYER = '@'

    PIPE = chr(11*16 + 3)#'|'
    PIPE_TOP_LEFT = chr(13*16 + 4)
    PIPE_TOP_RIGHT = chr(11*16 + 14)
    PIPE_BUTTOM_LEFT = chr(13*16 + 5)
    PIPE_BUTTOM_RIGHT = chr(11*16 + 8)

    MAP_BOTTOM = chr(12*16 + 4)

    PLAYER_X = 2
    MAX_DOWNWARD_SPEED = 4

    CHAR_SET = "resources/terminal16x16_gs_ro.png"

    PASSING_SOUNDS = ['Swish!', 'Whoosh!', 'Swoosh!', 'Chirp', 'Tweet']

    def __init__(self, random):
        self.random = random
        self.running = True

        self.player_y = self.MAP_HEIGHT // 2
        self.player_v = 0
        self.x = 0
        self.pipes_passed = 0
        self.pipes = []

        self.msg_panel = MessagePanel(self.MSG_START, self.MAP_HEIGHT+1, self.SCREEN_WIDTH - self.MSG_START, 5, padding=PanelPadding.create(top=1, right=1, bottom=1))
        self.status_panel = StatusPanel(0, self.MAP_HEIGHT+1, self.MSG_START, 5, padding=PanelPadding.create(top=1, left=1, bottom=1))
        self.panels = [self.status_panel, self.msg_panel]
        self.msg_panel.add("Welcome to")
        self.msg_panel.add("   " + self.GAME_TITLE + "!!!")
        self.msg_panel.add("Don't hit the pipes")

    def init_board(self):
        self.map = MapPanel(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT, self.EMPTY, border=PanelBorder.create(bottom=self.MAP_BOTTOM))
        self.panels.append(self.map)

    def create_new_player(self, prog):
        self.player = DefaultGridPlayer(prog, self.get_move_consts())
        self.map[(self.PLAYER_X, self.player_y)] = self.PLAYER

        self.update_vars_for_player()
        return self.player

    def start_game(self):
        pass

    def do_turn(self):
        # print("doing turn")
        self.handle_key(self.player.move)
        self.move_pipes()
        self.draw_pipe_if_needed()
        self.update_vars_for_player()

    def handle_key(self, key):
        if key == 'Q':
            self.running = False
            return

        self.map[(self.PLAYER_X, self.player_y)] = self.EMPTY
        if key == 'w' or key == ' ':
            self.player_y -= 2
            self.player_v = -1
        else:
            self.player_y += self.player_v
            self.player_v += 1 if self.player_v < self.MAX_DOWNWARD_SPEED else 0
        self.x += 1
        self.map.shift_all((-1, 0))
        new_pos = (self.PLAYER_X, self.player_y)
        if not self.map.in_bounds(new_pos) or self.map[new_pos] == self.PIPE:
            self.running = False
            # self.msg_panel.add("You flu into a pipe!")
        else:
            self.map[(self.PLAYER_X, self.player_y)] = self.PLAYER

    def move_pipes(self):
        num_pipes_before = len(self.pipes)
        self.pipes = [pipe.shift() for pipe in self.pipes if pipe.x > 1]
        num_pipes_after = len(self.pipes)
        self.pipes_passed += num_pipes_before - num_pipes_after

    def draw_pipe_if_needed(self):
        if not self.pipes:
            self.pipes.append(self.create_pipe())
            self.draw_pipe(self.pipes[-1])
        else:
            last_pipe = self.pipes[-1]
            dist_from_last_pipe = self.MAP_WIDTH - last_pipe.x
            print(dist_from_last_pipe)
            if dist_from_last_pipe > (20 - (self.x//100)):
                self.pipes.append(self.create_pipe())
                self.draw_pipe(self.pipes[-1])
        return

        # print(f"space: {(20 - (self.x//25))}")
        # if self.x % (20 - (self.x//100)) == 0:
        #     position = self.random.choice(range(10, self.MAP_HEIGHT-10))
        #     for i in range(self.MAP_HEIGHT):
        #         if abs(position-i) > 3:
        #             self.map[(self.MAP_WIDTH - 1, i)] = self.PIPE
        #             self.map[(self.MAP_WIDTH - 2, i)] = self.PIPE

    def draw_pipe(self, pipe):
        print(f'Drawing {pipe}')
        for i in range(self.MAP_HEIGHT):
            if abs(pipe.y-i) > 3:
                if pipe.y - i == 4:
                    self.map[(pipe.x, i)] = self.PIPE_TOP_LEFT
                    self.map[(pipe.x+1, i)] = self.PIPE_TOP_RIGHT
                elif pipe.y - i == -4:
                    self.map[(pipe.x, i)] = self.PIPE_BUTTOM_LEFT
                    self.map[(pipe.x+1, i)] = self.PIPE_BUTTOM_RIGHT
                else:
                    self.map[(pipe.x, i)] = self.PIPE
                    self.map[(pipe.x+1, i)] = self.PIPE

    def create_pipe(self):
        print('Creating pipe')
        y = self.random.choice(range(10, self.MAP_HEIGHT-10))
        return Pipe(self.MAP_WIDTH - 2, y)

    def update_vars_for_player(self):
        bot_vars = {
            "y": self.player_y,
            "next_pipe_y": self.pipes[0].y if self.pipes else -1,
            "dist_to_next_pipe": self.pipes[0].x - self.PLAYER_X if self.pipes else 9999,
        }
        self.player.bot_vars = bot_vars

    def is_running(self):
        return self.running

    def draw_screen(self, frame_buffer):
        if not self.running:
            self.msg_panel.add("Game Over.")
            if self.pipes_passed == 0:
                self.msg_panel.add("Better luck")
                self.msg_panel.add("      next time :(")
            else:
                self.msg_panel.add("     Good job!")

        self.status_panel["Meters Flown"] = self.x
        self.status_panel["Pipes Passed"] = self.pipes_passed
        self.status_panel["Score"] = self.get_score()

        for panel in self.panels:
            panel.redraw(frame_buffer)

    def get_score(self):
        return self.x + (self.pipes_passed * 50)

    @staticmethod
    def get_intro():
        return open("resources/intro.md", "r").read()

    @staticmethod
    def default_prog_for_bot(language):
        if language == GameLanguage.LITTLEPY:
            return open("resources/flappy_bot.lp", "r").read()

    @staticmethod
    def get_move_consts():
        return ConstMapping({"flap": ord(" "), "up": ord("w"), "down": ord("s"), "glide": ord("d")})


if __name__ == '__main__':
    from CYLGame import run
    run(FlappyBird)
