import tkinter as tk
import random
from tkinter import messagebox
PLAYER_COLORS = ["red", "green", "yellow", "blue"]
YARD_POSITIONS = {
    "red": [(1, 1), (1, 2), (2, 1), (2, 2)], 
    "green": [(10, 1), (10, 2), (11, 1), (11, 2)], 
    "yellow": [(10, 10), (10, 11), (11, 10), (11, 11)], 
    "blue": [(1, 10), (1, 11), (2, 10), (2, 11)], 
}
START_POSITIONS = { 
    "red": 1,
    "green": 14,
    "yellow": 27,
    "blue": 40,
}
HOME_PATH_ENTRY = {
    "red": 51,
    "green": 12,
    "yellow": 25,
    "blue": 38,
}
SAFE_SPOTS = [1, 9, 14, 22, 27, 35, 40, 48] # Start positions are often safe

CELL_SIZE = 40
BOARD_OFFSET = 20
TOKEN_RADIUS = CELL_SIZE // 3
MAIN_PATH_COLOR = "white"
SAFE_SPOT_COLOR = "lightgray"
YARD_BG_COLOR = "lightgoldenrodyellow"
HOME_AREA_COLOR = "pink"

class LudoGame:
    def __init__(self, master):
        self.master = master
        master.title("Ludo Game")
        master.geometry("800x700") 

        self.canvas = tk.Canvas(master, width=650, height=650, bg="wheat")
        self.canvas.pack(side=tk.RIGHT, padx=200, pady=10)

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(side=tk.RIGHT, padx=10)

        self.current_player_label = tk.Label(self.control_frame, text="Current Player: Red", font=("Arial", 14))
        self.current_player_label.pack(pady=10)

        self.dice_label = tk.Label(self.control_frame, text="Dice: -", font=("Arial", 14))
        self.dice_label.pack(pady=10)

        self.roll_button = tk.Button(self.control_frame, text="Roll Dice", command=self.roll_dice_action, font=("Arial", 12))
        self.roll_button.pack(pady=10)
        self.roll_button.config(state=tk.NORMAL)

        self.status_label = tk.Label(self.control_frame, text="Roll the dice to start.", wraplength=120, font=("Arial", 10))
        self.status_label.pack(pady=10)

        self.players = {} 
        self.current_player_index = 0
        self.dice_value = 0
        self.movable_tokens = [] 

        self.define_board_layout()
        self.initialize_players_and_tokens()
        self.draw_board()
        self.draw_all_tokens()

        self.canvas.bind("<Button-1>", self.handle_canvas_click)
        self.game_over = False
        self.extra_turn = False


    def define_board_layout(self):
        self.grid_cells = {}

        for r in range(15):
            for c in range(15):
                x0 = BOARD_OFFSET + c * CELL_SIZE
                y0 = BOARD_OFFSET + r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                self.grid_cells[(r, c)] = (x0, y0, x1, y1)

        self.main_path_coords = [
            (6,0),(6,1),(6,2),(6,3),(6,4),(6,5), (5,6),(4,6),(3,6),(2,6),(1,6), 
            (0,6),(0,7),(0,8),
            (1,8),(2,8),(3,8),(4,8),(5,8), (6,9),(6,10),(6,11),(6,12),(6,13), 
            (6,14),(7,14),(8,14), 
            (8,13),(8,12),(8,11),(8,10),(8,9), (9,8),(10,8),(11,8),(12,8),(13,8), 
            (14,8),(14,7),(14,6),
            (13,6),(12,6),(11,6),(10,6),(9,6), (8,5),(8,4),(8,3),(8,2),(8,1), 
            (8,0),(7,0) 
        ]
        self.home_path_coords = {
            "red":    [(7,1),(7,2),(7,3),(7,4),(7,5),(7,6)], 
            "green":  [(1,7),(2,7),(3,7),(4,7),(5,7),(6,7)], 
            "yellow": [(7,13),(7,12),(7,11),(7,10),(7,9),(7,8)],
            "blue":   [(13,7),(12,7),(11,7),(10,7),(9,7),(8,7)],
        }

        self.yard_layout = {
            "red":    [(1,1),(1,2),(2,1),(2,2)],
            "green":  [(1,10),(1,11),(2,10),(2,11)], 
            "yellow": [(10,10),(10,11),(11,10),(11,11)],
            "blue":   [(10,1),(10,2),(11,1),(11,2)], 
        }
        self.center_home_coords = [(7,7)]


    def draw_board(self):
        self.canvas.delete("board") 

        for player_color, cells in self.yard_layout.items():
            for r_idx, c_idx in cells:
                coords = self.grid_cells[(r_idx, c_idx)]
                self.canvas.create_rectangle(coords, fill=YARD_BG_COLOR, outline="black", width=2, tags="board")
                inner_x0, inner_y0, inner_x1, inner_y1 = coords
                cx = (inner_x0 + inner_x1) / 2
                cy = (inner_y0 + inner_y1) / 2
                radius = CELL_SIZE * 0.3  # You can tweak this size

                self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                        fill=player_color, tags="board")
        for i, (r_idx, c_idx) in enumerate(self.main_path_coords):
            coords = self.grid_cells[(r_idx, c_idx)]
            fill_color = MAIN_PATH_COLOR
            if i in SAFE_SPOTS:
                fill_color = SAFE_SPOT_COLOR
            if i == START_POSITIONS["red"]: fill_color = "lightcoral"
            if i == START_POSITIONS["green"]: fill_color = "lightgreen"
            if i == START_POSITIONS["yellow"]: fill_color = "lightyellow"
            if i == START_POSITIONS["blue"]: fill_color = "lightblue"

            self.canvas.create_rectangle(coords, fill=fill_color, outline="black", width=2, tags="board")
        for player_color, path in self.home_path_coords.items():
            for i, (r_idx, c_idx) in enumerate(path):
                coords = self.grid_cells[(r_idx, c_idx)]
                fill_c = player_color if i < 5 else HOME_AREA_COLOR
                if i == 5: 
                     fill_c = player_color 
                self.canvas.create_rectangle(coords, fill=fill_c, outline="black", width=2, tags="board")

        r_coords = self.grid_cells[self.home_path_coords["red"][-1]] 
        g_coords = self.grid_cells[self.home_path_coords["green"][-1]]
        y_coords = self.grid_cells[self.home_path_coords["yellow"][-1]]
        b_coords = self.grid_cells[self.home_path_coords["blue"][-1]]

        center_x = BOARD_OFFSET + 7.5 * CELL_SIZE
        center_y = BOARD_OFFSET + 7.5 * CELL_SIZE
        #triangle shape 
        self.canvas.create_polygon(
            r_coords[0]+CELL_SIZE, r_coords[1]+CELL_SIZE/2, 
            center_x, center_y,
            g_coords[0]+CELL_SIZE/2, g_coords[1]+CELL_SIZE, 
            fill="red", outline="black", tags="board"
        )
        self.canvas.create_polygon(
            g_coords[0]+CELL_SIZE/2, g_coords[1]+CELL_SIZE,
            center_x, center_y,
            y_coords[0], y_coords[1]+CELL_SIZE/2, 
            fill="green", outline="black", tags="board"
        )
        self.canvas.create_polygon(
            y_coords[0], y_coords[1]+CELL_SIZE/2,
            center_x, center_y,
            b_coords[0]+CELL_SIZE/2, b_coords[1], 
            fill="yellow", outline="black", tags="board"
        )
        self.canvas.create_polygon(
            b_coords[0]+CELL_SIZE/2, b_coords[1],
            center_x, center_y,
            r_coords[0]+CELL_SIZE, r_coords[1]+CELL_SIZE/2,
            fill="blue", outline="black", tags="board"
        )


    def initialize_players_and_tokens(self):
        self.players = {}
        for i, color in enumerate(PLAYER_COLORS):
            self.players[color] = {"tokens": [], "home_count": 0}
            yard_cells = self.yard_layout[color]
            for token_idx in range(4):
                token_info = {
                    "id": None, 
                    "color": color,
                    "state": "yard", 
                    "logical_pos": token_idx, 
                    "path_pos": -1, 
                    "token_idx_in_player": token_idx 
                }
                self.players[color]["tokens"].append(token_info)
        self.current_player_index = 0 
        self.update_player_label()

    def get_token_canvas_coords(self, token_info):
        color = token_info["color"]
        state = token_info["state"]
        logical_pos = token_info["logical_pos"] 
        path_pos = token_info["path_pos"]

        grid_r, grid_c = -1, -1

        if state == "yard":
            grid_r, grid_c = self.yard_layout[color][logical_pos]
        elif state == "on_board":
            grid_r, grid_c = self.main_path_coords[path_pos]
        elif state == "home_path":
            grid_r, grid_c = self.home_path_coords[color][path_pos]
        elif state == "home": 
            grid_r, grid_c = self.home_path_coords[color][-1]  

        if grid_r != -1 and grid_c != -1:
            cell_coords = self.grid_cells[(grid_r, grid_c)]
            center_x = (cell_coords[0] + cell_coords[2]) / 2
            center_y = (cell_coords[1] + cell_coords[3]) / 2
            offset_idx = token_info["token_idx_in_player"] % 2 
            offset_val = (token_info["token_idx_in_player"] // 2 - 0.5) * (TOKEN_RADIUS*0.8)
            if state == "on_board" or state == "home_path": 
                pass 
            return (center_x - TOKEN_RADIUS + (offset_val if offset_idx ==0 else 0) ,
                    center_y - TOKEN_RADIUS + (offset_val if offset_idx ==1 else 0),
                    center_x + TOKEN_RADIUS + (offset_val if offset_idx ==0 else 0),
                    center_y + TOKEN_RADIUS + (offset_val if offset_idx ==1 else 0))
        return None


    def draw_all_tokens(self):
        self.canvas.delete("tokens") 
        for color in PLAYER_COLORS:
            for token_info in self.players[color]["tokens"]:
                coords = self.get_token_canvas_coords(token_info)
                if coords:
                    token_tag = f"token_{color}_{token_info['token_idx_in_player']}"
                    token_id = self.canvas.create_oval(coords, fill=color, outline="black", width=2, tags=("tokens", token_tag))
                    token_info["id"] = token_id
                    token_info["canvas_tag"] = token_tag


    def update_player_label(self):
        self.current_player_label.config(text=f"Current Player: {PLAYER_COLORS[self.current_player_index].capitalize()}")

    def roll_dice_action(self):
        if self.game_over: return

        self.dice_value = random.randint(1, 6)
        self.dice_label.config(text=f"Dice: {self.dice_value}")
        self.roll_button.config(state=tk.DISABLED) 
        self.extra_turn = False 

        current_color = PLAYER_COLORS[self.current_player_index]
        self.movable_tokens = self.get_movable_tokens(current_color, self.dice_value)

        if not self.movable_tokens:
            self.status_label.config(text=f"No valid moves for {current_color.capitalize()}.")
            if self.dice_value == 6: 
                self.status_label.config(text=f"{current_color.capitalize()} rolled a 6! Roll again.")
                self.roll_button.config(state=tk.NORMAL)
            else:
                self.master.after(1000, self.next_turn) 
        else:
            self.status_label.config(text=f"{current_color.capitalize()}, select a token to move {self.dice_value} steps.")
            self.highlight_movable_tokens(True)


    def get_movable_tokens(self, color, dice_roll):
        movable = []
        player_tokens = self.players[color]["tokens"]
        for i, token in enumerate(player_tokens):
            if token["state"] == "home":
                continue

            if token["state"] == "yard":
                if dice_roll == 6:
                    movable.append(i) 
            elif token["state"] == "on_board":
                movable.append(i)
            elif token["state"] == "home_path":
                if token["path_pos"] + dice_roll < len(self.home_path_coords[color]):
                     movable.append(i)
        return movable

    def highlight_movable_tokens(self, highlight_on):
        for token_idx_in_player in self.movable_tokens:
            current_color = PLAYER_COLORS[self.current_player_index]
            token_info = self.players[current_color]["tokens"][token_idx_in_player]
            if token_info["id"]:
                self.canvas.itemconfig(token_info["id"], outline="gold" if highlight_on else "black", width=3 if highlight_on else 2)

    def handle_canvas_click(self, event):
        if self.game_over or not self.movable_tokens:
            return

        clicked_item = self.canvas.find_closest(event.x, event.y)
        if not clicked_item: return

        tags = self.canvas.gettags(clicked_item[0])

        for tag in tags:
            if tag.startswith("token_"):
                try:
                    _, color_str, token_idx_str = tag.split("_")
                    token_idx_in_player = int(token_idx_str)

                    current_player_color_str = PLAYER_COLORS[self.current_player_index]
                    if color_str == current_player_color_str and token_idx_in_player in self.movable_tokens:
                        self.highlight_movable_tokens(False) 
                        self.move_token(current_player_color_str, token_idx_in_player, self.dice_value)
                        self.movable_tokens = [] 
                        return 
                except ValueError:
                    continue 

    def move_token(self, color, token_idx_in_player, steps):
        token = self.players[color]["tokens"][token_idx_in_player]
        initial_state = token["state"]

        if token["state"] == "yard":
            if steps == 6:
                token["state"] = "on_board"
                token["path_pos"] = START_POSITIONS[color]
                self.status_label.config(text=f"{color.capitalize()} token out of yard!")
                self.roll_button.config(state=tk.NORMAL)
                self.extra_turn = True 
            else: 
                return
        elif token["state"] == "on_board":
            current_main_path_pos = token["path_pos"]
            home_entry_for_player = HOME_PATH_ENTRY[color]
            player_start_pos = START_POSITIONS[color]

            new_main_path_pos = (current_main_path_pos + steps) % len(self.main_path_coords)
            moved_past_home_entry = False
            if player_start_pos > home_entry_for_player: # e.g. Red: start 0, home_entry 50
                if current_main_path_pos <= home_entry_for_player and (current_main_path_pos + steps) > home_entry_for_player:
                     moved_past_home_entry = True
                elif current_main_path_pos > home_entry_for_player and (current_main_path_pos + steps) % len(self.main_path_coords) > home_entry_for_player and (current_main_path_pos + steps) // len(self.main_path_coords) > 0:
                     moved_past_home_entry = True

            else: 
                if current_main_path_pos <= home_entry_for_player and (current_main_path_pos + steps) > home_entry_for_player:
                    moved_past_home_entry = True


            if moved_past_home_entry:
                remaining_steps = steps - ( (home_entry_for_player - current_main_path_pos + len(self.main_path_coords)) % len(self.main_path_coords) + 1 )
                if remaining_steps < len(self.home_path_coords[color]):
                    token["state"] = "home_path"
                    token["path_pos"] = remaining_steps
                    if remaining_steps == len(self.home_path_coords[color]) - 1: # Reached exact home
                        token["state"] = "home"
                        self.players[color]["home_count"] += 1
                        self.status_label.config(text=f"{color.capitalize()} token reached home!")
                        self.extra_turn = True
                        self.check_win(color)
                else:
                    self.status_label.config(text=f"Move overshoots home for {color}.")
                    if not self.extra_turn and self.dice_value != 6:
                         self.master.after(500, self.next_turn)
                    else:
                         self.roll_button.config(state=tk.NORMAL)
                    return


            else: 
                token["path_pos"] = new_main_path_pos
                self.check_capture(color, new_main_path_pos)

        elif token["state"] == "home_path":
            new_home_path_pos = token["path_pos"] + steps
            if new_home_path_pos < len(self.home_path_coords[color]):
                token["path_pos"] = new_home_path_pos
                if new_home_path_pos == len(self.home_path_coords[color]) - 1: 
                    token["state"] = "home"
                    self.players[color]["home_count"] += 1
                    self.status_label.config(text=f"{color.capitalize()} token reached home!")
                    self.extra_turn = True
                    self.check_win(color)
            
        self.draw_all_tokens() 
        if self.game_over: return

        if self.dice_value == 6: 
            self.extra_turn = True

        if self.extra_turn:
            self.status_label.config(text=f"{color.capitalize()} gets an extra turn!")
            self.roll_button.config(state=tk.NORMAL)
            self.dice_label.config(text="Dice: -") 
        else:
            self.master.after(500, self.next_turn) 


    def check_capture(self, current_player_color, landing_pos_on_main_path):
        if landing_pos_on_main_path in SAFE_SPOTS:
            return

        for opp_color in PLAYER_COLORS:
            if opp_color == current_player_color:
                continue
            for opp_token in self.players[opp_color]["tokens"]:
                if opp_token["state"] == "on_board" and opp_token["path_pos"] == landing_pos_on_main_path:
                   
                    opp_token["state"] = "yard"
                    opp_token["path_pos"] = -1
                    opp_token["logical_pos"] = opp_token["token_idx_in_player"]
                    self.status_label.config(text=f"{current_player_color.capitalize()} captured {opp_color.capitalize()}'s token!")
                    self.extra_turn = True
                    return 

    def next_turn(self):
        if self.game_over: return

        self.current_player_index = (self.current_player_index + 1) % len(PLAYER_COLORS)
        self.update_player_label()
        self.dice_label.config(text="Dice: -")
        self.status_label.config(text=f"{PLAYER_COLORS[self.current_player_index].capitalize()}'s turn. Roll the dice.")
        self.roll_button.config(state=tk.NORMAL)
        self.extra_turn = False 

    def check_win(self, color):
        if self.players[color]["home_count"] == 4:
            self.game_over = True
            self.status_label.config(text=f"Player {color.capitalize()} Wins!")
            self.roll_button.config(state=tk.DISABLED)
            messagebox.showinfo("Game Over", f"Player {color.capitalize()} is the winner!")
            return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    game = LudoGame(root)
    root.mainloop()
