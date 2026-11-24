import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from mutagen.id3 import ID3, APIC, ID3NoHeaderError
from PIL import Image, ImageTk

class AlbumArtStudio:
    def __init__(self, root):
        self.root = root
        root.title("Album Art Studio")
        root.geometry("740x560")
        root.minsize(650, 500)
        self.files, self.image_path, self.output_dir = [], None, None
        self.preview_photo = None

        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Album Art Studio", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Add or replace the cover image embedded in MP3 files.").pack(anchor="w", pady=(2, 14))

        body = ttk.Frame(frame)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))
        ttk.Label(left, text="MP3 files", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        listbox_frame = ttk.Frame(left)
        listbox_frame.pack(fill="both", expand=True, pady=6)
        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, font=("Segoe UI", 10))
        scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        row = ttk.Frame(left); row.pack(fill="x")
        ttk.Button(row, text="Add MP3 files", command=self.add_files).pack(side="left")
        ttk.Button(row, text="Remove selected", command=self.remove_selected).pack(side="left", padx=5)
        ttk.Button(row, text="Clear", command=self.clear).pack(side="left")

        right = ttk.Frame(body, width=220)
        right.pack(side="right", fill="y"); right.pack_propagate(False)
        ttk.Label(right, text="Cover image", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.preview = ttk.Label(right, text="No image selected", anchor="center", relief="groove")
        self.preview.pack(fill="both", expand=True, pady=6)
        ttk.Button(right, text="Choose JPG / PNG", command=self.choose_image).pack(fill="x")
        self.image_name = ttk.Label(right, text="No image selected", wraplength=210)
        self.image_name.pack(anchor="w", pady=6)

        ttk.Separator(frame).pack(fill="x", pady=12)
        outrow = ttk.Frame(frame); outrow.pack(fill="x")
        ttk.Label(outrow, text="Save copies to:").pack(side="left")
        self.output_label = ttk.Label(outrow, text="Choose an output folder", foreground="#555")
        self.output_label.pack(side="left", padx=8, fill="x", expand=True)
        ttk.Button(outrow, text="Browse", command=self.choose_output).pack(side="right")
        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(fill="x", pady=(12, 5))
        self.status = ttk.Label(frame, text="Ready. Original MP3 files will not be overwritten.")
        self.status.pack(anchor="w")
        ttk.Button(frame, text="Embed artwork in MP3 copies", command=self.apply).pack(anchor="e", pady=(12, 0))

    def add_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        for p in paths:
            if p not in self.files:
                self.files.append(p); self.listbox.insert("end", Path(p).name)
        self.status.config(text=f"{len(self.files)} MP3 file(s) loaded.")

    def remove_selected(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i); del self.files[i]

    def clear(self):
        self.files.clear(); self.listbox.delete(0, "end")

    def choose_image(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if not p: return
        try:
            img = Image.open(p).convert("RGB"); img.thumbnail((210, 260))
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview.config(image=self.preview_photo, text="")
            self.image_path = p; self.image_name.config(text=Path(p).name)
        except Exception as e:
            messagebox.showerror("Image error", str(e))

    def choose_output(self):
        p = filedialog.askdirectory()
        if p:
            self.output_dir = p; self.output_label.config(text=p)

    def apply(self):
        if not self.files:
            messagebox.showwarning("Missing MP3", "Add at least one MP3 file."); return
        if not self.image_path:
            messagebox.showwarning("Missing image", "Choose a JPG or PNG cover."); return
        if not self.output_dir:
            messagebox.showwarning("Missing folder", "Choose an output folder."); return
        image_data = Path(self.image_path).read_bytes()
        mime = "image/png" if Path(self.image_path).suffix.lower() == ".png" else "image/jpeg"
        self.progress["maximum"] = len(self.files); self.progress["value"] = 0
        done, failed = [], []
        for n, src in enumerate(self.files, 1):
            try:
                dest = Path(self.output_dir) / Path(src).name
                dest.write_bytes(Path(src).read_bytes())  # preserve original
                try: tags = ID3(str(dest))
                except ID3NoHeaderError: tags = ID3()
                tags.delall("APIC")  # replace previous artwork, keep other tags
                tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=image_data))
                tags.save(str(dest), v2_version=3)
                done.append(dest.name)
            except Exception as e:
                failed.append(f"{Path(src).name}: {e}")
            self.progress["value"] = n
            self.status.config(text=f"Processed {n} of {len(self.files)}...")
            self.root.update_idletasks()
        msg = f"Updated {len(done)} MP3 file(s)."
        if failed: msg += "\n\nFailed:\n" + "\n".join(failed[:8])
        if failed: messagebox.showwarning("Finished with errors", msg)
        else: messagebox.showinfo("Finished", msg + f"\n\nSaved in:\n{self.output_dir}")
        self.status.config(text=msg.splitlines()[0])

if __name__ == "__main__":
    root = tk.Tk()
    AlbumArtStudio(root)
    root.mainloop()
