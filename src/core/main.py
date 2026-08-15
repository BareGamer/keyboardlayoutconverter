import time
import win32clipboard
import win32con
import keyboard

# ====================== Таблицы раскладок ======================
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

# ====================== Работа с буфером ======================
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

# ====================== Основная логика ======================
def process_hotkey():
    # 1. Сохраняем текущий буфер
    old_clipboard = get_clipboard_text()

    # 2. Очищаем буфер, чтобы потом понять, сработал ли Ctrl+C
    clear_clipboard()
    time.sleep(0.03)

    # 3. Копируем выделенный текст
    keyboard.send('ctrl+c')

    # 4. Ждём, пока буфер изменится (максимум ~0.4 сек)
    new_text = None
    for _ in range(20):  # 20 * 20мс = 400мс
        time.sleep(0.02)
        new_text = get_clipboard_text()
        if new_text is not None and new_text != "":
            break

    # 5. Если ничего не скопировалось — восстанавливаем старый буфер и выходим
    if not new_text:
        if old_clipboard is not None:
            set_clipboard_text(old_clipboard)
        return

    # 6. Конвертируем
    converted = convert_layout(new_text)

    # 7. Кладём результат и вставляем
    if set_clipboard_text(converted):
        time.sleep(0.04)
        keyboard.send('ctrl+v')

        # 8. (Опционально) восстанавливаем старый буфер через небольшую паузу
        # Раскомментируйте, если хотите, чтобы после вставки в буфере оставался старый текст
        # time.sleep(0.15)
        # if old_clipboard is not None:
        #     set_clipboard_text(old_clipboard)

def main():
    print("Программа запущена.")
    print("Горячая клавиша: Ctrl + Shift + M")
    print("Выделите текст и нажмите комбинацию.")
    print("Для выхода нажмите Ctrl+C в консоли.\n")

    keyboard.add_hotkey('ctrl+shift+m', process_hotkey)
    keyboard.wait()

if __name__ == "__main__":
    main()