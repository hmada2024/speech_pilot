import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pygame
import tempfile
import os
from gtts import gTTS

class CombinedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("تطبيق الصوتيات الديناميكي ومحول النص إلى صوت")
        self.geometry("800x600")  # حجم أكبر للنافذة

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.dynamic_audio_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dynamic_audio_tab, text="تطبيق الصوتيات الديناميكي")  # تم التصحيح هنا
        self.create_dynamic_audio_ui(self.dynamic_audio_tab)

        self.audio_converter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_converter_tab, text="محول النص إلى صوت")
        self.create_audio_converter_ui(self.audio_converter_tab)

        # تهيئة pygame مرة واحدة فقط
        pygame.mixer.init()

    def create_dynamic_audio_ui(self, master):
        # متغيرات لتخزين الاختيارات
        self.dynamic_db_path = tk.StringVar()
        self.dynamic_selected_table = tk.StringVar()
        self.dynamic_column1 = tk.StringVar()
        self.dynamic_column2 = tk.StringVar()
        self.dynamic_audio_column = tk.StringVar()

        # وصف التطبيق
        description_frame = ttk.LabelFrame(master, text="وصف التطبيق")
        description_frame.pack(padx=10, pady=10, fill="x")

        description_label = tk.Label(description_frame, text=(
            "اختر قاعدة البيانات والجدول والأعمدة، ثم جرّب الأصوات."
        ), anchor="center", justify="center", wraplength=400)
        description_label.pack(padx=10, pady=10)

        # إطار اختيار قاعدة البيانات
        db_frame = ttk.LabelFrame(master, text="قاعدة البيانات")
        db_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(db_frame, text="ملف قاعدة البيانات:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(db_frame, textvariable=self.dynamic_db_path, width=50).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(db_frame, text="تصفح", command=self.browse_database_dynamic).grid(row=0, column=2, padx=5, pady=5)

        # إطار اختيار الجدول والأعمدة
        table_frame = ttk.LabelFrame(master, text="اختيار الجدول والأعمدة")
        table_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(table_frame, text="الجدول:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dynamic_table_combo = ttk.Combobox(table_frame, textvariable=self.dynamic_selected_table, state="readonly")
        self.dynamic_table_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.dynamic_table_combo.bind("<<ComboboxSelected>>", self.update_dynamic_columns)

        ttk.Label(table_frame, text="العمود الأول:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dynamic_column1_combo = ttk.Combobox(table_frame, textvariable=self.dynamic_column1, state="readonly")
        self.dynamic_column1_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(table_frame, text="العمود الثاني:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.dynamic_column2_combo = ttk.Combobox(table_frame, textvariable=self.dynamic_column2, state="readonly")
        self.dynamic_column2_combo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(table_frame, text="عمود الصوت (BLOB):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.dynamic_audio_column_combo = ttk.Combobox(table_frame, textvariable=self.dynamic_audio_column, state="readonly")
        self.dynamic_audio_column_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # زر عرض البيانات
        ttk.Button(master, text="عرض البيانات وتشغيل الصوت", command=self.display_dynamic_data).pack(pady=20)

        # إطار لعرض البيانات
        self.dynamic_data_frame = ttk.LabelFrame(master, text="البيانات")
        self.dynamic_data_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def create_audio_converter_ui(self, master):
        # متغيرات لتخزين الاختيارات
        self.converter_db_path = tk.StringVar()
        self.converter_source_table = tk.StringVar()
        self.converter_source_column = tk.StringVar()
        self.converter_destination_table = tk.StringVar()
        self.converter_destination_column = tk.StringVar()

        # إضافة وصف التطبيق
        description_frame = ttk.LabelFrame(master, text="وصف التطبيق")
        description_frame.pack(padx=10, pady=10, fill="x")

        description_label = tk.Label(description_frame, text=(
            "أهلاً بك في تطبيق محول النص إلى صوت!\n"
            "يتيح لك هذا التطبيق تحويل النصوص الموجودة في قاعدة بيانات SQLite إلى ملفات صوتية\n"
            "بالاعتماد على مكتبة gTTS (Google Text-to-Speech).\n\n"
            "الخطوات:\n"
            "1. اختر ملف قاعدة البيانات.\n"
            "2. اختر الجدول والعمود الذي يحتوي على النص.\n"
            "3. اختر الجدول والعمود الذي سيتم تخزين الصوت فيه.\n"
            "4. اضغط على زر 'تحويل النص إلى صوت' للبدء في التحويل.\n\n"
            "تمتع باستخدام التطبيق!"
        ), anchor="center", justify="center", wraplength=400)
        description_label.pack(padx=10, pady=10)

        # إطار اختيار قاعدة البيانات
        db_frame = ttk.LabelFrame(master, text="قاعدة البيانات")
        db_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(db_frame, text="ملف قاعدة البيانات:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(db_frame, textvariable=self.converter_db_path, width=50).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(db_frame, text="تصفح", command=self.browse_database_converter).grid(row=0, column=2, padx=5, pady=5)

        # إطار اختيار المصدر
        source_frame = ttk.LabelFrame(master, text="المصدر (النص)")
        source_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(source_frame, text="الجدول:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.converter_source_table_combo = ttk.Combobox(source_frame, textvariable=self.converter_source_table, state="readonly")
        self.converter_source_table_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.converter_source_table_combo.bind("<<ComboboxSelected>>", self.update_converter_source_columns)

        ttk.Label(source_frame, text="العمود:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.converter_source_column_combo = ttk.Combobox(source_frame, textvariable=self.converter_source_column, state="readonly")
        self.converter_source_column_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # إطار اختيار الوجهة
        dest_frame = ttk.LabelFrame(master, text="الوجهة (الصوت)")
        dest_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(dest_frame, text="الجدول:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.converter_dest_table_combo = ttk.Combobox(dest_frame, textvariable=self.converter_destination_table, state="readonly")
        self.converter_dest_table_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.converter_dest_table_combo.bind("<<ComboboxSelected>>", self.update_converter_dest_columns)

        ttk.Label(dest_frame, text="العمود:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.converter_dest_column_combo = ttk.Combobox(dest_frame, textvariable=self.converter_destination_column, state="readonly")
        self.converter_dest_column_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # زر المعالجة
        ttk.Button(master, text="تحويل النص إلى صوت", command=self.process_data).pack(pady=20)

        # شريط التقدم
        self.progress = ttk.Progressbar(master, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(padx=10, pady=5)

    # --- وظائف تطبيق الصوتيات الديناميكي ---
    def browse_database_dynamic(self):
        file_path = filedialog.askopenfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")])
        if file_path:
            self.dynamic_db_path.set(file_path)
            self.update_dynamic_table_list()

    def update_dynamic_table_list(self):
        db_path = self.dynamic_db_path.get()
        if db_path:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                self.dynamic_table_combo['values'] = tables
                self.converter_source_table_combo['values'] = tables # تحديث قائمة الجداول في التبويب الآخر أيضًا
                self.converter_dest_table_combo['values'] = tables   # تحديث قائمة الجداول في التبويب الآخر أيضًا
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"خطأ في فتح قاعدة البيانات: {e}")

    def update_dynamic_columns(self, event=None):
        db_path = self.dynamic_db_path.get()
        table_name = self.dynamic_selected_table.get()
        if db_path and table_name:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [row[1] for row in cursor.fetchall()]
                self.dynamic_column1_combo['values'] = columns
                self.dynamic_column2_combo['values'] = columns
                self.dynamic_audio_column_combo['values'] = columns
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"خطأ في جلب أعمدة الجدول: {e}")

    def fetch_dynamic_data(self, table, col1, col2, audio_col):
        db_path = self.dynamic_db_path.get()
        if db_path and table and col1 and col2 and audio_col:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(f"SELECT {col1}, {col2}, {audio_col} FROM {table}")
                rows = cursor.fetchall()
                conn.close()
                return rows
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"خطأ في جلب البيانات: {e}")
                return []
        return []

    def play_audio(self, audio_blob):
        if audio_blob:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                    temp_audio.write(audio_blob)
                    temp_audio_path = temp_audio.name
                pygame.mixer.quit() # التأكد من إغلاق أي صوت قيد التشغيل
                pygame.mixer.init()
                pygame.mixer.music.load(temp_audio_path)
                pygame.mixer.music.play()
                print("Playing audio")
                os.remove(temp_audio_path)
            except pygame.error as e:
                print(f"Pygame Error playing audio: {e}")
            except Exception as e:
                print(f"Error playing audio: {e}")

    def display_dynamic_data(self):
        for widget in self.dynamic_data_frame.winfo_children():
            widget.destroy()

        table = self.dynamic_selected_table.get()
        col1 = self.dynamic_column1.get()
        col2 = self.dynamic_column2.get()
        audio_col = self.dynamic_audio_column.get()

        rows = self.fetch_dynamic_data(table, col1, col2, audio_col)

        canvas = tk.Canvas(self.dynamic_data_frame)
        scrollbar = tk.Scrollbar(self.dynamic_data_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for index, row in enumerate(rows):
            label1 = tk.Label(scrollable_frame, text=row[0], width=30, anchor='w')
            label2 = tk.Label(scrollable_frame, text=row[1], width=30, anchor='w')
            play_button = tk.Button(scrollable_frame, text="🔊", command=lambda ab=row[2]: self.play_audio(ab))

            label1.grid(row=index, column=0, padx=5, pady=5)
            label2.grid(row=index, column=1, padx=5, pady=5)
            play_button.grid(row=index, column=2, padx=5, pady=5)

    # --- وظائف تطبيق محول النص إلى صوت ---
    def browse_database_converter(self):
        file_path = filedialog.askopenfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")])
        if file_path:
            self.converter_db_path.set(file_path)
            self.update_converter_table_lists()

    def update_converter_table_lists(self):
        db_path = self.converter_db_path.get()
        if db_path:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                self.converter_source_table_combo['values'] = tables
                self.converter_dest_table_combo['values'] = tables
                self.dynamic_table_combo['values'] = tables # تحديث قائمة الجداول في التبويب الآخر أيضًا
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"خطأ في فتح قاعدة البيانات: {e}")

    def update_converter_source_columns(self, event=None):
        self._update_columns(self.converter_source_table.get(), self.converter_source_column_combo)

    def update_converter_dest_columns(self, event=None):
        self._update_columns(self.converter_destination_table.get(), self.converter_dest_column_combo)

    def _update_columns(self, table_name, combo_box):
        db_path = self.converter_db_path.get()
        if db_path and table_name:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [row[1] for row in cursor.fetchall()]
                combo_box['values'] = columns
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"خطأ في جلب أعمدة الجدول: {e}")

    def convert_text_to_blob(self, text):
        tts = gTTS(text=text, lang='ar') # يمكنك تغيير اللغة هنا
        temp_file = "temp_audio.mp3"
        tts.save(temp_file)
        with open(temp_file, "rb") as audio_file:
            audio_blob = audio_file.read()
        os.remove(temp_file)
        return audio_blob

    def process_data(self):
        db_path = self.converter_db_path.get()
        source_table = self.converter_source_table.get()
        source_column = self.converter_source_column.get()
        destination_table = self.converter_destination_table.get()
        destination_column = self.converter_destination_column.get()

        if not all([db_path, source_table, source_column, destination_table, destination_column]):
            messagebox.showerror("خطأ", "الرجاء ملء جميع الحقول.")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # جلب البيانات من جدول المصدر
            cursor.execute(f"SELECT id, {source_column} FROM {source_table}")
            rows = cursor.fetchall()

            # إعداد شريط التقدم
            self.progress["maximum"] = len(rows)
            self.progress["value"] = 0

            for row in rows:
                item_id, text_to_convert = row
                try:
                    audio_blob = self.convert_text_to_blob(text_to_convert)
                    # تحديث جدول الوجهة
                    cursor.execute(f"UPDATE {destination_table} SET {destination_column} = ? WHERE id = ?", (audio_blob, item_id))
                    conn.commit()
                    self.progress["value"] += 1
                    self.update_idletasks()
                    print(f"تم تحويل النص من {source_table}.{source_column} (ID: {item_id}) إلى صوت وحفظه في {destination_table}.{destination_column}.")
                except Exception as e:
                    print(f"فشل تحويل النص (ID: {item_id}): {e}")

            messagebox.showinfo("اكتمل", "تمت معالجة البيانات بنجاح.")
            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror("خطأ في قاعدة البيانات", f"حدث خطأ أثناء معالجة قاعدة البيانات: {e}")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    app = CombinedApp()
    app.mainloop()