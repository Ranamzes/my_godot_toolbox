import os
import sys
import shutil
import urllib.request
import zipfile
import tempfile
import argparse
from datetime import datetime

# Add parent directory to import paths to access project_parser
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from project_parser import GodotConfigParser

JAM_PLUGIN_ZIP = "https://github.com/Ranamzes/JamCountdown/archive/refs/heads/main.zip"

def install_jam_countdown(project_path, jam_name=None, jam_url=None, jam_deadline=None):
    print(f"[*] Starting installation of Game Jam Countdown plugin into project: {project_path}")
    
    addons_dir = os.path.join(project_path, "addons")
    target_plugin_dir = os.path.join(addons_dir, "jamcountdown")
    
    # Download and install if not already present
    if not os.path.exists(target_plugin_dir):
        os.makedirs(addons_dir, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "jamcountdown.zip")
            
            print(f"[*] Downloading JamCountdown from fork (Ranamzes/JamCountdown)...")
            try:
                urllib.request.urlretrieve(JAM_PLUGIN_ZIP, zip_path)
                print("[+] Archive successfully downloaded.")
            except Exception as e:
                print(f"[-] Error while downloading plugin: {e}")
                return False

            print("[*] Extracting archive...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                print("[+] Extraction completed.")
            except Exception as e:
                print(f"[-] Error while extracting archive: {e}")
                return False
            
            extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d)) and 'JamCountdown' in d]
            if not extracted_dirs:
                print("[-] Error: Could not find extracted plugin folder.")
                return False
                
            source_plugin_dir = os.path.join(temp_dir, extracted_dirs[0], "addons", "jamcountdown")
            if not os.path.exists(source_plugin_dir):
                print("[-] Error: Missing addons/jamcountdown folder in the archive.")
                return False
                
            print(f"[*] Copying plugin to {target_plugin_dir}...")
            try:
                shutil.copytree(source_plugin_dir, target_plugin_dir)
                print("[+] Plugin successfully copied.")
            except Exception as e:
                print(f"[-] Error copying plugin: {e}")
                return False
    else:
        print(f"[!] Plugin Game Jam Countdown is already installed in {target_plugin_dir}. Skipping download.")

    # Enable the plugin
    enable_success = enable_plugin(project_path)
    if not enable_success:
        return False

    # Configure custom jam settings if provided
    if jam_name or jam_url or jam_deadline:
        configure_jam_settings(project_path, jam_name, jam_url, jam_deadline)

    return True

def enable_plugin(project_path):
    project_godot = os.path.join(project_path, "project.godot")
    if not os.path.exists(project_godot):
        print("[-] Error: project.godot file not found. Could not enable plugin.")
        return False
        
    print("[*] Enabling Game Jam Countdown plugin in project.godot...")
    try:
        parser = GodotConfigParser(project_godot)
        parser.merge_packed_array("editor_plugins", "enabled", ["res://addons/jamcountdown/plugin.cfg"])
        parser.write(project_godot)
        print("[+] Game Jam Countdown plugin successfully enabled.")
        return True
    except Exception as e:
        print(f"[-] Error editing project.godot: {e}")
        return False

def configure_jam_settings(project_path, jam_name, jam_url, jam_deadline):
    project_godot = os.path.join(project_path, "project.godot")
    if not os.path.exists(project_godot):
        return False

    print("[*] Configuring jam countdown settings in project.godot...")
    try:
        parser = GodotConfigParser(project_godot)
        
        parser.set_value("jam_countdown", "has_custom_data", "true")
        if jam_name:
            parser.set_value("jam_countdown", "jam_title", f'"{jam_name}"')
        if jam_url:
            parser.set_value("jam_countdown", "link_to_jam_page", f'"{jam_url}"')
            
        if jam_deadline:
            try:
                # Try ISO format parsing (e.g. 2026-06-15T18:00:00)
                dt = datetime.fromisoformat(jam_deadline.replace('Z', '+00:00'))
                utc_timestamp = int(dt.timestamp())
                parser.set_value("jam_countdown", "end_date_utc_unix", str(utc_timestamp))
                print(f"[+] Set jam deadline to UTC timestamp: {utc_timestamp} ({jam_deadline})")
            except Exception as e:
                print(f"[-] Error parsing deadline '{jam_deadline}': {e}. Storing as fallback.")

        parser.write(project_godot)
        print("[+] Jam countdown settings successfully configured in project.godot.")
        return True
    except Exception as e:
        print(f"[-] Error writing jam settings to project.godot: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download, install and configure Game Jam Countdown plugin")
    parser.add_argument("project_path", help="Path to the Godot project")
    parser.add_argument("--name", help="Game jam title")
    parser.add_argument("--url", help="Itch.io jam page URL")
    parser.add_argument("--deadline", help="Deadline in ISO 8601 format (e.g., 2026-06-15T18:00:00)")

    args = parser.parse_args()

    if install_jam_countdown(args.project_path, args.name, args.url, args.deadline):
        print("[+] Game Jam Countdown installation and configuration completed successfully!")
    else:
        print("[-] Failed to install Game Jam Countdown.")
        sys.exit(1)
