import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageTk
import os

APP_NAME = "PyPaint — простой графический редактор"
CANVAS_BG = "white"

TOOLS = ("Кисть", "Ластик", "Линия", "Прямоугольник", "Овал", "Пипетка")

class PyPaint(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x720")

        # состояния
        self.tool = tk.StringVar(value="Кисть")
        self.brush_size = tk.IntVar(value=8)
        self.color = "#000000"
        self.eraser_color = CANVAS_BG
        self.preview_item = None
        self.start_x = self.start_y = None
        self.last_x = self.last_y = None

        # холст (Canvas) + фоновое PIL изображение
        self.canvas = tk.Canvas(self, bg=CANVAS_BG, cursor="tcross")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # дефолтное изображение (подложка)
        self.image = Image.new("RGB", (1200, 800), CANVAS_BG)
        self.draw = ImageDraw.Draw(self.image)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        # стеки истории
        self.history = [self.image.copy()]
        self.redo_stack = []

        # правая панель инструментов
        self._build_toolbar()

        # меню
        self._build_menubar()

        # события мыши
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # хоткеи
        self.bind_all("<Control-n>", lambda e: self.new_image())
        self.bind_all("<Control-o>", lambda e: self.open_image())
        self.bind_all("<Control-s>", lambda e: self.save_image_as())
        self.bind_all("<Control-z>", lambda e: self.undo())
        self.bind_all("<Control-y>", lambda e: self.redo())
        self.bind_all("<Escape>",    lambda e: self.cancel_preview())

        self.update_title()

    # ---------- UI ----------
    def _build_toolbar(self):
        panel = tk.Frame(self, padx=6, pady=6)
        panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(panel, text="Инструменты", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,6))
        for t in TOOLS:
            rb = tk.Radiobutton(panel, text=t, value=t, variable=self.tool, command=self.update_cursor)
            rb.pack(anchor="w")

        tk.Label(panel, text="Размер кисти", pady=6).pack(anchor="w")
        tk.Scale(panel, from_=1, to=64, orient=tk.HORIZONTAL, variable=self.brush_size).pack(fill=tk.X)

        self.color_preview = tk.Label(panel, text="  Цвет  ", bg=self.color, fg="white")
        self.color_preview.pack(pady=(8,2), fill=tk.X)
        tk.Button(panel, text="Выбрать цвет…", command=self.pick_color).pack(fill=tk.X)

        tk.Label(panel, text=" ", pady=2).pack()  # отступ
        tk.Button(panel, text="Очистить холст", command=self.clear_canvas).pack(fill=tk.X)

        tk.Label(panel, text=" ", pady=2).pack()
        tk.Button(panel, text="Отменить (Ctrl+Z)", command=self.undo).pack(fill=tk.X)
        tk.Button(panel, text="Повторить (Ctrl+Y)", command=self.redo).pack(fill=tk.X)

        tk.Label(panel, text=" ", pady=2).pack()
        tk.Button(panel, text="Открыть… (Ctrl+O)", command=self.open_image).pack(fill=tk.X)
        tk.Button(panel, text="Сохранить как… (Ctrl+S)", command=self.save_image_as).pack(fill=tk.X)
        tk.Button(panel, text="Новый (Ctrl+N)", command=self.new_image).pack(fill=tk.X)

        tk.Label(panel, text=" ", pady=2).pack()
        tk.Button(panel, text="О приложении", command=self.about).pack(fill=tk.X)

    def _build_menubar(self):
        m = tk.Menu(self)
        file_m = tk.Menu(m, tearoff=0)
        file_m.add_command(label="Новый", accelerator="Ctrl+N", command=self.new_image)
        file_m.add_command(label="Открыть…", accelerator="Ctrl+O", command=self.open_image)
        file_m.add_command(label="Сохранить как…", accelerator="Ctrl+S", command=self.save_image_as)
        file_m.add_separator()
        file_m.add_command(label="Выход", command=self.quit)
        m.add_cascade(label="Файл", menu=file_m)

        edit_m = tk.Menu(m, tearoff=0)
        edit_m.add_command(label="Отменить", accelerator="Ctrl+Z", command=self.undo)
        edit_m.add_command(label="Повторить", accelerator="Ctrl+Y", command=self.redo)
        edit_m.add_separator()
        edit_m.add_command(label="Очистить холст", command=self.clear_canvas)
        m.add_cascade(label="Правка", menu=edit_m)

        tools_m = tk.Menu(m, tearoff=0)
        for t in TOOLS:
            tools_m.add_radiobutton(label=t, variable=self.tool, value=t, command=self.update_cursor)
        tools_m.add_separator()
        tools_m.add_command(label="Выбрать цвет…", command=self.pick_color)
        m.add_cascade(label="Инструменты", menu=tools_m)

        help_m = tk.Menu(m, tearoff=0)
        help_m.add_command(label="О PyPaint", command=self.about)
        m.add_cascade(label="Справка", menu=help_m)

        self.config(menu=m)

    def update_title(self, path=None):
        extra = f" — {os.path.basename(path)}" if path else ""
        self.title(APP_NAME + extra)

    def update_cursor(self):
        cur = "dotbox" if self.tool.get() in ("Пипетка",) else "tcross"
        self.canvas.configure(cursor=cur)

    def pick_color(self):
        c = colorchooser.askcolor(initialcolor=self.color)[1]
        if c:
            self.color = c
            self.color_preview.configure(bg=c)

    # ---------- История ----------
    def push_history(self):
        # сохраняем копию в стек, чистим redo
        self.history.append(self.image.copy())
        if len(self.history) > 50:
            self.history = self.history[-50:]
        self.redo_stack.clear()

    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())  # текущую — в redo
            self.image = self.history[-1].copy()
            self.draw = ImageDraw.Draw(self.image)
            self.refresh_canvas()
        else:
            self.bell()

    def redo(self):
        if self.redo_stack:
            img = self.redo_stack.pop()
            self.history.append(img)
            self.image = img.copy()
            self.draw = ImageDraw.Draw(self.image)
            self.refresh_canvas()
        else:
            self.bell()

    # ---------- Работа с изображением ----------
    def refresh_canvas(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        # заменить картинку у существующего элемента
        self.canvas.itemconfig(self.bg_image_id, image=self.tk_image)
        # подогнать размеры прокрутки/видимой области
        self.canvas.config(scrollregion=(0, 0, self.image.width, self.image.height))

    def new_image(self):
        if not self.confirm_discard():
            return
        w = max(self.image.width, 1200)
        h = max(self.image.height, 800)
        self.image = Image.new("RGB", (w, h), CANVAS_BG)
        self.draw = ImageDraw.Draw(self.image)
        self.refresh_canvas()
        self.history = [self.image.copy()]
        self.redo_stack.clear()
        self.update_title()

    def open_image(self):
        fn = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp"), ("Все файлы", "*.*")])
        if not fn:
            return
        try:
            img = Image.open(fn).convert("RGB")
            self.image = img.copy()
            self.draw = ImageDraw.Draw(self.image)
            self.refresh_canvas()
            self.history = [self.image.copy()]
            self.redo_stack.clear()
            self.update_title(fn)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_image_as(self):
        fn = filedialog.asksaveasfilename(defaultextension=".png",
                                          filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp")])
        if not fn:
            return
        try:
            # JPEG не поддерживает прозрачность, но у нас RGB — всё ок
            self.image.save(fn)
            self.update_title(fn)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def clear_canvas(self):
        self.draw.rectangle((0, 0, self.image.width, self.image.height), fill=CANVAS_BG)
        self.refresh_canvas()
        self.push_history()

    def about(self):
        messagebox.showinfo("О PyPaint",
                            "PyPaint — учебный мини-редактор рисования на Python/Tkinter.\n"
                            "Инструменты: кисть, ластик, линия, прямоугольник, овал, пипетка.\n"
                            "Горячие клавиши: Ctrl+N/O/S, Ctrl+Z/Y, Esc — отменить превью фигуры.")

    def confirm_discard(self):
        # простая защита от потери данных
        return messagebox.askyesno("Подтвердите", "Создать новый холст? Несохранённые изменения будут потеряны.")

    # ---------- Рисование ----------
    def on_press(self, e):
        self.cancel_preview()
        self.start_x, self.start_y = e.x, e.y
        self.last_x, self.last_y = e.x, e.y

        if self.tool.get() == "Пипетка":
            # забрать цвет пикселя
            if 0 <= e.x < self.image.width and 0 <= e.y < self.image.height:
                rgb = self.image.getpixel((e.x, e.y))
                self.color = "#%02x%02x%02x" % rgb
                self.color_preview.configure(bg=self.color)
            return

        if self.tool.get() in ("Линия", "Прямоугольник", "Овал"):
            # создаём превью-элемент
            if self.tool.get() == "Линия":
                self.preview_item = self.canvas.create_line(e.x, e.y, e.x, e.y,
                                                            fill=self.color, width=self.brush_size.get())
            elif self.tool.get() == "Прямоугольник":
                self.preview_item = self.canvas.create_rectangle(e.x, e.y, e.x, e.y,
                                                                 outline=self.color, width=self.brush_size.get())
            else:  # Овал
                self.preview_item = self.canvas.create_oval(e.x, e.y, e.x, e.y,
                                                            outline=self.color, width=self.brush_size.get())

    def on_drag(self, e):
        if self.start_x is None:
            return

        if self.tool.get() == "Кисть":
            self.draw_line_on_image(self.last_x, self.last_y, e.x, e.y,
                                    self.color, self.brush_size.get())
            self.last_x, self.last_y = e.x, e.y
            self.refresh_canvas()

        elif self.tool.get() == "Ластик":
            self.draw_line_on_image(self.last_x, self.last_y, e.x, e.y,
                                    self.eraser_color, self.brush_size.get())
            self.last_x, self.last_y = e.x, e.y
            self.refresh_canvas()

        elif self.tool.get() in ("Линия", "Прямоугольник", "Овал"):
            # обновляем превью-фигуру
            if self.preview_item:
                if self.tool.get() == "Линия":
                    self.canvas.coords(self.preview_item, self.start_x, self.start_y, e.x, e.y)
                else:
                    self.canvas.coords(self.preview_item, self.start_x, self.start_y, e.x, e.y)

    def on_release(self, e):
        if self.start_x is None:
            return

        if self.tool.get() in ("Кисть", "Ластик"):
            # фиксируем мазок в историю
            self.push_history()

        elif self.tool.get() == "Линия":
            self.draw.line((self.start_x, self.start_y, e.x, e.y),
                           fill=self.color, width=self.brush_size.get())
            self.refresh_canvas()
            self.push_history()

        elif self.tool.get() == "Прямоугольник":
            self.draw.rectangle((self.start_x, self.start_y, e.x, e.y),
                                outline=self.color, width=self.brush_size.get())
            self.refresh_canvas()
            self.push_history()

        elif self.tool.get() == "Овал":
            self.draw.ellipse((self.start_x, self.start_y, e.x, e.y),
                              outline=self.color, width=self.brush_size.get())
            self.refresh_canvas()
            self.push_history()

        # сброс временных состояний
        self.cancel_preview()
        self.start_x = self.start_y = None
        self.last_x = self.last_y = None

    def draw_line_on_image(self, x1, y1, x2, y2, color, width):
        # сглаживание: линия + кружок на концах
        self.draw.line((x1, y1, x2, y2), fill=color, width=width, joint="curve")
        r = width // 2
        self.draw.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=color, outline=color)

    def cancel_preview(self):
        if self.preview_item:
            self.canvas.delete(self.preview_item)
            self.preview_item = None

if __name__ == "__main__":
    PyPaint().mainloop()
