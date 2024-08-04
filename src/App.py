import tkinter as tk
import os
from tkinter import filedialog, ttk
from ttkthemes import ThemedTk
import CDMvalidator


# fix identifier errors
class App:

    def __init__(self):
        self.root = ThemedTk(theme="clearlooks")
        self.root.geometry("250x250")
        self.root.title("CDM Validator")

    def select_solution_file(self):
        self.solution_path = filedialog.askopenfilename()
        if not os.path.isfile(self.solution_path):
            print("Invalid file selected.")

    def normal_verification(self):
        self.src_path = filedialog.askopenfilename()

    def batch_verification(self):
        self.src_path = filedialog.askdirectory()

    def src_filename_selection(self):
        if self.validation_mode.get() == "normal":
            self.normal_verification()
        else:
            self.batch_verification()

    def verify(self):
        try:
            if self.export_var.get() == "SVG":
                if self.validation_mode.get() == "normal":
                    CDMvalidator.normal_validation_mode(self.src_path, self.solution_path, "SVG")
                else:
                    CDMvalidator.batch_verification_mode(self.src_path, self.solution_path, "SVG")
            elif self.export_var.get() == "PNG":
                if self.validation_mode.get() == "normal":
                    CDMvalidator.normal_validation_mode(self.src_path, self.solution_path, "PNG")
                else:
                    CDMvalidator.batch_verification_mode(self.src_path, self.solution_path, "PNG")
        except Exception as e:
            print(f"An error occurred during verification: {e}")

        finally:
            print("Verification complete.")
            self.root.destroy()

    def run(self):
        self.solution_button = ttk.Button(self.root, text="Select Solution File", command=self.select_solution_file)
        self.solution_button.pack(pady=5)

        self.validation_mode = tk.StringVar(value="normal")
        self.normal_radio = ttk.Radiobutton(self.root, text="Normal Validation", variable=self.validation_mode, value="normal")
        self.normal_radio.pack(pady=5)

        self.batch_radio = ttk.Radiobutton(self.root, text="Batch Validation", variable=self.validation_mode, value="batch")
        self.batch_radio.pack(pady=5)

        self.src_button = ttk.Button(self.root, text="Select source file / folder", command=self.src_filename_selection)
        self.src_button.pack(pady=5)

        self.export_var = tk.StringVar(value="PNG")
        self.png_radio = ttk.Radiobutton(self.root, text="Export PNG", variable=self.export_var, value="PNG")
        self.png_radio.pack(pady=5)

        self.svg_radio = ttk.Radiobutton(self.root, text="Export SVG", variable=self.export_var, value="SVG")
        self.svg_radio.pack(pady=5)

        self.export_button = ttk.Button(self.root, text="Run", command=self.verify)
        self.export_button.pack(pady=5)

        self.root.mainloop()



if __name__ == '__main__':
    app = App()
    app.run()
    exit(0)
