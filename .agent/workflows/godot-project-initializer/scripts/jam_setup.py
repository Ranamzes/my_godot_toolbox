import os
import sys
import shutil

# Добавляем родительский каталог в пути импорта для доступа к project_parser
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
from project_parser import GodotConfigParser

TEMPLATES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "templates")
LOCAL_JAM_PLUGIN_SRC = os.path.join(TEMPLATES_DIR, "jam", "addons", "jam_countdown")

def install_jam_countdown(project_path):
    print(f"[*] Начало установки улучшенного плагина Game Jam Countdown (v1.2.2) в проект: {project_path}")
    
    addons_dir = os.path.join(project_path, "addons")
    target_plugin_dir = os.path.join(addons_dir, "jam_countdown")
    
    if os.path.exists(target_plugin_dir):
        print(f"[!] Плагин Game Jam Countdown уже установлен в {target_plugin_dir}. Пропускаем копирование.")
        enable_plugin(project_path)
        return True

    if not os.path.exists(LOCAL_JAM_PLUGIN_SRC):
        print(f"[-] Ошибка: Локальный шаблон плагина не найден по пути: {LOCAL_JAM_PLUGIN_SRC}")
        return False

    os.makedirs(addons_dir, exist_ok=True)
    
    # Копируем плагин из локального шаблона
    print(f"[*] Копирование улучшенной версии плагина из шаблонов скилла...")
    try:
        shutil.copytree(LOCAL_JAM_PLUGIN_SRC, target_plugin_dir)
        print("[+] Плагин успешно скопирован в проект: res://addons/jam_countdown")
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
