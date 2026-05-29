import os
import sys
import shutil
import urllib.request
import zipfile
import tempfile

# Добавляем родительский каталог в пути импорта для доступа к project_parser
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from project_parser import GodotConfigParser

JAM_COUNTDOWN_ZIP_MASTER = "https://github.com/AndresGamboaA/JamCountdown/archive/refs/heads/master.zip"
JAM_COUNTDOWN_ZIP_MAIN = "https://github.com/AndresGamboaA/JamCountdown/archive/refs/heads/main.zip"

def install_jam_countdown(project_path):
    print(f"[*] Начало установки плагина Game Jam Countdown в проект: {project_path}")
    
    addons_dir = os.path.join(project_path, "addons")
    target_plugin_dir = os.path.join(addons_dir, "jam_countdown")
    
    if os.path.exists(target_plugin_dir):
        print(f"[!] Плагин Game Jam Countdown уже установлен в {target_plugin_dir}. Пропускаем скачивание.")
        enable_plugin(project_path)
        return True

    os.makedirs(addons_dir, exist_ok=True)
    
    # Создаем временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "jam_countdown.zip")
        
        # Скачиваем ZIP-архив (пробуем master, затем main)
        print(f"[*] Скачивание Game Jam Countdown с GitHub...")
        success = False
        for url in [JAM_COUNTDOWN_ZIP_MASTER, JAM_COUNTDOWN_ZIP_MAIN]:
            try:
                print(f"[*] Попытка загрузки с {url}...")
                urllib.request.urlretrieve(url, zip_path)
                print("[+] Архив успешно скачан.")
                success = True
                break
            except Exception as e:
                print(f"[-] Ошибка при загрузке с {url}: {e}")
                
        if not success:
            print("[-] Ошибка: Не удалось скачать плагин Game Jam Countdown.")
            print("[!] Вы можете скачать его вручную из Godot Asset Library или GitHub:")
            print("    https://github.com/AndresGamboaA/JamCountdown")
            return False

        # Распаковываем архив
        print("[*] Распаковка архива...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            print("[+] Распаковка завершена.")
        except Exception as e:
            print(f"[-] Ошибка при распаковке архива: {e}")
            return False
        
        # Ищем распакованную папку
        extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d)) and 'JamCountdown' in d]
        if not extracted_dirs:
            print("[-] Ошибка: Не удалось найти распакованную папку плагина.")
            return False
            
        # Проверяем пути внутри архива
        source_plugin_dir = os.path.join(temp_dir, extracted_dirs[0], "addons", "jam_countdown")
        if not os.path.exists(source_plugin_dir):
            source_plugin_dir = os.path.join(temp_dir, extracted_dirs[0], "addons", "JamCountdown")
            
        if not os.path.exists(source_plugin_dir):
            # Если папка addons отсутствует, пробуем использовать весь корень распакованной папки
            source_plugin_dir = os.path.join(temp_dir, extracted_dirs[0])
            
        if not os.path.exists(source_plugin_dir):
            print("[-] Ошибка: Не удалось обнаружить файлы плагина в распакованном архиве.")
            return False
            
        # Копируем плагин в проект
        print(f"[*] Копирование плагина в {target_plugin_dir}...")
        try:
            shutil.copytree(source_plugin_dir, target_plugin_dir)
            print("[+] Плагин успешно скопирован.")
        except Exception as e:
            print(f"[-] Ошибка при копировании плагина: {e}")
            return False
            
    # Активируем плагин в project.godot
    return enable_plugin(project_path)

def enable_plugin(project_path):
    project_godot = os.path.join(project_path, "project.godot")
    if not os.path.exists(project_godot):
        print("[-] Ошибка: Файл project.godot не найден. Не удалось активировать плагин.")
        return False
        
    print("[*] Активация плагина Game Jam Countdown в project.godot...")
    try:
        parser = GodotConfigParser(project_godot)
        # Добавляем плагин в список включенных
        parser.merge_packed_array("editor_plugins", "enabled", ["res://addons/jam_countdown/plugin.cfg"])
        parser.write(project_godot)
        print("[+] Плагин Game Jam Countdown успешно активирован.")
        return True
    except Exception as e:
        print(f"[-] Ошибка при редактировании project.godot: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python jam_setup.py <путь_к_проекту>")
        sys.exit(1)
        
    project_dir = sys.argv[1]
    if install_jam_countdown(project_dir):
        print("[+] Установка Game Jam Countdown завершена успешно!")
    else:
        print("[-] Не удалось установить Game Jam Countdown.")
        sys.exit(1)
