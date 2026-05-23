# My Godot Toolbox

Central registry of reusable Godot modules organized by **Function/Domain** in the `godot-shared-modules` organization.

## Agent Workflow

### 📦 Quick Install (One-Liner)

To add the **Toolbox Manager** skill to your current project, run the command for your OS:

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force .agent/workflows; Invoke-WebRequest https://raw.githubusercontent.com/godot-shared-modules/toolbox-skill/main/toolbox.md -OutFile .agent/workflows/toolbox.md
```

**Linux / Mac / Bash:**
```bash
mkdir -p .agent/workflows && curl -o .agent/workflows/toolbox.md https://raw.githubusercontent.com/godot-shared-modules/toolbox-skill/main/toolbox.md
```

This downloads the latest Skill from the shared repository.

### Usage
Use `/toolbox` slash command to invoke the agent skill (`.agent/workflows/toolbox.md`).

## Module Structure

Modules are categorized into folders like `systems/`, `ui/`, `mechanics/`.
Each module is a **separate Git repository** linked here as a **Submodule**.

```
my_godot_toolbox/
├── systems/
│   ├── inventory/          # Submodule -> github.com/godot-shared-modules/inventory
│   └── quest_system/       # Submodule -> github.com/godot-shared-modules/quest_system
├── ui/
│   └── menu_framework/     # Submodule
└── README.md
```

**Inside a module:**
```
<category>/<module_name>/
├── components/      # Single-responsibility node scripts & scenes
├── resources/       # Custom Resource classes
├── scenes/          # Pre-built scenes (ready-to-use assemblies)
├── <module_name>.gd # Main entry point / facade
├── .gitignore       # Excludes *.import, .godot/
└── README.md        # Documentation & metadata (REQUIRED)
```

## Module README Template

Each module's `README.md` is the **single source of truth**:

```markdown
# Module Name

One-line description.

## Module Info
- **Category**: systems
- **Version**: 1.0.0
- **Godot**: 4.3+
- **Tags**: ui, rpg
- **Dependencies**: none
- **Compatible Games**: 2D, 3D, Both
- **Autoloads**: none

## Configuration
- `@export var target: Node` — description **(required)**

## Signals
- `my_signal(arg)` — description

## Quick Start
1. ...

## API
- `ClassName.method()` — description
```

## Usage

### Install a module

```bash
# As a static copy (stable):
git clone --depth 1 <module_url> <dest_path> && rm -rf <dest_path>/.git

# As a submodule (editable, two-way sync):
git submodule add <module_url> <dest_path>
```

### Push changes back during a jam

```bash
cd <module_path>
git checkout main           # avoid detached HEAD!
git add . && git commit -m "fix: description" && git push
```
