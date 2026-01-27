import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser, ttk
from tkinter import font as tkfont

APP_NAME = "SkyNote — простой текстовый редактор"

class SkyNote(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("900x550")

        # ====== состояние форматирования ======
        self.font_family = tk.StringVar(value="Arial")
        self.font_size   = tk.IntVar(value=12)
        self.bold_var    = tk.BooleanVar(value=False)
        self.italic_var  = tk.BooleanVar(value=False)
        self.underline_var = tk.BooleanVar(value=False)
        self.fg_color = "#000000"
        self.bg_color = "#ffffff"

        # ====== виджеты ======
        self._build_ui()
        self._apply_font()

        # горячие клавиши
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-f>", lambda e: self.open_find_dialog())
        self.bind_all("<Control-a>", lambda e: self.select_all())

    # ---------- UI ----------
    def _build_ui(self):
        # текст
        self.text = tk.Text(self, wrap="word", undo=True, autoseparators=True, maxundo=-1)
        self.text.config(bg=self.bg_color, fg=self.fg_color)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # вертикальная прокрутка
        yscroll = tk.Scrollbar(self, command=self.text.yview)
        yscroll.pack(side=tk.LEFT, fill=tk.Y)
        self.text.config(yscrollcommand=yscroll.set)

        # панель кнопок
        panel = tk.Frame(self)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=6, pady=6)

        buttons = [
            ("Открыть", self.open_file),
            ("Сохранить", self.save_file),
            ("Копировать", self.copy_text),
            ("Вырезать", self.cut_text),
            ("Очистить все", self.clear_all),
            ("Вставить", self.paste_text),
            ("Выделить все", self.select_all),
            ("Удалить выделенное", self.delete_selected),
            ("Поиск", self.open_find_dialog),
            ("Шрифт/стиль…", self.open_font_dialog),
            ("Цвет текста…", self.change_text_color),
            ("Цвет фона…", self.change_bg_color),
        ]
        for name, cmd in buttons:
            b = tk.Button(panel, text=name, width=20, command=cmd)
            b.pack(pady=3)

        # тэги подсветки поиска
        self.text.tag_config("found", background="yellow")
        self.text.tag_config("cursor", background="#d0e7ff")

    # ---------- файл ----------
    def open_file(self):
        fn = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not fn: return
        try:
            with open(fn, "r", encoding="utf-8") as f:
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, f.read())
                self.title(f"{APP_NAME} — {fn}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def save_file(self):
        fn = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not fn: return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))
                self.title(f"{APP_NAME} — {fn}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ---------- буфер/редактирование ----------
    def copy_text(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.text.get(tk.SEL_FIRST, tk.SEL_LAST))
        except tk.TclError:
            pass

    def cut_text(self):
        try:
            self.copy_text()
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def paste_text(self):
        try:
            self.text.insert(tk.INSERT, self.clipboard_get())
        except tk.TclError:
            pass

    def clear_all(self):
        self.text.delete("1.0", tk.END)

    def select_all(self, *_):
        self.text.focus_set()
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def delete_selected(self):
        try:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    # ---------- поиск ----------
    def open_find_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Поиск")
        dlg.transient(self)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="Строка поиска:").grid(row=0, column=0, padx=8, pady=(10, 4), sticky="w")
        entry = tk.Entry(dlg, width=32)
        entry.grid(row=1, column=0, columnspan=3, padx=8, pady=2, sticky="we")
        entry.focus_set()

        case_var = tk.BooleanVar(value=False)
        whole_word_var = tk.BooleanVar(value=False)
        tk.Checkbutton(dlg, text="С учётом регистра", variable=case_var).grid(row=2, column=0, padx=8, sticky="w")
        tk.Checkbutton(dlg, text="Только слово целиком", variable=whole_word_var).grid(row=3, column=0, padx=8, sticky="w")

        def clear_highlight():
            self.text.tag_remove("found", "1.0", tk.END)
            self.text.tag_remove("cursor", "1.0", tk.END)

        def find_next():
            query = entry.get()
            if not query:
                return
            clear_highlight()
            start = self.text.index(tk.INSERT)
            haystack = self.text.get(start, tk.END)
            if not case_var.get():
                query_l, haystack_l = query.lower(), haystack.lower()
            else:
                query_l, haystack_l = query, haystack

            # поиск с текущей позиции, затем от начала (круговой)
            offset = haystack_l.find(query_l)
            if offset == -1:
                # попробовать от начала
                haystack2 = self.text.get("1.0", tk.END)
                haystack2l = haystack2 if case_var.get() else haystack2.lower()
                offset2 = haystack2l.find(query_l)
                if offset2 == -1:
                    messagebox.showinfo("Поиск", "Совпадений не найдено.")
                    return
                start_index = f"1.0+{offset2}c"
            else:
                start_index = f"{start}+{offset}c"

            end_index = f"{start_index}+{len(query)}c"

            if whole_word_var.get():
                # границы должны быть не-буквенно-цифровые
                import re
                text_slice = self.text.get(start_index, end_index)
                if text_slice != query if case_var.get() else text_slice.lower() != query.lower():
                    # защита на всякий
                    pass
                # проверим границы
                before = self.text.get(f"{start_index}-1c", start_index)
                after = self.text.get(end_index, f"{end_index}+1c")
                is_word_boundary = lambda ch: not ch.isalnum() and ch != "_"
                if not (is_word_boundary(before) and is_word_boundary(after)):
                    # если не целое слово — ищем дальше рекурсивно
                    self.text.mark_set(tk.INSERT, f"{end_index}")
                    find_next()
                    return

            self.text.tag_add("found", start_index, end_index)
            self.text.tag_add("cursor", start_index, end_index)
            self.text.mark_set(tk.INSERT, end_index)
            self.text.see(start_index)

        def find_all():
            query = entry.get()
            if not query:
                return
            clear_highlight()
            text_all = self.text.get("1.0", tk.END)
            src = text_all
            q = query
            if not case_var.get():
                src = text_all.lower()
                q = query.lower()

            idx = 0
            count = 0
            while True:
                pos = src.find(q, idx)
                if pos == -1:
                    break
                start_index = f"1.0+{pos}c"
                end_index = f"{start_index}+{len(query)}c"
                if whole_word_var.get():
                    before = self.text.get(f"{start_index}-1c", start_index)
                    after = self.text.get(end_index, f"{end_index}+1c")
                    is_word_boundary = lambda ch: not ch.isalnum() and ch != "_"
                    if not (is_word_boundary(before) and is_word_boundary(after)):
                        idx = pos + 1
                        continue
                self.text.tag_add("found", start_index, end_index)
                count += 1
                idx = pos + len(q)
            messagebox.showinfo("Поиск", f"Найдено совпадений: {count}")

        btn_frame = tk.Frame(dlg)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=8)
        tk.Button(btn_frame, text="Найти далее", width=14, command=find_next).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Найти все", width=14, command=find_all).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Очистить", width=10, command=lambda:(self.text.tag_remove("found","1.0",tk.END),
                                                                       self.text.tag_remove("cursor","1.0",tk.END))).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Закрыть", width=10, command=dlg.destroy).pack(side=tk.LEFT, padx=4)

        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

    # ---------- формат ----------
    def _apply_font(self):
        weight = "bold" if self.bold_var.get() else "normal"
        slant  = "italic" if self.italic_var.get() else "roman"
        underline = 1 if self.underline_var.get() else 0
        f = tkfont.Font(family=self.font_family.get(), size=self.font_size.get(),
                        weight=weight, slant=slant, underline=underline)
        self.text.configure(font=f, fg=self.fg_color, bg=self.bg_color)

    def open_font_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Шрифт и стиль")
        dlg.transient(self)
        dlg.resizable(False, False)
        dlg.grab_set()

        # список шрифтов
        tk.Label(dlg, text="Шрифт:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        families = sorted(tkfont.families())
        fam_cb = ttk.Combobox(dlg, values=families, width=28)
        fam_cb.set(self.font_family.get())
        fam_cb.grid(row=1, column=0, padx=10, pady=2)

        # размер
        tk.Label(dlg, text="Размер:").grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))
        size_sp = tk.Spinbox(dlg, from_=6, to=96, width=6)
        size_sp.delete(0, tk.END); size_sp.insert(0, str(self.font_size.get()))
        size_sp.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        # стиль
        bold_cb = tk.Checkbutton(dlg, text="Жирный", variable=self.bold_var)
        italic_cb = tk.Checkbutton(dlg, text="Курсив", variable=self.italic_var)
        under_cb = tk.Checkbutton(dlg, text="Подчёркнутый", variable=self.underline_var)
        bold_cb.grid(row=2, column=0, padx=10, pady=4, sticky="w")
        italic_cb.grid(row=3, column=0, padx=10, pady=4, sticky="w")
        under_cb.grid(row=4, column=0, padx=10, pady=4, sticky="w")

        # предпросмотр
        prev = tk.Label(dlg, text="Пример текста: SkyNote", relief="groove", width=34, height=2)
        prev.grid(row=2, column=1, rowspan=2, padx=10, pady=4, sticky="we")

        def update_preview(*_):
            family = fam_cb.get()
            try:
                size = int(size_sp.get())
            except ValueError:
                size = self.font_size.get()
            weight = "bold" if self.bold_var.get() else "normal"
            slant  = "italic" if self.italic_var.get() else "roman"
            underline = 1 if self.underline_var.get() else 0
            prev.configure(font=tkfont.Font(family=family, size=size, weight=weight,
                                            slant=slant, underline=underline))
        for w in (fam_cb, size_sp, bold_cb, italic_cb, under_cb):
            w.bind("<<ComboboxSelected>>", update_preview)
            w.bind("<ButtonRelease-1>", update_preview)
            w.bind("<KeyRelease>", update_preview)
        update_preview()

        def apply_and_close():
            self.font_family.set(fam_cb.get())
            try:
                self.font_size.set(int(size_sp.get()))
            except ValueError:
                pass
            self._apply_font()
            dlg.destroy()

        btns = tk.Frame(dlg)
        btns.grid(row=5, column=0, columnspan=2, pady=8)
        tk.Button(btns, text="OK", width=10, command=apply_and_close).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Отмена", width=10, command=dlg.destroy).pack(side=tk.LEFT, padx=6)

        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

    def change_text_color(self):
        color = colorchooser.askcolor(initialcolor=self.fg_color)[1]
        if color:
            self.fg_color = color
            self._apply_font()

    def change_bg_color(self):
        color = colorchooser.askcolor(initialcolor=self.bg_color)[1]
        if color:
            self.bg_color = color
            self._apply_font()

if __name__ == "__main__":
    SkyNote().mainloop()
