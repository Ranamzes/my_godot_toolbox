---
name: godot-project-initializer
description: "Initialize and configure Godot 4 projects (Base, 2D, Jam) using automated presets, Godot-MCP integration, and interactive user polling."
---

# Godot Project Initializer

This skill enables quick, professional, and reliable initialization of new **Godot 4** projects (v4.0 and above). It automates directory creation, configuration merging (`base`, `2d`, `jam` presets), registering global autoload singletons, and preparing the workspace for live AI-editing via **Godot-MCP**.

---

## 1. CRITICAL RULE: Interactive User Polling

You **MUST** begin by conducting a brief interactive poll in the user's preferred language (e.g., Russian if the user asks in Russian). **DO NOT** execute initialization scripts blindly without clarifying the requirements first.

Ask the following questions to help select the best presets and configuration:
1. **Game Description**: "Briefly describe your game idea (genre, core loop)."
2. **Visual Style & Presets**: "What is the visual style? If it is 2D pixel-art, we will apply the `2d` preset (enabling Nearest texture filtering, gl_compatibility rendering, and Pixel Snap). Otherwise, we will set up the base Forward+ renderer."
3. **Game Jam Preset**: "Are you building this for a game jam? If yes, we'll apply the `jam` preset to configure standard WASD/Arrows inputs."
4. **Godot-MCP Integration**: "Would you like to install the `godot_mcp` addon? This will allow me to see your scene trees, add/configure nodes, and edit GDScripts in real-time while the project is open in the Godot Editor."
5. **Toolbox Systems**: "Do you want to immediately copy any ready-made systems from your `my_godot_toolbox` (such as `footstep_system`)?"

---

## 2. Initialization Workflow (For the Agent)

Once the user confirms the desired setup:

### Step 1: Run the Initialization Script
Invoke the `initialize.py` script with the chosen flags. The script is located at:
`my_godot_toolbox/.agent/workflows/godot-project-initializer/scripts/initialize.py`

Example run for a 2D Game Jam project with Godot-MCP and Antigravity + Cursor workspace support:
```bash
python3 my_godot_toolbox/.agent/workflows/godot-project-initializer/scripts/initialize.py \
  --path /Users/remart/Projects/games/my_new_game \
  --presets base,2d,jam \
  --ai antigravity,cursor \
  --mcp
```

### Script Arguments:
* `--path`: Absolute path to the new/existing Godot project folder.
* `--presets`: Comma-separated list of presets (`base`, `2d`, `jam`).
* `--ai`: Comma-separated list of target AI environments to prepare directories for (`antigravity`, `cursor`, `windsurf`, `vscode`, `all`). Creates matching folders (e.g., `.agent`, `.cursor`) and automatically places a `.gdignore` file inside each one to prevent Godot imports.
* `--mcp`: Flag. If set, downloads the `ee0pdt/Godot-MCP` editor addon, unpacks it into `addons/godot_mcp`, and registers it in `project.godot`.

### Step 2: Verify Created Files
Check that:
1. `project.godot` exists and is valid.
2. The folder structure is present (`src/autoloads/`, `scenes/`, `scripts/`, `assets/`).
3. `.gitignore` and `.gitattributes` are generated correctly.
4. Auto-loaded singletons (`event_bus.gd`, etc.) are placed in `src/autoloads/` and configured.

### Step 3: Explain Structure to the User
Explain the generated structure to the user in their language. Highlight the available autoloads (`EventBus` for events, `SoundManager` for audio) and how to run the game.

If Godot-MCP was installed, remind the user:
> "I have installed and enabled the **Godot-MCP** plugin in your project. Open this project in the Godot 4 Editor. Once it's open, I will be able to use the `godot-editor` MCP server tools to interact with your live scene tree, create nodes, and tweak scripts directly from our chat!"

---

## 3. Presets & Autoloads Specification

### Base Preset
* Sets up the standard directory layout.
* Copies and registers **`EventBus`** (`res://src/autoloads/event_bus.gd`) and **`SoundManager`** (`res://src/autoloads/sound_manager.gd`) singletons to support global events and pooled audio.
* Generates optimized `.gitignore` and `.gitattributes` (Git LFS enabled).

### 2D Preset
* Switches rendering method to `gl_compatibility` (best for pixel-art and web/mobile targets).
* Sets default texture filter to `Nearest` (keeps pixel-art crisp and sharp).
* Enables `snap_2d_transforms_to_pixel` and `snap_2d_vertices_to_pixel` to prevent sub-pixel jitter during camera movement.

### Jam Preset
* Sets up standard input map actions WASD + Arrow Keys (`move_left`, `move_right`, `move_up`, `move_down`), Spacebar (`jump`), and E/LMB (`action`).
* Automatically downloads, installs, and enables the timezone-safe **Game Jam Countdown** editor plugin from the user's fork (`https://github.com/Ranamzes/JamCountdown`) in your project to keep track of the jam's deadline right from your editor toolbar.
* Supports automatic preconfiguration of the countdown via command-line arguments.

---

## 4. Interactive Jam Configuration Workflow (For the Agent)

When the **jam** preset is selected, you **MUST** follow this autonomous workflow to minimize user effort:

1. **Ask for the Jam URL**:
   Ask the user for the Itch.io link to their game jam. E.g., *"Could you please share the link to your game jam on itch.io?"*

2. **Autonomous Jam Scraping**:
   - Immediately invoke the `read_url_content` tool to fetch and read the game jam page's contents.
   - Scan the page metadata, HTML, or markdown text to extract:
     * The **Jam Title** (e.g. `<title>`, `DinoJam 5`, etc.)
     * The **Jam Deadline / End Date** (Look for date elements, countdown data-targets, or strings specifying when the jam ends. Convert the found local/UTC date to a standard ISO 8601 format like `YYYY-MM-DDTHH:MM:SS` in UTC or with an offset).
   - Once retrieved, present the discovered values to the user for quick verification:
     > *"I checked the jam page and found the following details:*
     > * *Jam Name: **DinoJam 5***
     > * *Deadline: **June 15, 2026 at 18:00 UTC** (formatted as `2026-06-15T18:00:00`)*
     >
     > *Please let me know if these details are correct or if you'd like me to adjust them! Once confirmed, I will automatically download and configure the countdown plugin."*
   - If you cannot fetch the page or fail to find these details autonomously, politely ask the user to provide them:
     > *"I successfully visited the page but couldn't locate the exact deadline. Could you please tell me the jam name and the deadline date/time?"*

3. **Run setup with Jam arguments**:
   Once the details are confirmed by the user, pass them directly to the initialization script to preconfigure the project settings:
   ```bash
   python3 my_godot_toolbox/.agent/workflows/godot-project-initializer/scripts/initialize.py \
     --path /Users/remart/Projects/games/my_new_game \
     --presets base,2d,jam \
     --jam-name "DINOJAM 5" \
     --jam-url "https://itch.io/jam/dinojam5" \
     --jam-deadline "2026-06-15T18:00:00"
   ```
   This automatically downloads your improved fork, enables it, and preconfigures `res://addons/jamcountdown/jam_countdown.tscn` perfectly in `project.godot`.

4. **Fallback Configuration**:
   If the project has already been initialized, you can dynamically configure the jam countdown at any time by running `jam_setup.py`:
   ```bash
   python3 my_godot_toolbox/.agent/workflows/godot-project-initializer/scripts/jam_setup.py \
     /Users/remart/Projects/games/my_new_game \
     --name "DINOJAM 5" \
     --url "https://itch.io/jam/dinojam5" \
     --deadline "2026-06-15T18:00:00"
   ```
