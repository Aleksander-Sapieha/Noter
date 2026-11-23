from tkinter import *
from tkinter import filedialog, messagebox
import os
import json

root = Tk()
root.geometry("800x600")
root.title("Sticky Notes")
root.minsize(width=350, height=250)

# Variables
current_file = None

# --- FUNCTIONS ---

def save_note():
    global current_file

    if current_file is None:
        current_file = filedialog.asksaveasfilename(
            defaultextension=".note",
            filetypes=[("Sticky Notes files", "*.note")]
        )

    if not current_file:
        return

    content = text_info.get("1.0", "end-1c")

    formatting = []

    for tag in ("bold", "italic", "underline"):
        ranges = text_info.tag_ranges(tag)

        for i in range(0, len(ranges), 2):
            start = ranges[i]
            end = ranges[i + 1]

            formatting.append({
                "tag": tag,
                "start": str(start),
                "end": str(end)
            })

    data = {
        "version": 1,
        "content": content,
        "formatting": formatting
    }

    with open(current_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    root.title(f"Sticky Notes - {os.path.basename(current_file)}")


def open_note():
    global current_file

    path = filedialog.askopenfilename(
        filetypes=[("Sticky Notes files", "*.note")]
    )

    if not path:
        return

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if data.get("version") != 1:
            raise ValueError("Unsupported note version")

        content = data["content"]
        formatting = data["formatting"]

        text_info.delete("1.0", END)
        text_info.insert("1.0", content)

        for item in formatting:
            tag = item["tag"]

            if tag not in ("bold", "italic", "underline"):
                continue

            text_info.tag_add(
                tag,
                item["start"],
                item["end"]
            )

        current_file = path
        root.title(f"Sticky Notes - {os.path.basename(path)}")

    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        messagebox.showerror("Error", f"Could not open note:\n{error}")


def new_note():
    global current_file

    text_info.delete("1.0", END)
    current_file = None
    root.title("Sticky Notes - Untitled")


def update_counter(event=None):
    content = text_info.get("1.0", "end-1c")
    words = len(content.split())
    characters = len(content)

    counter.config(
        text=f"Words: {words} | Characters: {characters}"
    )

def apply_format(tag):
    try:
        start = text_info.index("sel.first")
        end = text_info.index("sel.last")

        existing = text_info.tag_names(start)

        if tag in existing:
            text_info.tag_remove(tag, start, end)
        else:
            text_info.tag_add(tag, start, end)

    except TclError:
        pass


def bold():
    apply_format("bold")


def italic():
    apply_format("italic")


def underline():
    apply_format("underline")

# --- MENU ---

menu = Menu(root)
root.config(menu=menu)

file_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)

file_menu.add_command(label="New", command=new_note)
file_menu.add_command(label="Open", command=open_note)
file_menu.add_command(label="Save", command=save_note)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)


# --- EDITOR ---

toolbar = Frame(root)
toolbar.pack(fill=X)

Button(toolbar, text="B", font=("Arial", 10, "bold"),
       command=bold).pack(side=LEFT)

Button(toolbar, text="I", font=("Arial", 10, "italic"),
       command=italic).pack(side=LEFT)

Button(toolbar, text="U", font=("Arial", 10, "underline"),
       command=underline).pack(side=LEFT)

editor_frame = Frame(root)
editor_frame.pack(fill=BOTH, expand=True)

scrollbar = Scrollbar(editor_frame)
scrollbar.pack(side=RIGHT, fill=Y)

text_info = Text(
    editor_frame,
    wrap=WORD,
    undo=True,
    yscrollcommand=scrollbar.set,
    font=("Arial", 12)
)

text_info.pack(fill=BOTH, expand=True)

text_info.tag_configure(
    "bold",
    font=("Arial", 12, "bold")
)

text_info.tag_configure(
    "italic",
    font=("Arial", 12, "italic")
)

text_info.tag_configure(
    "underline",
    underline=True
)

scrollbar.config(command=text_info.yview)

# --- STATUS BAR ---

counter = Label(root, text="Words: 0 | Characters: 0", anchor=W)
counter.pack(fill=X)

if __name__ == "__main__":
    text_info.bind("<KeyRelease>", update_counter)
    root.mainloop()
