# macOS Actuation Control CLI - Documentation

**Version:** 1.0.0 
**Last Updated:** January 2026  
**Developer:** Kartik (NullVoider)

---

## Table of Contents

1. [Overview](#overview)
2. [Capability Summary](#capability-summary)
3. [Technical Specifications](#technical-specifications)
4. [Installation & Setup](#installation--setup)
5. [Usage Modes](#usage-modes)
6. [Syntax Reference](#syntax-reference)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The macOS VM Control CLI is an intelligent middleware tool designed for Computer Use Agents (CUA) to remotely control macOS virtual machines via SSH. It provides comprehensive mouse and keyboard automation using `cliclick` and `osascript` (AppleScript).

### Key Features
- ✅ **Zero UI Required** - Pure command-line interface
- ✅ **SSH-Based** - Secure remote control over SSH
- ✅ **Smart Detection** - Automatically detects command type (mouse/keyboard)
- ✅ **Batch Processing** - Execute multiple commands from files
- ✅ **Interactive Mode** - Real-time control with command prompt
- ✅ **Cross-Platform Client** - Runs on any system with Python 3.x

---

## Capability Summary

### 🖱️ Mouse Control Capabilities

| Capability | Description | Precision |
|------------|-------------|-----------|
| **Movement** | Move cursor to exact coordinates | Pixel-perfect |
| **Clicking** | Left, right, middle, double, triple clicks | 100% reliable |
| **Dragging** | Click-drag-release operations | Smooth paths |
| **Scrolling** | 4-directional scrolling with custom amounts | Line-by-line |
| **Hold/Release** | Manual drag control | Full control |
| **Relative Actions** | "here" actions at current cursor position | Position-aware |

### ⌨️ Keyboard Control Capabilities

| Capability | Description | Support Level |
|------------|-------------|---------------|
| **Text Typing** | Type arbitrary text with special char escaping | Full |
| **Modifiers** | Cmd (⌘), Ctrl (⌃), Alt (⌥), Shift (⇧), Fn | All supported |
| **Navigation Keys** | Arrow keys, Home, End, PgUp, PgDn | AppleScript-backed |
| **Special Keys** | Enter, Tab, Esc, Space, Delete, Backspace | All functional |
| **Function Keys** | F1-F16 | Hardware-dependent |
| **Media Keys** | Volume, Brightness, Play/Pause, Mute | Full support |
| **Shortcuts** | Multi-modifier combinations (e.g., Cmd+Shift+Q) | Unlimited |

### 🔧 System Features

| Feature | Description |
|---------|-------------|
| **Connection Management** | Persistent SSH connections with auto-reconnect |
| **Tool Detection** | Auto-finds cliclick across common install paths |
| **Error Handling** | Graceful failures with detailed error messages |
| **Batch Execution** | File-based command sequences with timing control |
| **Command History** | All executed commands logged to output |
| **Smart Delays** | Automatic timing for UI-heavy operations |

---

## Technical Specifications

### System Requirements

**Server (macOS VM):**
- **Hardware:** Apple Silicon (M1/M2/M3/M4) recommended for pre-built binaries.
    - *Note: Intel Macs must run the tool from source (Python).*
- **OS:** macOS 11.0 (Big Sur) or later.
- **Dependencies:** - SSH server enabled
    - `cliclick` installed (via Homebrew or manual)
    - Accessibility permissions enabled for Terminal/SSH

**Client (Control Machine):**
- **For Binary Usage:** - Linux (x64), Windows (x64), or macOS (Apple Silicon).
    - No Python required.
- **For Source Usage:**
    - Python 3.7 or later.
    - `paramiko` library.

### Dependencies

```bash
# Server-side (macOS VM)
brew install cliclick

# Client-side (Control Machine)
pip install paramiko
```

### Architecture

```
┌─────────────────┐         SSH          ┌──────────────────┐
│  Client Machine │ ◄─────────────────►  │    macOS VM      │
│  (Python CLI)   │     Port 2222        │                  │
└─────────────────┘                      │  ┌────────────┐  │
                                         │  │  cliclick  │  │
                                         │  └────────────┘  │
                                         │  ┌────────────┐  │
                                         │  │ osascript  │  │
                                         │  └────────────┘  │
                                         └──────────────────┘
```

### Performance Metrics

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Mouse Move | ~20-50ms | 50-100 ops/sec |
| Click | ~30-60ms | 30-50 ops/sec |
| Type Character | ~10-20ms | 100+ chars/sec |
| Scroll | ~100-200ms | 10-20 ops/sec |
| Keyboard Shortcut | ~40-80ms | 20-40 ops/sec |

*Note: Latencies include network overhead. Local operations are faster.*

---

## Installation & Setup

### Step 1: Install cliclick on macOS VM

```bash
# Via Homebrew (recommended)
brew install cliclick

# Verify installation
which cliclick
# Expected output: /usr/local/bin/cliclick or /opt/homebrew/bin/cliclick

# Test cliclick
cliclick -v
```

### Step 2: Enable SSH on macOS VM

```bash
# Enable SSH (Remote Login)
sudo systemsetup -setremotelogin on

# Verify SSH is running
sudo systemsetup -getremotelogin
# Expected output: Remote Login: On
```

### Step 3: Configure Port Forwarding (if using VM)

For VMs like UTM, QEMU, or VirtualBox:

```bash
# Example: Forward host port 2222 to guest port 22
# (Configuration varies by hypervisor)
```

### Step 4: Install Python Dependencies

```bash
# On control machine
pip install paramiko
```

### Step 5: Download & Install

**Option A: One-Line Installer (Recommended)**
This automatically detects your OS, downloads the latest binary, and adds it to your PATH.

* **Linux & macOS:**
    ```bash
    curl -fsSL https://raw.githubusercontent.com/nullvoider07/macos_actuation_control/main/install/install.sh | bash
    ```

* **Windows (PowerShell):**
    ```powershell
    irm https://raw.githubusercontent.com/nullvoider07/macos_actuation_control/main/install/install.ps1 | iex
    ```

**Option B: Manual Download**
If you prefer, download the standalone binary for your OS directly from the [Releases Page](https://github.com/nullvoider07/macos_actuation_control/releases).

---

## Usage Modes

### 1. Interactive Mode (Default)

```bash
python3 macos_actuation_control.py --username agentuser --host localhost --port 2222
```

**Features:**
- Real-time command execution
- Command history
- Tab completion (if supported by terminal)
- `help` command for quick reference
- `exit` or `quit` to disconnect

**Example Session:**
```
macOS> 960 540 left
[MOUSE] Executed: 960 540 left

macOS> type Hello World
[KEYBOARD] Executed: type Hello World

macOS> press #c
[KEYBOARD] Executed: press #c

macOS> exit
[*] Exiting...
[*] Disconnected from macOS VM
```

### 2. Single Command Mode

```bash
python3 macos_actuation_control.py -c "960 540 right" --username agentuser --host localhost --port 2222
```

**Use Cases:**
- Quick one-off operations
- Scripting integrations
- API-like execution

### 3. Batch Mode (File Execution)

```bash
python3 macos_actuation_control.py -f commands.txt -d 0.5 --username agentuser --host localhost --port 2222
```

**File Format:** (`commands.txt`)
```
# This is a comment - ignored by the parser
# Lines starting with # are comments
# Empty lines are also ignored

# Open Spotlight and search for Calculator
press #space
type Calculator
press {Enter}

# Wait for app to open, then perform calculation
# (Use delays between commands with -d flag)
type 2+2
press {Enter}
```

**Batch Mode Options:**
- `-f` / `--file` - Specify command file path
- `-d` / `--delay` - Delay in seconds between commands (default: 0.1)

---

## Syntax Reference

### Mouse Commands

#### Basic Format
```
<x> <y> <action> [parameters]
```

#### Actions

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| **Move** | `<x> <y> move` | Move cursor to coordinates | `500 400 move` |
| **Left Click** | `<x> <y> left` | Move and left-click | `960 540 left` |
| **Click (Alias)** | `<x> <y> click` | Same as left-click | `960 540 click` |
| **Right Click** | `<x> <y> right` | Move and right-click | `960 540 right` |
| **Double Click** | `<x> <y> double` | Move and double-click | `640 360 double` |
| **Triple Click** | `<x> <y> triple` | Move and triple-click | `640 360 triple` |
| **Middle Click** | `<x> <y> middle` | Move and middle-click | `960 540 middle` |
| **Hold** | `<x> <y> hold` | Press and hold mouse button | `500 500 hold` |
| **Release** | `<x> <y> release` | Release mouse button | `700 700 release` |
| **Drag** | `<x> <y> drag <x2> <y2>` | Drag from (x,y) to (x2,y2) | `100 100 drag 500 500` |

#### Scrolling

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| **Scroll Up** | `<x> <y> scroll_up [amount]` | Scroll up N lines | `960 540 scroll_up 5` |
| **Scroll Down** | `<x> <y> scroll_down [amount]` | Scroll down N lines | `960 540 scroll_down 10` |
| **Scroll Left** | `<x> <y> scroll_left [amount]` | Scroll left N columns | `960 540 scroll_left 3` |
| **Scroll Right** | `<x> <y> scroll_right [amount]` | Scroll right N columns | `960 540 scroll_right 3` |

**Notes:**
- Default scroll amount: 5
- Scrolling uses AppleScript key codes (arrow keys)
- Alternative syntaxes: `scroll-up`, `scrollup`

#### "Here" Actions (Current Position)

| Command | Syntax | Description |
|---------|--------|-------------|
| **Here + Click** | `here left` | Click at current cursor position |
| **Here + Right** | `here right` | Right-click at current position |
| **Here + Double** | `here double` | Double-click at current position |
| **Here + Triple** | `here triple` | Triple-click at current position |
| **Here + Scroll** | `here scroll_down 5` | Scroll at current position |

### Keyboard Commands

#### Basic Format
```
<action> <content>
```

#### Actions

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| **Type** | `type <text>` | Type literal text | `type Hello World` |
| **Press** | `press <keys>` | Press key/shortcut | `press #c` |
| **Key (Alias)** | `key <keys>` | Same as press | `key {Enter}` |

#### Special Keys

##### Navigation Keys
```
{Enter}      or {Return}     - Enter/Return key
{Tab}                        - Tab key
{Esc}        or {Escape}     - Escape key
{Space}                      - Space bar
{Backspace}  or {BS}         - Backspace (delete left)
{Delete}     or {Del}        - Forward delete (delete right)
{Up}                         - Arrow up
{Down}                       - Arrow down
{Left}                       - Arrow left
{Right}                      - Arrow right
{Home}                       - Home (jump to line start)
{End}                        - End (jump to line end)
{PgUp}                       - Page up
{PgDn}                       - Page down
```

##### Function Keys
```
{F1}, {F2}, {F3}, {F4}, {F5}, {F6}, {F7}, {F8}
{F9}, {F10}, {F11}, {F12}, {F13}, {F14}, {F15}, {F16}
```

##### Media Keys
```
{VolumeUp}                   - Increase volume
{VolumeDown}                 - Decrease volume
{Mute}                       - Mute/unmute audio
{BrightnessUp}               - Increase brightness
{BrightnessDown}             - Decrease brightness
{PlayPause}                  - Play/pause media
```

##### Modifier Keys (Standalone)
```
{Cmd}       or {Command}     - Command key (⌘)
{Option}    or {Alt}         - Option/Alt key (⌥)
{Control}   or {Ctrl}        - Control key (⌃)
{Shift}                      - Shift key (⇧)
{Fn}                         - Function key
```

#### Modifier Symbols

| Symbol | Modifier | Example | Description |
|--------|----------|---------|-------------|
| `#` or `⌘` | Command | `#c` | Command+C (Copy) |
| `!` or `⌥` | Option/Alt | `!{Delete}` | Option+Delete |
| `^` or `⌃` | Control | `^a` | Control+A |
| `+` or `⇧` | Shift | `+a` | Shift+A (uppercase) |

#### Multi-Modifier Combinations

```
#+z                          - Command+Shift+Z (Redo)
#!{Esc}                      - Command+Option+Esc (Force Quit menu)
^!{Delete}                   - Control+Option+Delete
#+3                          - Command+Shift+3 (Screenshot)
```

### Auto-Detection Rules

The CLI automatically detects command types:

| Input Pattern | Detected As | Example |
|---------------|-------------|---------|
| `<num> <num>` | Mouse move | `500 400` → `500 400 move` |
| `<num> <num> <action>` | Mouse action | `500 400 right` |
| `here <action>` | Mouse at current pos | `here left` |
| `type <text>` | Keyboard typing | `type Hello` |
| `press <keys>` | Keyboard shortcut | `press #c` |
| `#<char>` | Keyboard shortcut | `#c` → `press #c` |
| `{Key}` | Special key press | `{Enter}` → `press {Enter}` |
| `<plain text>` | Type text | `Hello` → `type Hello` |

---

## Examples

### Basic Mouse Operations

```bash
# Move cursor to center of 1920x1080 screen
960 540 move

# Left-click at position
960 540 left

# Right-click to open context menu
960 540 right

# Double-click to select word
640 360 double

# Triple-click to select paragraph
640 360 triple

# Click at current cursor position
here left
```

### Drag & Drop

```bash
# Drag a file from (300,300) to (700,700)
300 300 drag 700 700

# Manual drag (for complex paths)
500 500 hold
# ... intermediate movements if needed ...
700 700 release
```

### Scrolling

```bash
# Scroll down in a browser
960 540 scroll_down 10

# Scroll up in a document
960 540 scroll_up 5

# Horizontal scrolling in a wide table
960 540 scroll_right 3

# Scroll at current cursor position
here scroll_down 5
```

### Text Typing

```bash
# Type simple text
type Hello World

# Type with special characters
type Price: $100 @ 50% off!

# Type with quotes
type He said "Hello"

# Type multi-line (use Enter key)
type Line 1
press {Enter}
type Line 2
```

### Keyboard Shortcuts

```bash
# Copy (Command+C)
press #c

# Paste (Command+V)
press #v

# Select All (Command+A)
press #a

# Undo (Command+Z)
press #z

# Redo (Command+Shift+Z)
press #+z

# Save (Command+S)
press #s

# Open Spotlight (Command+Space)
press #space

# App Switcher (Command+Tab)
press #tab

# Force Quit menu (Command+Option+Esc)
press #!{Esc}
```

### Navigation

```bash
# Jump to beginning of line
press {Home}

# Jump to end of line
press {End}

# Move cursor right by one character
press {Right}

# Move cursor up by one line
press {Up}

# Page down
press {PgDn}

# Delete word to the left
press !{Delete}

# Control+A (line start in Terminal)
press ^a

# Control+E (line end in Terminal)
press ^e
```

### Function Keys

```bash
# Mission Control (F3)
press {F3}

# Launchpad (F4)
press {F4}

# Show Desktop (F11)
press {F11}

# Adjust volume
press {VolumeUp}
press {VolumeDown}
press {Mute}
```

### Complex Workflows

#### Example 1: Open Calculator and Perform Calculation
```bash
# Open Spotlight
press #space

# Type app name
type Calculator

# Press Enter to open
press {Enter}

# Wait for app to open (use -d flag in batch mode)
# Then type calculation
type 2+2

# Press Enter for result
press {Enter}
```

#### Example 2: Select and Copy Text
```bash
# Click at start of text
300 400 left

# Drag to select text
300 400 drag 600 400

# Copy selection
press #c
```

#### Example 3: Fill a Form
```bash
# Click first field
400 300 left

# Type name
type John Doe

# Tab to next field
press {Tab}

# Type email
type john@example.com

# Tab to next field
press {Tab}

# Type phone
type 555-1234

# Submit form
press {Enter}
```

### Batch File Example

**File:** `workflow.txt`
```
# Open Safari
press #space
type Safari
press {Enter}

# Wait for Safari to open
# (Add delays between commands with -d 1.0)

# Navigate to URL
press #l
type https://example.com
press {Enter}

# Scroll down page
960 540 scroll_down 10

# Click a link at specific position
500 600 left

# Take screenshot
press #+4
```

**Execute:**
```bash
python3 macos_actuation_control.py -f workflow.txt -d 1.0 --username agentuser
```

---

## Troubleshooting

### Common Issues

#### 1. "cliclick not found"

**Problem:** CLI can't find cliclick on macOS VM

**Solutions:**
```bash
# Install via Homebrew
brew install cliclick

# Or download manually
curl -O https://github.com/BlueM/cliclick/releases/latest/download/cliclick
chmod +x cliclick
sudo mv cliclick /usr/local/bin/
```

#### 2. "Authentication failed"

**Problem:** SSH credentials incorrect

**Solutions:**
- Verify username and password
- Ensure SSH is enabled on macOS: `sudo systemsetup -setremotelogin on`
- Check port forwarding (if using VM)

#### 3. "Connection refused"

**Problem:** Can't connect to SSH server

**Solutions:**
- Verify SSH is running: `sudo launchctl list | grep ssh`
- Check firewall settings on macOS
- Verify port forwarding configuration
- Test with regular SSH: `ssh -p 2222 user@localhost`

#### 4. Navigation Keys Not Working

**Problem:** Arrow keys, Home, End, etc. don't work

**Solution:** These keys now use AppleScript (implemented in latest version). Ensure:
- Python 3 is available on macOS VM
- Commands execute without errors
- Test directly: `osascript -e 'tell application "System Events" to key code 126'`

#### 5. Scrolling Doesn't Work

**Problem:** Scroll commands don't scroll the page

**Solutions:**
- Ensure the window is focused (CLI auto-clicks before scrolling)
- Increase scroll amount: `960 540 scroll_down 20`
- Check if the app supports keyboard-based scrolling
- Some apps require mouse wheel events (not supported by cliclick)

#### 6. Special Characters Not Typing

**Problem:** Characters like `$`, `"`, `\` don't appear

**Solution:** These are automatically escaped in the latest version. If issues persist:
- Use the `type` command explicitly: `type Price: $100`
- Avoid using special chars in shorthand mode

#### 7. Modifier Keys Not Working

**Problem:** Cmd+C, Cmd+V, etc. don't work

**Solutions:**
- Use correct syntax: `press #c` (not `#c` alone in some contexts)
- Ensure modifiers are before the key: `#+z` not `z+#`
- For Cmd+Tab specifically, use: `press #tab`

#### 8. Slow Performance

**Problem:** Commands execute slowly

**Solutions:**
- Reduce batch delay: `-d 0.05` (minimum 20ms recommended)
- Use single command mode for one-off operations
- Check network latency: `ping your-vm-ip`
- Ensure VM has adequate resources (CPU, RAM)

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Add -m verbose flag to cliclick commands (modify script if needed)
# Or run with Python debugging:
python3 -u macos_actuation_control.py -c "test command" --username user
```

### Getting Help

If issues persist:
1. Check cliclick documentation: `cliclick -h`
2. Test cliclick directly on macOS VM
3. Verify SSH connection works independently
4. Review error messages in output

---

## Appendix

### Complete Command Reference Card

```
MOUSE COMMANDS
--------------
<x> <y> move               - Move cursor
<x> <y> left               - Left-click
<x> <y> right              - Right-click
<x> <y> double             - Double-click
<x> <y> triple             - Triple-click
<x> <y> middle             - Middle-click
<x> <y> drag <x2> <y2>     - Drag
<x> <y> hold               - Hold button
<x> <y> release            - Release button
<x> <y> scroll_up [n]      - Scroll up
<x> <y> scroll_down [n]    - Scroll down
<x> <y> scroll_left [n]    - Scroll left
<x> <y> scroll_right [n]   - Scroll right
here <action>              - Action at cursor

KEYBOARD COMMANDS
-----------------
type <text>                - Type text
press <keys>               - Press keys

MODIFIERS
---------
#  or  ⌘                   - Command
!  or  ⌥                   - Option/Alt
^  or  ⌃                   - Control
+  or  ⇧                   - Shift

SPECIAL KEYS
------------
{Enter}, {Tab}, {Esc}, {Space}
{Backspace}, {Delete}
{Up}, {Down}, {Left}, {Right}
{Home}, {End}, {PgUp}, {PgDn}
{F1}-{F16}
{VolumeUp}, {VolumeDown}, {Mute}
{BrightnessUp}, {BrightnessDown}

COMMON SHORTCUTS
----------------
#c         - Copy
#v         - Paste
#x         - Cut
#a         - Select All
#z         - Undo
#+z        - Redo
#space     - Spotlight
#tab       - App Switcher
#w         - Close Window
#q         - Quit App
```

---
 
**Last Updated:** January 11, 2026
**Developer:** Kartik (NullVoider)

---

## About This Project

This macOS actuation CLI tool was built from scratch through iterative testing and refinement. Every command, every feature, and every line of code was crafted to solve real automation challenges for Computer Use Agents.

If you find this tool useful, encounter bugs, or have feature requests, feel free to reach out directly via [X (formerly Twitter)](https://x.com/nullvoider07).