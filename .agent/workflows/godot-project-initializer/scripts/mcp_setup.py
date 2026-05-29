import os
import sys
import shutil
import urllib.request
import zipfile
import tempfile

# Добавляем родительский каталог в пути импорта, чтобы использовать project_parser
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from project_parser import GodotConfigParser

MCP_REPO_ZIP = "https://github.com/ee0pdt/Godot-MCP/archive/refs/heads/main.zip"

def install_godot_mcp(project_path):
    print(f"[*] Начало установки Godot-MCP в проект: {project_path}")
    
    addons_dir = os.path.join(project_path, "addons")
    target_plugin_dir = os.path.join(addons_dir, "godot_mcp")
    
    if os.path.exists(target_plugin_dir):
        print(f"[!] Плагин Godot-MCP уже установлен в {target_plugin_dir}. Пропускаем скачивание.")
        enable_plugin(project_path)
        return True

    os.makedirs(addons_dir, exist_ok=True)
    
    # Создаем временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "godot_mcp.zip")
        
        # Скачиваем ZIP-архив
        print(f"[*] Скачивание Godot-MCP с GitHub...")
        try:
            urllib.request.urlretrieve(MCP_REPO_ZIP, zip_path)
            print("[+] Архив успешно скачан.")
        except Exception as e:
            print(f"[-] Ошибка при скачивании плагина: {e}")
            print("[!] Пожалуйста, скачайте плагин вручную с https://github.com/ee0pdt/Godot-MCP")
            print("    и распакуйте папку 'addons/godot_mcp' в директорию вашего проекта 'addons/'.")
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
        
        # Ищем распакованную папку. Обычно имя 'Godot-MCP-main'
        extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d)) and 'Godot-MCP' in d]
        if not extracted_dirs:
            print("[-] Ошибка: Не удалось найти распакованную папку плагина.")
            return False
            
        source_plugin_dir = os.path.join(temp_dir, extracted_dirs[0], "addons", "godot_mcp")
        if not os.path.exists(source_plugin_dir):
            # Пробуем поискать в корне или другую структуру
            print("[-] Ошибка: В архиве отсутствует папка addons/godot_mcp.")
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
        
    print("[*] Активация плагина Godot-MCP в project.godot...")
    try:
        parser = GodotConfigParser(project_godot)
        # Добавляем плагин в список включенных
        parser.merge_packed_array("editor_plugins", "enabled", ["res://addons/godot_mcp/plugin.cfg"])
        parser.write(project_godot)
        print("[+] Плагин Godot-MCP успешно активирован.")
        return True
    except Exception as e:
        print(f"[-] Ошибка при редактировании project.godot: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python mcp_setup.py <путь_к_проекту>")
        sys.exit(1)
        
    project_dir = sys.argv[1]
    if install_godot_mcp(project_dir):
        print("[+] Установка Godot-MCP завершена успешно!")
    else:
        print("[-] Не удалось установить Godot-MCP.")
        sys.exit(1)
