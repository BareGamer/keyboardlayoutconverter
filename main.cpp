#include <windows.h>
#include <string>
#include <map>
#include <cctype>
#include <iostream>

// ====================== Таблицы раскладок ======================
std::map<wchar_t, wchar_t> en_to_ru = {
    {L'q', L'й'}, {L'w', L'ц'}, {L'e', L'у'}, {L'r', L'к'}, {L't', L'е'},
    {L'y', L'н'}, {L'u', L'г'}, {L'i', L'ш'}, {L'o', L'щ'}, {L'p', L'з'},
    {L'[', L'х'}, {L']', L'ъ'}, {L'a', L'ф'}, {L's', L'ы'}, {L'd', L'в'},
    {L'f', L'а'}, {L'g', L'п'}, {L'h', L'р'}, {L'j', L'о'}, {L'k', L'л'},
    {L'l', L'д'}, {L';', L'ж'}, {L'\'', L'э'}, {L'z', L'я'}, {L'x', L'ч'},
    {L'c', L'с'}, {L'v', L'м'}, {L'b', L'и'}, {L'n', L'т'}, {L'm', L'ь'},
    {L',', L'б'}, {L'.', L'ю'}, {L'/', L'.'},
    // Заглавные
    {L'Q', L'Й'}, {L'W', L'Ц'}, {L'E', L'У'}, {L'R', L'К'}, {L'T', L'Е'},
    {L'Y', L'Н'}, {L'U', L'Г'}, {L'I', L'Ш'}, {L'O', L'Щ'}, {L'P', L'З'},
    {L'{', L'Х'}, {L'}', L'Ъ'}, {L'A', L'Ф'}, {L'S', L'Ы'}, {L'D', L'В'},
    {L'F', L'А'}, {L'G', L'П'}, {L'H', L'Р'}, {L'J', L'О'}, {L'K', L'Л'},
    {L'L', L'Д'}, {L':', L'Ж'}, {L'"', L'Э'}, {L'Z', L'Я'}, {L'X', L'Ч'},
    {L'C', L'С'}, {L'V', L'М'}, {L'B', L'И'}, {L'N', L'Т'}, {L'M', L'Ь'},
    {L'<', L'Б'}, {L'>', L'Ю'}, {L'?', L','}
};

std::map<wchar_t, wchar_t> ru_to_en;

// Обратная таблица
void init_reverse_map() {
    for (const auto& p : en_to_ru) {
        ru_to_en[p.second] = p.first;
    }
}

// ====================== Конвертация ======================
std::wstring convert_layout(const std::wstring& text) {
    if (text.empty()) return text;

    // Простое определение раскладки: если есть русские буквы — считаем, что текст набран в русской
    bool has_russian = false;
    for (wchar_t c : text) {
        if ((c >= L'а' && c <= L'я') || (c >= L'А' && c <= L'Я') || c == L'ё' || c == L'Ё') {
            has_russian = true;
            break;
        }
    }

    std::wstring result;
    result.reserve(text.size());

    if (has_russian) {
        // Русский → Английский
        for (wchar_t c : text) {
            auto it = ru_to_en.find(c);
            result += (it != ru_to_en.end()) ? it->second : c;
        }
    } else {
        // Английский → Русский
        for (wchar_t c : text) {
            auto it = en_to_ru.find(c);
            result += (it != en_to_ru.end()) ? it->second : c;
        }
    }

    return result;
}

// ====================== Работа с буфером обмена ======================
std::wstring get_clipboard_text() {
    if (!OpenClipboard(nullptr)) return L"";

    HANDLE hData = GetClipboardData(CF_UNICODETEXT);
    if (!hData) {
        CloseClipboard();
        return L"";
    }

    wchar_t* pszText = static_cast<wchar_t*>(GlobalLock(hData));
    if (!pszText) {
        CloseClipboard();
        return L"";
    }

    std::wstring text(pszText);
    GlobalUnlock(hData);
    CloseClipboard();
    return text;
}

bool set_clipboard_text(const std::wstring& text) {
    if (!OpenClipboard(nullptr)) return false;
    EmptyClipboard();

    size_t size = (text.size() + 1) * sizeof(wchar_t);
    HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, size);
    if (!hMem) {
        CloseClipboard();
        return false;
    }

    wchar_t* pMem = static_cast<wchar_t*>(GlobalLock(hMem));
    memcpy(pMem, text.c_str(), size);
    GlobalUnlock(hMem);

    SetClipboardData(CF_UNICODETEXT, hMem);
    CloseClipboard();
    return true;
}

// ====================== Симуляция нажатий ======================
void send_ctrl_key(WORD vk) {
    // Нажать Ctrl
    keybd_event(VK_CONTROL, 0, 0, 0);
    // Нажать нужную клавишу
    keybd_event(vk, 0, 0, 0);
    // Отпустить клавишу
    keybd_event(vk, 0, KEYEVENTF_KEYUP, 0);
    // Отпустить Ctrl
    keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0);
}

// ====================== Основная логика ======================
void process_hotkey() {
    // 1. Копируем выделенный текст
    send_ctrl_key('C');
    Sleep(50); // Небольшая пауза, чтобы приложение успело положить текст в буфер

    // 2. Читаем буфер
    std::wstring original = get_clipboard_text();
    if (original.empty()) return;

    // 3. Конвертируем
    std::wstring converted = convert_layout(original);

    // 4. Кладём результат обратно
    if (!set_clipboard_text(converted)) return;

    Sleep(30);

    // 5. Вставляем
    send_ctrl_key('V');
}

// ====================== Точка входа ======================
int main() {
    init_reverse_map();

    // Регистрируем горячую клавишу: Ctrl + Shift + Z
    // MOD_CONTROL | MOD_SHIFT, 'Z'
    if (!RegisterHotKey(nullptr, 1, MOD_CONTROL | MOD_SHIFT, 'Z')) {
        std::wcout << L"Не удалось зарегистрировать горячую клавишу.\n";
        return 1;
    }

    std::wcout << L"Программа запущена.\n";
    std::wcout << L"Горячая клавиша: Ctrl + Shift + Z\n";
    std::wcout << L"Выделите текст и нажмите комбинацию.\n";
    std::wcout << L"Для выхода закройте это окно.\n";

    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        if (msg.message == WM_HOTKEY) {
            process_hotkey();
        }
    }

    UnregisterHotKey(nullptr, 1);
    return 0;
}