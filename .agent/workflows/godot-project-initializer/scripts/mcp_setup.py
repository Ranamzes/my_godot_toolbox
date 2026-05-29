import os
import sys
import shutil
import urllib.request
import zipfile
import tempfile

# Add parent directory to import paths to access project_parser
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from project_parser import GodotConfigParser

MCP_REPO_ZIP = "https://github.com/ee0pdt/Godot-MCP/archive/refs/heads/main.zip"

def install_godot_mcp(project_path):
    print(f"[*] Starting installation of Godot-MCP into project: {project_path}")
    
    addons_dir = os.path.join(project_path, "addons")
    target_plugin_dir = os.path.join(addons_dir, "godot_mcp")
    
    if os.path.exists(target_plugin_dir):
        print(f"[!] Godot-MCP plugin is already installed in {target_plugin_dir}. Skipping download.")
        enable_plugin(project_path)
        return True

    os.makedirs(addons_dir, exist_ok=True)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "godot_mcp.zip")
        
        # Download ZIP archive
        print(f"[*] Downloading Godot-MCP from GitHub...")
        try:
            urllib.request.urlretrieve(MCP_REPO_ZIP, zip_path)
            print("[+] Archive successfully downloaded.")
        except Exception as e:
            print(f"[-] Error while downloading plugin: {e}")
            print("[!] Please download the plugin manually from https://github.com/ee0pdt/Godot-MCP")
            print("    and extract 'addons/godot_mcp' into your project's 'addons/' directory.")
            return False

        # Extract archive
        print("[*] Extracting archive...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            print("[+] Extraction completed.")
        except Exception as e:
            print(f"[-] Error while extracting archive: {e}")
            return False
        
        # Search for extracted folder. Usually named 'Godot-MCP-main'
        extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d)) and 'Godot-MCP' in d]
        if not extracted_dirs:
            print("[-] Error: Could not find extracted plugin folder.")
            return False
            
        source_plugin_dir = os.path.join(temp_dir, extracted_dirs[0], "addons", "godot_mcp")
        if not os.path.exists(source_plugin_dir):
            # Try searching in root or different structure
            print("[-] Error: Missing addons/godot_mcp folder in the archive.")
            return False
            
        # Copy plugin to project
        print(f"[*] Copying plugin to {target_plugin_dir}...")
        try:
            shutil.copytree(source_plugin_dir, target_plugin_dir)
            print("[+] Plugin successfully copied.")
        except Exception as e:
            print(f"[-] Error copying plugin: {e}")
            return False
            
    # Enable plugin in project.godot
    return enable_plugin(project_path)

def enable_plugin(project_path):
    project_godot = os.path.join(project_path, "project.godot")
    if not os.path.exists(project_godot):
        print("[-] Error: project.godot file not found. Could not enable plugin.")
        return False
        
    print("[*] Enabling Godot-MCP plugin in project.godot...")
    try:
        parser = GodotConfigParser(project_godot)
        # Add plugin to enabled list
        parser.merge_packed_array("editor_plugins", "enabled", ["res://addons/godot_mcp/plugin.cfg"])
        parser.write(project_godot)
        print("[+] Godot-MCP plugin successfully enabled.")
        return True
    except Exception as e:
        print(f"[-] Error editing project.godot: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_setup.py <project_path>")
        sys.exit(1)
        
    project_dir = sys.argv[1]
    if install_godot_mcp(project_dir):
        print("[+] Godot-MCP installation completed successfully!")
    else:
        print("[-] Failed to install Godot-MCP.")
        sys.exit(1)
