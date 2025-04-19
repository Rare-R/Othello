import tkinter as tk
from tkinter import messagebox
import arabic_reshaper
from bidi.algorithm import get_display

# تنظیمات فونت
FONT_NAME = "Vazir"
FONT_SIZE = 12

class Othello:
    def __init__(self, master):
        self.master = master
        master.title("اتللو")
        self.board_size = 8
        self.cell_size = 60
        self.sequence = ''
        self.sequence2 = '' # ذخیره ی دنباله ی معادل به دلیل تقارن صفحه
        self.pieces = {}  # برای نگهداری اشیاء گرافیکی مهره‌ها
        self.hint_markers = {}  # برای نگهداری اشیاء گرافیکی نشانگرهای راهنما
        self.history = []  # برای نگهداری وضعیت‌های قبلی بازی برای قابلیت Undo/Redo
        self.current_player = "black"  # شروع بازی با مهره سیاه (پیش فرض)
        self.player_color = tk.StringVar(value="سیاه")  # رنگ انتخابی کاربر (پیش فرض سیاه)
        self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.reset_board_state()  # تنظیم وضعیت اولیه تخته
        self.NumOfMoves = 0
        self.show_hints = tk.BooleanVar()
        self.show_hints.set(False) # پیش فرض راهنما خاموش است

        # تنظیم فونت پیش‌فرض
        self.default_font = (FONT_NAME, FONT_SIZE)

        # تابع برای اصلاح نمایش متن فارسی
        def format_persian(text):
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)

        # فریم اصلی
        main_frame = tk.Frame(master)
        main_frame.pack(padx=10, pady=10)

        # فریم برای حروف ستون‌ها در بالا
        top_labels_frame = tk.Frame(main_frame)
        top_labels_frame.grid(row=0, column=1, columnspan=self.board_size, sticky="ew")
        for j in range(self.board_size):
            col_label = tk.Label(top_labels_frame, text=chr(ord('A') + j), width=3, anchor="center", font=self.default_font)
            col_label.pack(side="left", padx=self.cell_size // 3)  # تنظیم padx برای فاصله

        # فریم برای تخته و شماره ردیف‌ها
        board_frame = tk.Frame(main_frame)
        board_frame.grid(row=1, column=1)

        # نمایش شماره ردیف‌ها در سمت چپ
        for i in range(self.board_size):
            row_label = tk.Label(board_frame, text=str(i + 1), height=1, font=self.default_font)
            row_label.grid(row=i, column=0, sticky="ew")

        # Canvas برای تخته بازی
        self.canvas = tk.Canvas(board_frame, width=self.board_size * self.cell_size, height=self.board_size * self.cell_size, bd=2, relief=tk.SOLID)
        self.canvas.grid(row=0, column=1, rowspan=self.board_size)
        self.canvas.bind("<Button-1>", self.on_click)

        # نمایش شماره ردیف‌ها در سمت راست
        for i in range(self.board_size):
            row_label_right = tk.Label(board_frame, text=str(i + 1), height=1, font=self.default_font)
            row_label_right.grid(row=i, column=2, sticky="ew")

        # فریم برای دکمه‌ها و انتخاب رنگ
        controls_frame = tk.Frame(main_frame)
        controls_frame.grid(row=1, column=0, sticky="ns", padx=10)

        tk.Label(controls_frame, text=format_persian("رنگ شما:"), pady=5, font=self.default_font).pack()
        black_radio = tk.Radiobutton(controls_frame, text=format_persian("سیاه"), variable=self.player_color, value="سیاه", font=self.default_font)
        white_radio = tk.Radiobutton(controls_frame, text=format_persian("سفید"), variable=self.player_color, value="سفید", font=self.default_font)
        black_radio.pack()
        white_radio.pack()

        self.undo_button = tk.Button(controls_frame, text=format_persian("عقب"), command=self.undo_move, width=10, font=self.default_font)
        self.undo_button.pack(pady=5)

        self.redo_button = tk.Button(controls_frame, text=format_persian("جلو"), command=self.redo_move, state=tk.DISABLED, width=10, font=self.default_font)
        self.redo_button.pack(pady=5)

        self.hint_check = tk.Checkbutton(controls_frame, text=format_persian("راهنما"), command=self.check_hint, variable=self.show_hints, font=self.default_font)
        self.hint_check.pack(pady=5)

        self.save_log_button = tk.Button(controls_frame, text=format_persian("ذخیره حرکات"), command=self.save_game_log, width=10, font=self.default_font)
        self.save_log_button.pack(pady=5)

        self.reset_button = tk.Button(controls_frame, text=format_persian("شروع مجدد"), command=self.reset_game, width=10, font=self.default_font)
        self.reset_button.pack(pady=5)

        # (فعلا نگه میداریم اگر باز هم مشکل بود حذف میکنیم) فریم برای حروف ستون‌ها در پایین
        bottom_labels_frame = tk.Frame(main_frame)
        bottom_labels_frame.grid(row=2, column=1, columnspan=self.board_size, sticky="ew")
        for j in range(self.board_size):
            col_label = tk.Label(bottom_labels_frame, text=chr(ord('A') + j), width=3, anchor="center", font=self.default_font)
            col_label.pack(side="left", padx=self.cell_size // 3)

        self.draw_board()
        self.update_valid_moves()

    def reset_board_state(self):
        self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.board[3][3] = 'white'
        self.board[3][4] = 'black'
        self.board[4][3] = 'black'
        self.board[4][4] = 'white'

    def reset_game(self):
        self.reset_board_state()
        self.current_player = "black"
        self.history = []
        self.NumOfMoves = 0
        self.sequence = ''
        self.sequence2 = ''
        self.draw_board()
        self.update_valid_moves()
        self.enable_undo()
        self.disable_redo()

    def draw_board(self):
        self.canvas.delete("all")  # پاک کردن تمام عناصر قبلی canvas
        self.pieces = {}
        for i in range(self.board_size):
            for j in range(self.board_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = (j + 1) * self.cell_size
                y2 = (i + 1) * self.cell_size
                color = "green" if (i + j) % 2 == 0 else "forest green"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                piece = self.board[i][j]
                if piece:
                    radius = self.cell_size // 3
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    oval = self.canvas.create_oval(center_x - radius, center_y - radius,
                                                   center_x + radius, center_y + radius,
                                                   fill=piece, outline="black")
                    self.pieces[(i, j)] = oval
        if self.show_hints.get():
            self.draw_hints()

    def on_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if self.NumOfMoves == 0:
            current_board = [row[:] for row in self.board]
            self.history.append((current_board, self.current_player))

        if self.is_valid_move(row, col):
            if self.NumOfMoves < len(self.history) - 1:
                # اگر بعد از Undo حرکت جدید انجام شود، تاریخچه جلو را حذف کنید
                self.history = self.history[:self.NumOfMoves+1]
                self.disable_redo()
            self.place_piece(row, col)
            self.animate_flip(row, col)
            self.switch_player()
            self.update_valid_moves()
            self.enable_redo()
            self.sequence = self.sequence[:2*self.NumOfMoves] + chr(ord('A') + col) + str(row + 1)
            self.sequence2 = self.sequence2[:2*self.NumOfMoves] + chr(int(68.5 + (68.5 - (ord('A') + col)))) + str(4.5 + (4.5 - (row + 1)))
            self.NumOfMoves += 1
            # ذخیره وضعیت جدید بعد از انجام حرکت
            self.save_state()
        else:
            reshaped_text = arabic_reshaper.reshape("این حرکت مجاز نیست.")
            bidi_text = get_display(reshaped_text)
            messagebox.showinfo("خطا", bidi_text)

    def check_hint(self):
        if self.show_hints.get():
            self.draw_hints()
        else:
            self.draw_board()



    def save_game_log(self):
        filename = ""
        x = 1
        if self.player_color.get() == "سیاه":
            if self.NumOfMoves % 2 == 0: # این بهترین روش نیست اما برای اوپنینگ با احتمال زیاد کار می کند، فکر می کنم 99.99٪ یا شاید 100٪
                self.NumOfMoves -= 1
            filename = "black_moves.txt"
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()  # حذف فضای اضافی اول و انتهای خط
                    N = min(self.NumOfMoves, len(line)//2)
                    if line:  # اگر خط خالی نیست
                        if (self.sequence[:2] != line[:2]) and (self.sequence2[:2] != line[:2]): # برای اولین حرکت چون حرکت قبلی ای وجود ندارد...
                            print(self.sequence, line, 1000)
                            reshaped_text = arabic_reshaper.reshape("دنباله با کتاب مغایرت دارد")
                            bidi_text = get_display(reshaped_text)
                            messagebox.showinfo("خطا", bidi_text)
                            x = 0
                            break
                        if self.sequence[:2*self.NumOfMoves] == line[:2*self.NumOfMoves] or self.sequence2[:2*self.NumOfMoves] == line[:2*self.NumOfMoves]:
                            print(self.sequence, line, 5000)
                            reshaped_text = arabic_reshaper.reshape("دنباله وجود دارد")
                            bidi_text = get_display(reshaped_text)
                            messagebox.showinfo("خطا", bidi_text)
                            x = 0
                            break

                        for R in range(N, 2, -2):
                            if ( self.sequence[:2 * (R - 1)] == line[:2 * (R - 1)]) and (self.sequence[2 * (R - 1):2 * R] != line[2 * (R - 1):2 * R]):
                                print(self.sequence[:2 * (R - 1)],line[:2 * (R - 1)],1000)
                                print(self.sequence[2 * (R - 1):2 * R],line[2 * (R - 1):2 * R],1000)
                                print(self.sequence, line, 1000)
                                reshaped_text = arabic_reshaper.reshape("دنباله با کتاب مغایرت دارد")
                                bidi_text = get_display(reshaped_text)
                                messagebox.showinfo("خطا", bidi_text)
                                x = 0
                            else:
                                print(self.sequence[:2 * (R - 1)],R)
                                print(self.sequence)
                                print(2 * R - 1,2 * R)
                                print(self.sequence[2 * (R - 1):2 * R])
                            if x == 0: break
                    if x == 0: break
        elif self.player_color.get() == "سفید":
            if self.NumOfMoves % 2 == 1:
                self.NumOfMoves -= 1
            filename = "white_moves.txt"
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()  # حذف فضای اضافی اول و انتهای خط
                    N = min(self.NumOfMoves, len(line) // 2)
                    if self.sequence[:2*self.NumOfMoves] == line[:2*self.NumOfMoves] or self.sequence2[:2*self.NumOfMoves] == line[:2*self.NumOfMoves]:
                        reshaped_text = arabic_reshaper.reshape("دنباله وجود دارد")
                        bidi_text = get_display(reshaped_text)
                        messagebox.showinfo("خطا", bidi_text)
                        x = 0
                        break
                    if line:  # اگر خط خالی نیست
                        for R in range(N, 0, -2):
                            if (self.sequence[:2 * (R - 1)] == line[:2 * (R - 1)]) and (self.sequence[2 * (R - 1):2 * R] != line[2 * (R - 1):2 * R]):
                                reshaped_text = arabic_reshaper.reshape("دنباله با کتاب مغایرت دارد")
                                bidi_text = get_display(reshaped_text)
                                messagebox.showinfo("خطا", bidi_text)
                                x = 0
                            if x == 0: break
                    if x == 0: break

        if x:
            try:
                with open(filename, "a", encoding='utf-8') as f:
                    f.write("".join(self.sequence[:2 * self.NumOfMoves]) + "\n")
                    f.write("".join(self.sequence2[:2 * self.NumOfMoves]) + "\n")
                reshaped_text = arabic_reshaper.reshape(f"دنباله حرکات در فایل {filename} ذخیره شد.")
                bidi_text = get_display(reshaped_text)
                messagebox.showinfo("ذخیره شد", bidi_text)
            except Exception as e:
                reshaped_text = arabic_reshaper.reshape(f"مشکلی در ذخیره حرکات رخ داد: {e}")
        # else:
                bidi_text = get_display(reshaped_text)
        #   messagebox.showerror("خطا", "رنگ بازیکن مشخص نشده است.")

    def save_state(self):
        current_board = [row[:] for row in self.board]
        self.history.append((current_board, self.current_player))
        self.enable_undo()
        self.disable_redo()

    def load_state(self, index):
        if 0 <= index < len(self.history):
            temp_board = [row[:] for row in self.history[index][0]]
            self.board = temp_board
            self.draw_board()
            self.update_valid_moves()
            if index > 0:
                self.enable_undo()
            else:
                self.disable_undo()
            if index < (len(self.history)-1):
                self.enable_redo()
            else:
                self.disable_redo()

    def undo_move(self):
        if self.NumOfMoves > 0:
            self.NumOfMoves -= 1
            self.switch_player()
            self.load_state(self.NumOfMoves)

            # در صورت نیاز، می‌توانید self.sequence رو نیز به صورت زیر به‌روزرسانی کنید:
            # self.sequence = self.sequence[:-2]

    def redo_move(self):
        if self.NumOfMoves < (len(self.history)-1):
            self.NumOfMoves += 1
            self.switch_player()
            self.load_state(self.NumOfMoves)

            # در صورت نیاز، می‌توانید self.sequence رو نیز به صورت مناسب به‌روزرسانی کنید.

    def enable_undo(self):
        self.undo_button.config(state=tk.NORMAL)

    def disable_undo(self):
        self.undo_button.config(state=tk.DISABLED)

    def enable_redo(self):
        self.redo_button.config(state=tk.NORMAL)

    def disable_redo(self):
        self.redo_button.config(state=tk.DISABLED)

    def place_piece(self, row, col):
        self.board[row][col] = self.current_player
        radius = self.cell_size // 3
        center_x = (col * self.cell_size + (col + 1) * self.cell_size) // 2
        center_y = (row * self.cell_size + (row + 1) * self.cell_size) // 2
        oval = self.canvas.create_oval(center_x - radius, center_y - radius,
                                       center_x + radius, center_y + radius,
                                       fill=self.current_player, outline="black")
        self.pieces[(row, col)] = oval

    def is_valid_move(self, row, col):
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        if self.board[row][col] != '':
            return False

        opponent = 'white' if self.current_player == 'black' else 'black'
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == opponent:
                found_opponent = True
                r += dr
                c += dc
            if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == self.current_player and found_opponent:
                return True
        return False

    def animate_flip(self, row, col):
        opponent = 'white' if self.current_player == 'black' else 'black'
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        pieces_to_flip = []

        for dr, dc in directions:
            temp_flip = []
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == opponent:
                temp_flip.append((r, c))
                r += dr
                c += dc
            if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == self.current_player and temp_flip:
                pieces_to_flip.extend(temp_flip)

        for r, c in pieces_to_flip:
            self.board[r][c] = self.current_player
            if (r, c) in self.pieces:
                original_color = opponent
                target_color = self.current_player
                steps = 10
                delay = 50  # میلی ثانیه
                for i in range(steps + 1):
                    ratio = i / steps
                    intermediate_color = self.interpolate_color(original_color, target_color, ratio)
                    self.master.after(i * delay, self._update_piece_color, r, c, intermediate_color)
                self.master.after((steps + 1) * delay, self._final_piece_color, r, c, target_color)
            else:
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = (c + 1) * self.cell_size
                y2 = (r + 1) * self.cell_size
                radius = self.cell_size // 3
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                oval = self.canvas.create_oval(center_x - radius, center_y - radius,
                                               center_x + radius, center_y + radius,
                                               fill=self.current_player, outline="black")
                self.pieces[(r, c)] = oval

    def interpolate_color(self, color1, color2, ratio):
        c1 = self.master.winfo_rgb(color1)
        c2 = self.master.winfo_rgb(color2)
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        return '#%02x%02x%02x' % (r // 256, g // 256, b // 256)

    def _update_piece_color(self, r, c, color):
        if (r, c) in self.pieces:
            self.canvas.itemconfig(self.pieces[(r, c)], fill=color)

    def _final_piece_color(self, r, c, color):
        if (r, c) in self.pieces:
            self.canvas.itemconfig(self.pieces[(r, c)], fill=color)

    def switch_player(self):
        self.current_player = 'white' if self.current_player == 'black' else 'black'

    def update_valid_moves(self):
        self.valid_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.is_valid_move(i, j):
                    self.valid_moves.append((i, j))
        self.draw_board()

        if not self.valid_moves:
            self.switch_player()
            self.valid_moves_other = []
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.is_valid_move(i, j):
                        self.valid_moves_other.append((i, j))
            if not self.valid_moves_other:
                self.game_over()
                return
            else:
                current = "سیاه" if self.current_player == "black" else "سفید"
                other = "سفید" if self.current_player == "black" else "سیاه"
                reshaped_text = arabic_reshaper.reshape(f"هیچ حرکتی برای {other} وجود ندارد. نوبت به {current} رسید.")
                bidi_text = get_display(reshaped_text)
                messagebox.showinfo("اطلاع", bidi_text)

    def draw_hints(self):
        hint_radius = self.cell_size // 8  # کاهش اندازه دایره‌های راهنما
        for r, c in self.valid_moves:
            x1 = c * self.cell_size + self.cell_size // 2 - hint_radius
            y1 = r * self.cell_size + self.cell_size // 2 - hint_radius
            x2 = c * self.cell_size + self.cell_size // 2 + hint_radius
            y2 = r * self.cell_size + self.cell_size // 2 + hint_radius
            hint = self.canvas.create_oval(x1, y1, x2, y2, fill="yellow", outline="")
            self.hint_markers[(r, c)] = hint

    def game_over(self):
        black_count = sum(row.count('black') for row in self.board)
        white_count = sum(row.count('white') for row in self.board)
        winner = "سیاه" if black_count > white_count else "سفید" if white_count > black_count else "مساوی"
        reshaped_text = arabic_reshaper.reshape(f"بازی تمام شد! نتیجه: سیاه {black_count} - سفید {white_count}. برنده: {winner}")
        bidi_text = get_display(reshaped_text)
        messagebox.showinfo("پایان بازی", bidi_text)

if __name__ == "__main__":
    with open("white_moves.txt", "a", encoding='utf-8') as f:
        pass
    with open("black_moves.txt", "a", encoding='utf-8') as f:
        pass
    root = tk.Tk()
    game = Othello(root)
    root.mainloop()
