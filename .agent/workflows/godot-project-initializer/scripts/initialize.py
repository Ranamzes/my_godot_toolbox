import os
import sys
import argparse
import shutil

# Добавляем родительский каталог в пути импорта для доступа к вспомогательным модулям
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from project_parser import GodotConfigParser
from mcp_setup import install_godot_mcp

TEMPLATES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "templates")

def main():
    parser = argparse.ArgumentParser(description="Автоматический сборщик и инициализатор проектов Godot 4")
    parser.add_argument("--path", required=True, help="Путь к создаваемому/существующему проекту Godot")
    parser.add_argument("--presets", default="base", help="Список пресетов через запятую (например, base,2d,jam)")
    parser.add_argument("--mcp", action="store_true", help="Включить и установить интеграцию с Godot-MCP")
    parser.add_argument("--ai", default="antigravity", help="ИИ-среда для подготовки служебных папок (antigravity, cursor, windsurf, vscode, all)")
    
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    presets = [p.strip().lower() for p in args.presets.split(",")]
    selected_ais = [a.strip().lower() for a in args.ai.split(",")]
    
    print(f"[*] Инициализация Godot проекта в: {project_path}")
    print(f"[*] Выбранные пресеты: {', '.join(presets)}")
    print(f"[*] Целевые ИИ-среды: {', '.join(selected_ais)}")
    
    # 1. Создание каталога проекта
    os.makedirs(project_path, exist_ok=True)
    
    # Создаем базовые директории в проекте
    folders = [
        "src/autoloads",
        "scenes",
        "scripts",
        "assets/textures",
        "assets/sounds",
        "assets/music"
    ]
    for folder in folders:
        os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
    # 2. Инициализация Git-файлов и базового project.godot
    project_godot_path = os.path.join(project_path, "project.godot")
    base_template_dir = os.path.join(TEMPLATES_DIR, "base")
    
    # Копируем gitignore и gitattributes
    shutil.copy(os.path.join(base_template_dir, "gitignore.txt"), os.path.join(project_path, ".gitignore"))
    shutil.copy(os.path.join(base_template_dir, "gitattributes.txt"), os.path.join(project_path, ".gitattributes"))
    print("[+] Созданы .gitignore и .gitattributes")
    
    # Создаем служебные папки ИИ и копируем gdignore
    ai_dirs = {
        "antigravity": ".agent",
        "cursor": ".cursor",
        "windsurf": ".windsurf",
        "vscode": ".vscode"
    }
    for ai_key, folder_name in ai_dirs.items():
        if ai_key in selected_ais or "all" in selected_ais:
            ai_folder_path = os.path.join(project_path, folder_name)
            os.makedirs(ai_folder_path, exist_ok=True)
            shutil.copy(os.path.join(base_template_dir, "gdignore.txt"), os.path.join(ai_folder_path, ".gdignore"))
            print(f"[+] Создана служебная папка ИИ: {folder_name} с .gdignore")
    
    # Если project.godot не существует, создаем его на основе базового шаблона
    if not os.path.exists(project_godot_path):
        shutil.copy(os.path.join(base_template_dir, "project.godot.ini"), project_godot_path)
        # Настраиваем имя проекта по названию папки
        project_name = os.path.basename(os.path.normpath(project_path))
        config = GodotConfigParser(project_godot_path)
        config.set_value("application", "config/name", f'"{project_name}"')
        config.write(project_godot_path)
        print(f"[+] Создан новый project.godot для проекта: {project_name}")
        
    # 3. Применяем конфигурации пресетов (2D, Jam)
    config = GodotConfigParser(project_godot_path)
    
    for preset in presets:
        if preset == "base":
            continue
            
        preset_dir = os.path.join(TEMPLATES_DIR, preset)
        preset_ini = os.path.join(preset_dir, "project.godot.ini")
        
        if os.path.exists(preset_ini):
            print(f"[*] Применение конфигурации пресета '{preset}'...")
            config.merge_with_ini(preset_ini)
            
    # 4. Настройка автозагрузок (Autoloads)
    autoloads = {}
    
    # Скопируем базовые синглтоны (EventBus и SoundManager)
    # EventBus
    event_bus_src = os.path.join(base_template_dir, "autoloads", "event_bus.gd")
    event_bus_dest = os.path.join(project_path, "src", "autoloads", "event_bus.gd")
    shutil.copy(event_bus_src, event_bus_dest)
    autoloads["EventBus"] = "*res://src/autoloads/event_bus.gd"
    
    # SoundManager
    sound_manager_src = os.path.join(base_template_dir, "autoloads", "sound_manager.gd")
    sound_manager_dest = os.path.join(project_path, "src", "autoloads", "sound_manager.gd")
    shutil.copy(sound_manager_src, sound_manager_dest)
    autoloads["SoundManager"] = "*res://src/autoloads/sound_manager.gd"
    
    print("[+] Скопированы базовые синглтоны (EventBus.gd, SoundManager.gd)")
        
    # Регистрируем автозагрузки в project.godot
    for name, res_path in autoloads.items():
        config.set_value("autoload", name, f'"{res_path}"')
        
    config.write(project_godot_path)
    print("[+] Автозагрузки зарегистрированы в project.godot")
    
    # 5. Установка Godot-MCP (если запрошено)
    if args.mcp:
        install_godot_mcp(project_path)
        
    print("\n[+] Инициализация проекта успешно завершена!")
    print("Доступная структура проекта:")
    print(" - res://src/autoloads/ (Глобальные синглтоны)")
    print(" - res://scenes/ (Игровые сцены)")
    print(" - res://scripts/ (Логика и компоненты)")
    print(" - res://assets/ (Текстуры, Звуки, Музыка)")

if __name__ == "__main__":
    main()
