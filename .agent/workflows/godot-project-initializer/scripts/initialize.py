import os
import sys
import argparse
import shutil

# Add parent directory to import paths to access helper modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from project_parser import GodotConfigParser
from mcp_setup import install_godot_mcp
from jam_setup import install_jam_countdown

TEMPLATES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "templates")

def main():
    parser = argparse.ArgumentParser(description="Automated project builder and initializer for Godot 4")
    parser.add_argument("--path", required=True, help="Path to the created/existing Godot project folder")
    parser.add_argument("--presets", default="base", help="Comma-separated list of presets (e.g. base,2d,jam)")
    parser.add_argument("--mcp", action="store_true", help="Enable and install Godot-MCP integration")
    parser.add_argument("--ai", default="antigravity", help="Target AI environments to prepare folders for (antigravity, cursor, windsurf, vscode, all)")
    parser.add_argument("--jam-name", help="Optional Game Jam Title to preconfigure")
    parser.add_argument("--jam-url", help="Optional Itch.io jam page URL to preconfigure")
    parser.add_argument("--jam-deadline", help="Optional Jam deadline in ISO 8601 format (e.g. 2026-06-15T18:00:00)")
    
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    presets = [p.strip().lower() for p in args.presets.split(",")]
    selected_ais = [a.strip().lower() for a in args.ai.split(",")]
    
    print(f"[*] Initializing Godot project at: {project_path}")
    print(f"[*] Selected presets: {', '.join(presets)}")
    print(f"[*] Target AI environments: {', '.join(selected_ais)}")
    
    # 1. Project directory creation
    os.makedirs(project_path, exist_ok=True)
    
    # Create base directories in project
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
        
    # 2. Initialize Git files and base project.godot
    project_godot_path = os.path.join(project_path, "project.godot")
    base_template_dir = os.path.join(TEMPLATES_DIR, "base")
    
    # Copy gitignore and gitattributes
    shutil.copy(os.path.join(base_template_dir, "gitignore.txt"), os.path.join(project_path, ".gitignore"))
    shutil.copy(os.path.join(base_template_dir, "gitattributes.txt"), os.path.join(project_path, ".gitattributes"))
    print("[+] Created .gitignore and .gitattributes")
    
    # Create AI service folders and copy gdignore
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
            print(f"[+] Created AI service folder: {folder_name} with .gdignore")
    
    # If project.godot does not exist, create it from base template
    if not os.path.exists(project_godot_path):
        shutil.copy(os.path.join(base_template_dir, "project.godot.ini"), project_godot_path)
        # Set project name based on folder name
        project_name = os.path.basename(os.path.normpath(project_path))
        config = GodotConfigParser(project_godot_path)
        config.set_value("application", "config/name", f'"{project_name}"')
        config.write(project_godot_path)
        print(f"[+] Created new project.godot for project: {project_name}")
        
    # 3. Apply preset configurations (2D, Jam)
    config = GodotConfigParser(project_godot_path)
    
    for preset in presets:
        if preset == "base":
            continue
            
        preset_dir = os.path.join(TEMPLATES_DIR, preset)
        preset_ini = os.path.join(preset_dir, "project.godot.ini")
        
        if os.path.exists(preset_ini):
            print(f"[*] Applying configuration for preset '{preset}'...")
            config.merge_with_ini(preset_ini)
            
    # 4. Configure Autoloads
    autoloads = {}
    
    # Copy base singletons (EventBus and SoundManager)
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
    
    print("[+] Copied base singletons (EventBus.gd, SoundManager.gd)")
        
    # Register autoloads in project.godot
    for name, res_path in autoloads.items():
        config.set_value("autoload", name, f'"{res_path}"')
        
    config.write(project_godot_path)
    print("[+] Autoloads registered in project.godot")
    
    # 5. Install Godot-MCP (if requested)
    if args.mcp:
        install_godot_mcp(project_path)
        
    # 6. Install Game Jam Countdown plugin (if jam preset selected)
    if "jam" in presets:
        install_jam_countdown(project_path, jam_name=args.jam_name, jam_url=args.jam_url, jam_deadline=args.jam_deadline)
        
    print("\n[+] Project initialization completed successfully!")
    print("Available project structure:")
    print(" - res://src/autoloads/ (Global singletons)")
    print(" - res://scenes/ (Game scenes)")
    print(" - res://scripts/ (Logic and components)")
    print(" - res://assets/ (Textures, Sounds, Music)")

if __name__ == "__main__":
    main()
