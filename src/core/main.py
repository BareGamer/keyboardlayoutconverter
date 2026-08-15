import time
import threading

import win32clipboard
import win32con
import keyboard
import pystray

from PIL import Image, ImageDraw


# ====================== Character map ======================
en_to_ru = {
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е',
    'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
    '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в',
    'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
    'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч',
    'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
    ',': 'б', '.': 'ю', '/': '.',
    'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е',
    'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
    '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы', 'D': 'В',
    'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
    'L': 'Д', ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч',
    'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т', 'M': 'Ь',
    '<': 'Б', '>': 'Ю', '?': ','
}

ru_to_en = {v: k for k, v in en_to_ru.items()}


def convert_layout(text: str) -> str:
    if not text:
        return text
    has_russian = any(('а' <= c.lower() <= 'я') or c in 'ёЁ' for c in text)
    table = ru_to_en if has_russian else en_to_ru
    return ''.join(table.get(c, c) for c in text)


# ====================== working with the clipboard buffer ======================
def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data
    except:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        return None


def set_clipboard_text(text: str) -> bool:
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
        return True
    except:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        return False


def clear_clipboard():
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()
    except:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass


def process_hotkey():
    old_clipboard = get_clipboard_text()

    # 2. Очищаем буфер, чтобы потом понять, сработал ли Ctrl+C
    clear_clipboard()
    time.sleep(0.03)

    # copying the selected text
    keyboard.send('ctrl+c')

    # waiting for the buffer to update (~0.4s)
    new_text = None
    for _ in range(20):  # 20 * 20ms = 400ms
        time.sleep(0.02)
        new_text = get_clipboard_text()
        if new_text is not None and new_text != "":
            break

    # if copying was unsuccessful, restore the old buffer
    if not new_text:
        if old_clipboard is not None:
            set_clipboard_text(old_clipboard)
        return

    converted = convert_layout(new_text)

    # trying to insert new text into the buffer
    if set_clipboard_text(converted):
        time.sleep(0.04)
        keyboard.send('ctrl+v')


# ====================== System tray ======================

enabled = True


def toggle_enabled(icon, item):
    global enabled
    enabled = not enabled
    icon.menu = create_menu()


def quit_application(icon, item):
    keyboard.unhook_all_hotkeys()
    icon.stop()


def create_icon_image():
    image = Image.new('RGB', (64, 64), 'white')
    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (4, 4, 60, 60),
        outline='black',
        width=3
    )

    draw.text(
        (16, 20),
        'RU',
        fill='black'
    )

    return image


def create_menu():
    return pystray.Menu(
        pystray.MenuItem(
            'Enabled',
            toggle_enabled,
            checked=lambda item: enabled
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            'Hotkey: Ctrl + Shift + M',
            lambda icon, item: None,
            enabled=False
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            'Exit',
            quit_application
        )
    )


def main():
    print("Program running.")
    print("Hotkey: Ctrl + Shift + M")
    print("Select the text and press the hotkey to run the program.")
    print("To exit press Ctrl+C in the console.\n")

    keyboard.add_hotkey('ctrl+shift+m', process_hotkey)

    icon = pystray.Icon(
        'KeyboardLayoutConverter',
        create_icon_image(),
        'Keyboard Layout Converter',
        menu=create_menu()
    )

    icon.run()


if __name__ == "__main__":
    main()