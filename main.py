# main.py
# This script allows the user to choose which script to run.
import json
import locale
import os
import platform
import re
import shutil
import sys

from colorama import Fore, Style, init
from config import force_update_config, get_config
from logo import print_logo
from new_signup import get_user_documents_path

# Only import windll on Windows systems
if platform.system() == "Windows":
    import ctypes
    # Only import windll on Windows systems

# Initialize colorama
init()

# Define emoji and color constants
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
    "MENU": "📋",
    "ARROW": "➜",
    "LANG": "🌐",
    "UPDATE": "🔄",
    "ADMIN": "🔐",
    "AIRDROP": "💰",
    "ROCKET": "🚀",
    "STAR": "⭐",
    "SUN": "🌟",
    "CONTRIBUTE": "🤝",
    "SETTINGS": "⚙️",
    "WARNING": "⚠️",
    "NEW": "🆕",
    "MAGIC": "✨",
    "USER": "👤",
    "LIGHTNING": "⚡",  # Added lightning emoji for performance enhancements
}


# Function to check if running as frozen executable
def is_frozen():
    """Check if the script is running as a frozen executable."""
    return getattr(sys, "frozen", False)


# Function to check admin privileges (Windows only)
def is_admin():
    """Check if the script is running with admin privileges (Windows only)."""
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    # Always return True for non-Windows to avoid changing behavior
    return True


# Function to restart with admin privileges
def run_as_admin():
    """Restart the current script with admin privileges (Windows only)."""
    if platform.system() != "Windows":
        return False

    try:
        args = [sys.executable] + sys.argv

        # Request elevation via ShellExecute
        print(
            f"{Fore.YELLOW}{EMOJI['ADMIN']} Requesting administrator privileges...{Style.RESET_ALL}"
        )
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            args[0],
            " ".join('"' + arg + '"' for arg in args[1:]),
            None,
            1,
        )
        return True
    except Exception as e:
        print(
            f"{Fore.RED}{EMOJI['ERROR']} Failed to restart with admin privileges: {e}{Style.RESET_ALL}"
        )
        return False


class Translator:
    def __init__(self):
        self.translations = {}
        self.current_language = self.detect_system_language()  # Use correct method name
        self.fallback_language = "en"  # Fallback language if translation is missing
        self.load_translations()

    def detect_system_language(self):
        """Detect system language and return corresponding language code"""
        try:
            system = platform.system()

            if system == "Windows":
                return self._detect_windows_language()
            else:
                return self._detect_unix_language()

        except Exception as e:
            print(
                f"{Fore.YELLOW}{EMOJI['INFO']} Failed to detect system language: {e}{Style.RESET_ALL}"
            )
            return "en"

    def _detect_windows_language(self):
        """Detect language on Windows systems"""
        try:
            # Ensure we are on Windows
            if platform.system() != "Windows":
                return "en"

            # Get keyboard layout
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            threadid = user32.GetWindowThreadProcessId(hwnd, 0)
            layout_id = user32.GetKeyboardLayout(threadid) & 0xFFFF

            # Map language ID to our language codes
            language_map = {
                0x0409: "en",  # English
                0x0404: "zh_tw",  # Traditional Chinese
                0x0804: "zh_cn",  # Simplified Chinese
                0x0422: "vi",  # Vietnamese
                0x0419: "ru",  # Russian
                0x0415: "tr",  # Turkish
                0x0402: "bg",  # Bulgarian
            }

            return language_map.get(layout_id, "en")
        except:
            return self._detect_unix_language()

    def _detect_unix_language(self):
        """Detect language on Unix-like systems (Linux, macOS)"""
        try:
            # Get the system locale
            system_locale = locale.getdefaultlocale()[0]
            if not system_locale:
                return "en"

            system_locale = system_locale.lower()

            # Map locale to our language codes
            if system_locale.startswith("zh_tw") or system_locale.startswith("zh_hk"):
                return "zh_tw"
            elif system_locale.startswith("zh_cn"):
                return "zh_cn"
            elif system_locale.startswith("en"):
                return "en"
            elif system_locale.startswith("vi"):
                return "vi"
            elif system_locale.startswith("nl"):
                return "nl"
            elif system_locale.startswith("de"):
                return "de"
            elif system_locale.startswith("fr"):
                return "fr"
            elif system_locale.startswith("pt"):
                return "pt"
            elif system_locale.startswith("ru"):
                return "ru"
            elif system_locale.startswith("tr"):
                return "tr"
            elif system_locale.startswith("bg"):
                return "bg"
            # Try to get language from LANG environment variable as fallback
            env_lang = os.getenv("LANG", "").lower()
            if "tw" in env_lang or "hk" in env_lang:
                return "zh_tw"
            elif "cn" in env_lang:
                return "zh_cn"
            elif "vi" in env_lang:
                return "vi"
            elif "nl" in env_lang:
                return "nl"
            elif "de" in env_lang:
                return "de"
            elif "fr" in env_lang:
                return "fr"
            elif "pt" in env_lang:
                return "pt"
            elif "ru" in env_lang:
                return "ru"
            elif "tr" in env_lang:
                return "tr"
            elif "bg" in env_lang:
                return "bg"

            return "en"
        except:
            return "en"

    def load_translations(self):
        """Load all available translations"""
        try:
            locales_dir = os.path.join(os.path.dirname(__file__), "locales")
            if hasattr(sys, "_MEIPASS"):
                locales_dir = os.path.join(sys._MEIPASS, "locales")

            if not os.path.exists(locales_dir):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} Locales directory not found{Style.RESET_ALL}"
                )
                return

            for file in os.listdir(locales_dir):
                if file.endswith(".json"):
                    lang_code = file[:-5]  # Remove .json
                    try:
                        with open(
                            os.path.join(locales_dir, file), "r", encoding="utf-8"
                        ) as f:
                            self.translations[lang_code] = json.load(f)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(
                            f"{Fore.RED}{EMOJI['ERROR']} Error loading {file}: {e}{Style.RESET_ALL}"
                        )
                        continue
        except Exception as e:
            print(
                f"{Fore.RED}{EMOJI['ERROR']} Failed to load translations: {e}{Style.RESET_ALL}"
            )

    def get(self, key, **kwargs):
        """Get translated text with fallback support"""
        try:
            # Try current language
            result = self._get_translation(self.current_language, key)
            if result == key and self.current_language != self.fallback_language:
                # Try fallback language if translation not found
                result = self._get_translation(self.fallback_language, key)
            return result.format(**kwargs) if kwargs else result
        except Exception:
            return key

    def _get_translation(self, lang_code, key):
        """Get translation for a specific language"""
        try:
            keys = key.split(".")
            value = self.translations.get(lang_code, {})
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k, key)
                else:
                    return key
            return value
        except Exception:
            return key

    def set_language(self, lang_code):
        """Set current language with validation"""
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False

    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.translations.keys())


# Create translator instance
translator = Translator()


def print_menu():
    """Print menu options"""
    try:
        config = get_config()
        if config.getboolean("Utils", "enabled_account_info"):
            import cursor_acc_info

            cursor_acc_info.display_account_info(translator)
    except Exception as e:
        print(
            f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.account_info_error', error=str(e))}{Style.RESET_ALL}"
        )

    print(
        f"\n{Fore.CYAN}{EMOJI['MENU']} {translator.get('menu.title')}:{Style.RESET_ALL}"
    )
    if translator.current_language == "zh_cn" or translator.current_language == "zh_tw":
        print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{'─' * 110}{Style.RESET_ALL}")

    # Get terminal width
    try:
        terminal_width = shutil.get_terminal_size().columns
    except:
        terminal_width = 80  # Default width

    # Define all menu items
    menu_items = {
        0: f"{Fore.GREEN}0{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.exit')}",
        1: f"{Fore.GREEN}1{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.reset')}",
        2: f"{Fore.GREEN}2{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register')} ({Fore.RED}{translator.get('menu.outdate')}{Style.RESET_ALL})",
        3: f"{Fore.GREEN}3{Style.RESET_ALL}. {EMOJI['SUN']} {translator.get('menu.register_google')} {EMOJI['ROCKET']} ({Fore.YELLOW}{translator.get('menu.lifetime_access_enabled')}{Style.RESET_ALL})",
        4: f"{Fore.GREEN}4{Style.RESET_ALL}. {EMOJI['STAR']} {translator.get('menu.register_github')} {EMOJI['ROCKET']} ({Fore.YELLOW}{translator.get('menu.lifetime_access_enabled')}{Style.RESET_ALL})",
        5: f"{Fore.GREEN}5{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register_manual')}",
        6: f"{Fore.GREEN}6{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.temp_github_register')}",
        7: f"{Fore.GREEN}7{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.quit')}",
        8: f"{Fore.GREEN}8{Style.RESET_ALL}. {EMOJI['LANG']} {translator.get('menu.select_language')}",
        9: f"{Fore.GREEN}9{Style.RESET_ALL}. {EMOJI['UPDATE']} {translator.get('menu.disable_auto_update')}",
        10: f"{Fore.GREEN}10{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.totally_reset')}",
        11: f"{Fore.GREEN}11{Style.RESET_ALL}. {EMOJI['CONTRIBUTE']} {translator.get('menu.contribute')}",
        12: f"{Fore.GREEN}12{Style.RESET_ALL}. {EMOJI['SETTINGS']}  {translator.get('menu.config')}",
        13: f"{Fore.GREEN}13{Style.RESET_ALL}. {EMOJI['SETTINGS']}  {translator.get('menu.select_chrome_profile')}",
        14: f"{Fore.GREEN}14{Style.RESET_ALL}. {EMOJI['ERROR']}  {translator.get('menu.delete_google_account', fallback='Delete Cursor Google Account')}",
        15: f"{Fore.GREEN}15{Style.RESET_ALL}. {EMOJI['UPDATE']}  {translator.get('menu.bypass_version_check', fallback='Bypass Cursor Version Check')}",
        16: f"{Fore.GREEN}16{Style.RESET_ALL}. {EMOJI['UPDATE']}  {translator.get('menu.check_user_authorized', fallback='Check User Authorized')}",
        17: f"{Fore.GREEN}17{Style.RESET_ALL}. {EMOJI['UPDATE']}  {translator.get('menu.bypass_token_limit', fallback='Bypass Token Limit')}",
    }

    # Automatically calculate the number of menu items in the left and right columns
    total_items = len(menu_items)
    left_column_count = (
        total_items + 1
    ) // 2  # The number of options displayed on the left (rounded up)

    # Build left and right columns of menus
    sorted_indices = sorted(menu_items.keys())
    left_menu = [menu_items[i] for i in sorted_indices[:left_column_count]]
    right_menu = [menu_items[i] for i in sorted_indices[left_column_count:]]

    # Calculate the maximum display width of left menu items
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def get_display_width(s):
        """Calculate the display width of a string, considering Chinese characters and emojis"""
        # Remove ANSI color codes
        clean_s = ansi_escape.sub("", s)
        width = 0
        for c in clean_s:
            # Chinese characters and some emojis occupy two character widths
            if ord(c) > 127:
                width += 2
            else:
                width += 1
        return width

    max_left_width = 0
    for item in left_menu:
        width = get_display_width(item)
        max_left_width = max(max_left_width, width)

    # Set the starting position of right menu
    fixed_spacing = 4  # Fixed spacing
    right_start = max_left_width + fixed_spacing

    # Calculate the number of spaces needed for right menu items
    spaces_list = []
    for i in range(len(left_menu)):
        if i < len(left_menu):
            left_item = left_menu[i]
            left_width = get_display_width(left_item)
            spaces = right_start - left_width
            spaces_list.append(spaces)

    # Print menu items
    max_rows = max(len(left_menu), len(right_menu))

    for i in range(max_rows):
        # Print left menu items
        if i < len(left_menu):
            left_item = left_menu[i]
            print(left_item, end="")

            # Use pre-calculated spaces
            spaces = spaces_list[i]
        else:
            # If left side has no items, print only spaces
            spaces = right_start
            print("", end="")

        # Print right menu items
        if i < len(right_menu):
            print(" " * spaces + right_menu[i])
        else:
            print()  # Change line
    if translator.current_language == "zh_cn" or translator.current_language == "zh_tw":
        print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{'─' * 110}{Style.RESET_ALL}")


def select_language():
    """Language selection menu"""
    print(
        f"\n{Fore.CYAN}{EMOJI['LANG']} {translator.get('menu.select_language')}:{Style.RESET_ALL}"
    )
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")

    languages = translator.get_available_languages()
    for i, lang in enumerate(languages):
        lang_name = translator.get(f"languages.{lang}")
        print(f"{Fore.GREEN}{i}{Style.RESET_ALL}. {lang_name}")

    try:
        choice = input(
            f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices=f'0-{len(languages) - 1}')}: {Style.RESET_ALL}"
        )
        if choice.isdigit() and 0 <= int(choice) < len(languages):
            translator.set_language(languages[int(choice)])
            return True
        else:
            print(
                f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}"
            )
            return False
    except (ValueError, IndexError):
        print(
            f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}"
        )
        return False


def check_latest_version():
    """Check if current version matches the latest release version - Disabled"""
    # Version check disabled for security reasons
    print(
        f"\n{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('updater.up_to_date', fallback='Version check disabled, using local version only.')}{Style.RESET_ALL}"
    )
    return True


def main():
    # Check for admin privileges if running as executable on Windows only
    if platform.system() == "Windows" and is_frozen() and not is_admin():
        print(
            f"{Fore.YELLOW}{EMOJI['ADMIN']} {translator.get('menu.admin_required')}{Style.RESET_ALL}"
        )
        if run_as_admin():
            sys.exit(0)  # Exit after requesting admin privileges
        else:
            print(
                f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.admin_required_continue')}{Style.RESET_ALL}"
            )

    print_logo()

    # Initialize configuration
    config = get_config(translator)
    if not config:
        print(
            f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.config_init_failed')}{Style.RESET_ALL}"
        )
        return
    force_update_config(translator)

    # Always disable update check
    if config.has_section("Utils") and "enabled_update_check" in config["Utils"]:
        config.set("Utils", "enabled_update_check", "False")
        config_dir = os.path.join(get_user_documents_path(), ".cursor-free-vip")
        config_file = os.path.join(config_dir, "config.ini")
        with open(config_file, "w") as configfile:
            config.write(configfile)

    # Print menu without version check
    print_menu()

    while True:
        try:
            choice_num = 17
            choice = input(
                f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices=f'0-{choice_num}')}: {Style.RESET_ALL}"
            )

            if choice == "0":
                print(
                    f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.exit')}...{Style.RESET_ALL}"
                )
                print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
                return
            elif choice == "1":
                import reset_machine_manual

                reset_machine_manual.run(translator)
                print_menu()
            elif choice == "2":
                import cursor_register

                cursor_register.main(translator)
                print_menu()
            elif choice == "3":
                import cursor_register_google

                cursor_register_google.main(translator)
                print_menu()
            elif choice == "4":
                import cursor_register_github

                cursor_register_github.main(translator)
                print_menu()
            elif choice == "5":
                import cursor_register_manual

                cursor_register_manual.main(translator)
                print_menu()
            elif choice == "6":
                print(
                    f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.coming_soon')}{Style.RESET_ALL}"
                )
                # github_cursor_register.main(translator)
                print_menu()
            elif choice == "7":
                import quit_cursor

                quit_cursor.quit_cursor(translator)
                print_menu()
            elif choice == "8":
                if select_language():
                    print_menu()
                continue
            elif choice == "9":
                import disable_auto_update

                disable_auto_update.run(translator)
                print_menu()
            elif choice == "10":
                import totally_reset_cursor

                totally_reset_cursor.run(translator)
                # print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.fixed_soon')}{Style.RESET_ALL}")
                print_menu()
            elif choice == "11":
                import logo

                print(logo.CURSOR_CONTRIBUTORS)
                print_menu()
            elif choice == "12":
                from config import print_config

                print_config(get_config(), translator)
                print_menu()
            elif choice == "13":
                from oauth_auth import OAuthHandler

                oauth = OAuthHandler(translator)
                oauth._select_profile()
                print_menu()
            elif choice == "14":
                import delete_cursor_google

                delete_cursor_google.main(translator)
                print_menu()
            elif choice == "15":
                import bypass_version

                bypass_version.main(translator)
                print_menu()
            elif choice == "16":
                import check_user_authorized

                check_user_authorized.main(translator)
                print_menu()
            elif choice == "17":
                import bypass_token_limit

                bypass_token_limit.run(translator)
                print_menu()
            else:
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}"
                )
                print_menu()

        except KeyboardInterrupt:
            print(
                f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.program_terminated')}{Style.RESET_ALL}"
            )
            print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
            return
        except Exception as e:
            print(
                f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.error_occurred', error=str(e))}{Style.RESET_ALL}"
            )
            print_menu()


if __name__ == "__main__":
    main()
