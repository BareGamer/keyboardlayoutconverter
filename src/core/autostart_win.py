import os
import sys
import winreg


APP_NAME = "KeyboardLayoutConverter"

RUN_KEY = (
    r"Software\Microsoft\Windows\CurrentVersion\Run"
)


def get_main_exe_path() -> str:
    """
    Определяет путь к main.exe.

    При обычном запуске Python:
        рядом с этим модулем ожидается main.exe.

    При запуске frozen/autostart.exe:
        main.exe также ожидается рядом с autostart.exe.
    """

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(
            os.path.abspath(sys.executable)
        )
    else:
        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_dir,
        'main.exe',
    )


def get_autostart_value():
    """
    Возвращает текущий путь из реестра или None.
    """

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_READ,
        ) as key:

            value, _ = winreg.QueryValueEx(
                key,
                APP_NAME,
            )

            return value

    except FileNotFoundError:
        return None

    except OSError as error:
        print(
            f"[Autostart] Read error: {error}"
        )

        return None


def enable_autostart(
    exe_path: str | None = None,
) -> bool:
    """
    Добавляет main.exe в автозапуск текущего пользователя.
    """

    if exe_path is None:
        exe_path = get_main_exe_path()

    exe_path = os.path.abspath(exe_path)

    if not os.path.isfile(exe_path):
        print(
            f"[Autostart] EXE not found: {exe_path}"
        )

        return False

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:

            winreg.SetValueEx(
                key,
                APP_NAME,
                0,
                winreg.REG_SZ,
                f'"{exe_path}"',
            )

        return True

    except OSError as error:
        print(
            f"[Autostart] Enable error: {error}"
        )

        return False


def disable_autostart() -> bool:
    """
    Удаляет приложение из автозапуска.
    """

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:

            try:
                winreg.DeleteValue(
                    key,
                    APP_NAME,
                )

            except FileNotFoundError:
                pass

        return True

    except OSError as error:
        print(
            f"[Autostart] Disable error: {error}"
        )

        return False


def is_autostart_enabled() -> bool:
    """
    Проверяет, включён ли автозапуск.
    """

    value = get_autostart_value()

    if not value:
        return False

    expected = os.path.normcase(
        os.path.abspath(
            get_main_exe_path()
        )
    )

    # Убираем кавычки вокруг пути.
    actual = value.strip().strip('"')

    try:
        actual = os.path.normcase(
            os.path.abspath(actual)
        )
    except Exception:
        return False

    return actual == expected


def print_status():
    """
    Выводит состояние автозапуска в консоль.
    """

    enabled = is_autostart_enabled()

    if enabled:
        print("Autostart: ENABLED")
    else:
        print("Autostart: DISABLED")

    current_value = get_autostart_value()

    if current_value:
        print(f"Registry value: {current_value}")


def main():
    """
    Консольный интерфейс для управления автозапуском.

    Команды:

        autostart.exe on
        autostart.exe off
        autostart.exe status
        autostart.exe toggle
    """

    args = sys.argv[1:]

    if not args:
        print("Keyboard Layout Converter - Autostart")
        print()
        print("Usage:")
        print("  autostart.exe on")
        print("  autostart.exe off")
        print("  autostart.exe status")
        print("  autostart.exe toggle")
        print()

        print_status()
        return

    command = args[0].lower()

    if command == 'on':
        if enable_autostart():
            print("Autostart enabled.")
        else:
            print("Failed to enable autostart.")

        return

    if command == 'off':
        if disable_autostart():
            print("Autostart disabled.")
        else:
            print("Failed to disable autostart.")

        return

    if command == 'status':
        print_status()
        return

    if command == 'toggle':
        if is_autostart_enabled():
            success = disable_autostart()
            print(
                "Autostart disabled."
                if success
                else "Failed to disable autostart."
            )
        else:
            success = enable_autostart()
            print(
                "Autostart enabled."
                if success
                else "Failed to enable autostart."
            )

        return

    print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()