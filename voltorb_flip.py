import tkinter as tk
from PIL import Image, ImageTk
import random
import os, sys

def get_asset_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class RCPanel(tk.Canvas):
    def __init__(self, master, image_path, row_sum=0, voltorb_count=0, **kwargs):
        img = Image.open(image_path)
        img = img.resize((75, 75), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        super().__init__(master, width=75, height=75, highlightthickness=0, **kwargs)
        self.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.row_sum_text = self.create_text(55, 20, text=str(row_sum), fill="black", font=("Arial", 20, "bold"))
        self.voltorb_count_text = self.create_text(55, 55, text=str(voltorb_count), fill="red", font=("Arial", 20, "bold"))

    def update_values(self, row_sum, voltorb_count):
        self.itemconfig(self.row_sum_text, text=str(row_sum))
        self.itemconfig(self.voltorb_count_text, text=str(voltorb_count))

class VoltorbFlipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voltorb Flip Desktop")
        self.root.configure(bg="#05A865")
        self.root.geometry("850x750")

        self.assets_path = get_asset_path("assets")
        self.images = {
            "unflipped": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "card_unflipped.png"))),
            "1": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "card_1.png"))),
            "2": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "card_2.png"))),
            "3": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "card_3.png"))),
            "V": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "card_voltorb.png"))),
            "exit": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "exit.png"))),
            "reset": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "reset.png"))),
            "infocard": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "infocard.png"))),
            "win_popup": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "Win.png")).resize((500, 300))),
            "loss_popup": ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "Loss.png")).resize((500, 300)))
        }

        self.root.overrideredirect(True) 

        self.header_frame = tk.Frame(root, bg="white", height=100, width=850)
        self.header_frame.place(x=0, y=0)

        self.titlebar_img = ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "titlebar.png")).resize((850, 40)))
        self.titlebar_label = tk.Label(self.header_frame, image=self.titlebar_img, bd=0, bg="#F5A9B8")
        self.titlebar_label.place(x=0, y=0, width=850, height=40)

        self.titlebar_label.bind("<Button-1>", self.start_move)
        self.titlebar_label.bind("<B1-Motion>", self.do_move)

        self.close_button = tk.Button(
            self.header_frame, text="✕", command=self.root.quit,
            font=("Arial", 12, "bold"), fg="white", bg="#f28597",
            activebackground="#e07286", bd=0, highlightthickness=0, relief="flat"
        )
        self.close_button.place(x=812, y=5, width=30, height=30)

        self.minimize_button = tk.Button(
            self.header_frame, text="━", command=self.minimize_window,
            font=("Arial", 12, "bold"), fg="white", bg="#f28597",
            activebackground="#e07286", bd=0, highlightthickness=0, relief="flat"
        )
        self.minimize_button.place(x=778, y=5, width=30, height=30)

        self.header_label = tk.Label(self.header_frame, text="Voltorb Flip", font=("Arial", 24, "bold"), bg="white", fg="black")
        self.header_label.place(x=425, y=70, anchor="center")


        self.shadow1 = tk.Frame(root, bg="#d0d0d0", height=2)
        self.shadow1.pack(fill="x")
        self.shadow2 = tk.Frame(root, bg="#a0a0a0", height=2)
        self.shadow2.pack(fill="x")

        self.infocard_label = tk.Label(self.root, image=self.images["infocard"], bg="#05A865", borderwidth=0)
        self.infocard_label.place(x=10, y=105)

        self.level_text = tk.Label(self.root, text="1", font=("Arial", 36, "bold"), fg="black", bg="#d9d9d9")
        self.level_text.place(x=160, y=273)

        self.total_coins_text = tk.Label(self.root, text="00000", font=("Arial", 20, "bold"), fg="black", bg="#d9d9d9")
        self.total_coins_text.place(x=75, y=165)

        self.coins_text = tk.Label(self.root, text="00000", font=("Arial", 20, "bold"), fg="black", bg="#d9d9d9")
        self.coins_text.place(x=75, y=240)

        self.exit_button = tk.Button(self.root, image=self.images["exit"], command=self.root.quit, bd=0, highlightthickness=0, relief="flat", bg="#05A865", activebackground="#05A865")
        self.exit_button.place(x=35, y=620)

        self.reset_button = tk.Button(self.root, image=self.images["reset"], command=self.restart_game, bd=0, highlightthickness=0, relief="flat", bg="#05A865", activebackground="#05A865")
        self.reset_button.place(x=10, y=398)

        self.container = tk.Frame(self.root, bg="#05A865")
        self.container.place(x=225, y=104)

        self.board_size = 5
        self.level = 1
        self.total_coins = 0

        self.board_frame = tk.Frame(self.container, bg="#05A865")
        self.board_frame.pack()

        self.rc_right = []
        self.rc_bottom = []

        self.start_game()

    def start_game(self):
        self.coins = 0
        self.first_guess = True
        self.revealed_specials = 0

        level_data = {
            1: [(3, 1, 6), (0, 3, 6), (5, 0, 6), (2, 2, 6), (4, 1, 6)],
            2: [(1, 3, 7), (6, 0, 7), (3, 2, 7), (0, 4, 7), (5, 1, 7)],
            3: [(2, 3, 8), (7, 0, 8), (4, 2, 8), (1, 4, 8), (6, 1, 8)],
            4: [(3, 3, 8), (0, 5, 8), (8, 0, 10), (5, 2, 10), (2, 4, 10)],
            5: [(7, 1, 10), (4, 3, 10), (1, 5, 10), (9, 0, 10), (6, 2, 10)],
            6: [(3, 4, 10), (0, 6, 10), (8, 1, 10), (5, 3, 10), (2, 5, 10)],
            7: [(7, 2, 10), (4, 4, 10), (1, 6, 13), (9, 1, 13), (6, 3, 10)],
            8: [(0, 7, 10), (8, 2, 10), (5, 4, 10), (2, 6, 10), (7, 3, 10)]
        }

        choice = random.choice(level_data[self.level])
        twos, threes, voltorbs = choice
        self.total_specials = twos + threes

        self.hidden_board = [[1 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.revealed = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
        positions = [(r, c) for r in range(self.board_size) for c in range(self.board_size)]
        random.shuffle(positions)

        for _ in range(voltorbs):
            r, c = positions.pop()
            self.hidden_board[r][c] = 'V'
        for _ in range(threes):
            r, c = positions.pop()
            self.hidden_board[r][c] = 3
        for _ in range(twos):
            r, c = positions.pop()
            self.hidden_board[r][c] = 2

        self.render_board()
        self.update_status()

    def render_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        self.rc_right.clear()
        self.rc_bottom.clear()

        for r in range(self.board_size):
            row = []
            for c in range(self.board_size):
                btn = tk.Button(self.board_frame, image=self.images["unflipped"], borderwidth=0)
                btn.grid(row=r, column=c, padx=10, pady=10)
                btn.config(command=lambda x=r, y=c: self.reveal_tile(x, y))
                row.append(btn)

            img_path = os.path.join(self.assets_path, f"rc{(r % 5) + 1}.png")
            row_sum = sum(val if isinstance(val, int) else 0 for val in self.hidden_board[r])
            voltorbs = sum(1 for val in self.hidden_board[r] if val == 'V')
            rc_panel = RCPanel(self.board_frame, img_path, row_sum, voltorbs)
            rc_panel.grid(row=r, column=self.board_size, padx=5)
            self.rc_right.append(rc_panel)
            self.buttons.append(row)

        for c in range(self.board_size):
            img_path = os.path.join(self.assets_path, f"rc{(c % 5) + 1}.png")
            total = 0
            bombs = 0
            for r in range(self.board_size):
                val = self.hidden_board[r][c]
                if isinstance(val, int):
                    total += val
                elif val == 'V':
                    bombs += 1
            rc_panel = RCPanel(self.board_frame, img_path, total, bombs)
            rc_panel.grid(row=self.board_size, column=c, pady=5)
            self.rc_bottom.append(rc_panel)

    def reveal_tile(self, r, c):
        if self.revealed[r][c]:
            return

        self.revealed[r][c] = True
        value = self.hidden_board[r][c]
        self.buttons[r][c].config(image=self.images[str(value)])

        if value == 'V':
            self.level = 1
            self.update_status()
            self.disable_all_buttons()
            self.reveal_all_cards()
            self.show_popup("loss")
            return

        elif isinstance(value, int):
            if self.first_guess:
                self.coins = value
                self.first_guess = False
            else:
                self.coins *= value

            if value in [2, 3]:
                self.revealed_specials += 1

            self.update_status()

            if self.revealed_specials == self.total_specials:
                self.total_coins += self.coins
                if self.level < 8:
                    self.level += 1
                self.update_status()
                self.disable_all_buttons()
                self.reveal_all_cards()
                self.show_popup("win") 

    def show_popup(self, result):
            popup = tk.Toplevel(self.root)
            popup.overrideredirect(True)
            popup.configure(bg="#e49ba8")  

            popup_width = 500
            popup_height = 340

            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            root_width = self.root.winfo_width()
            root_height = self.root.winfo_height()
            x = root_x + (root_width // 2) - (popup_width // 2)
            y = root_y + (root_height // 2) - (popup_height // 2)
            popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

            header_frame = tk.Frame(popup, bg="white", height=40, width=popup_width)
            header_frame.place(x=0, y=0)

            titlebar_img = ImageTk.PhotoImage(Image.open(os.path.join(self.assets_path, "titlebar.png")).resize((popup_width, 40)))
            titlebar_label = tk.Label(header_frame, image=titlebar_img, bd=0)
            titlebar_label.image = titlebar_img 
            titlebar_label.place(x=0, y=0, width=popup_width, height=40)

            def start_move(event):
                popup._x_offset = event.x
                popup._y_offset = event.y

            def do_move(event):
                x = event.x_root - popup._x_offset
                y = event.y_root - popup._y_offset
                popup.geometry(f'+{x}+{y}')

            titlebar_label.bind("<Button-1>", start_move)
            titlebar_label.bind("<B1-Motion>", do_move)

            close_button = tk.Button(
                header_frame, text="✕", command=popup.destroy,
                font=("Arial", 12, "bold"), fg="white", bg="#f28597",
                activebackground="#e07286", bd=0, highlightthickness=0, relief="flat"
            )
            close_button.place(x=popup_width - 38, y=5, width=30, height=30)

            img = self.images["win_popup"] if result == "win" else self.images["loss_popup"]
            label = tk.Label(popup, image=img)
            label.image = img  
            label.place(x=0, y=40, width=popup_width, height=popup_height - 40)

            popup.grab_set()
            popup.wait_window()

    def reveal_all_cards(self):
        for r in range(self.board_size):
            for c in range(self.board_size):
                if not self.revealed[r][c]:
                    value = self.hidden_board[r][c]
                    self.buttons[r][c].config(image=self.images[str(value)])
                    self.revealed[r][c] = True

    def disable_all_buttons(self):
        for row in self.buttons:
            for btn in row:
                btn.config(state=tk.DISABLED)

    def restart_game(self):
        self.start_game()

    def update_status(self, text=""):
        self.level_text.config(text=str(self.level))
        self.coins_text.config(text=f"{max(self.coins, 0):05d}")
        self.total_coins_text.config(text=f"{max(self.total_coins, 0):05d}")

    def start_move(self, event):
        self._x_offset = event.x
        self._y_offset = event.y

    def do_move(self, event):
        x = event.x_root - self._x_offset
        y = event.y_root - self._y_offset
        self.root.geometry(f'+{x}+{y}')

    def minimize_window(self):
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.after(10, lambda: self.root.overrideredirect(True))

if __name__ == "__main__":
    root = tk.Tk()
    app_width = 850
    app_height = 750
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (app_width // 2)
    y = (screen_height // 2) - (app_height // 2)
    root.geometry(f"{app_width}x{app_height}+{x}+{y}")

    app = VoltorbFlipApp(root)
    root.mainloop()
