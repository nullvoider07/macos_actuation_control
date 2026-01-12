#!/usr/bin/env python3
"""
macOS VM Control CLI Tool - Enhanced Version
Intelligent middleware for CUA to control macOS VM mouse and keyboard
Uses cliclick for mouse control and osascript/cliclick for keyboard control
"""

import sys
import re
import time
import paramiko
import getpass
from typing import Optional, Tuple, List


class MacOSVMController:
    """Smart CLI tool for controlling macOS VM via SSH"""
    
    # Mouse action keywords
    MOUSE_ACTIONS = {
        'move', 'click', 'left', 'right', 'middle', 'double', 
        'triple', 'scroll_up', 'scroll_down', 'scroll_left', 'scroll_right',
        'drag', 'here', 'hold', 'release'
    }
    
    # Keyboard action keywords
    KEYBOARD_ACTIONS = {'type', 'press', 'key'}
    
    # 1. SPECIAL KEYS (Only keys supported by cliclick 'kp:')
    SPECIAL_KEYS = {
        # Function keys
        '{F1}': 'f1', '{F2}': 'f2', '{F3}': 'f3', '{F4}': 'f4',
        '{F5}': 'f5', '{F6}': 'f6', '{F7}': 'f7', '{F8}': 'f8',
        '{F9}': 'f9', '{F10}': 'f10', '{F11}': 'f11', '{F12}': 'f12',
        '{F13}': 'f13', '{F14}': 'f14', '{F15}': 'f15', '{F16}': 'f16',
        
        # Navigation & System
        '{Enter}': 'return', '{Return}': 'return',
        '{Tab}': 'tab', 
        '{Esc}': 'esc', '{Escape}': 'esc',
        '{Space}': 'space', 
        '{Backspace}': 'delete', '{BS}': 'delete',
        '{Delete}': 'fwd-delete', '{Del}': 'fwd-delete',
        '{Up}': 'arrow-up', '{Down}': 'arrow-down',
        '{Left}': 'arrow-left', '{Right}': 'arrow-right',
        '{Home}': 'home', '{End}': 'end',
        '{PgUp}': 'page-up', '{PgDn}': 'page-down',
        
        # Media (Supported by cliclick)
        '{VolumeUp}': 'volume-up',
        '{VolumeDown}': 'volume-down',
        '{Mute}': 'mute',
        '{BrightnessUp}': 'brightness-up',
        '{BrightnessDown}': 'brightness-down',
        '{PlayPause}': 'play-pause',
    }
    
    # 2. MODIFIER MAP (Used for kd/ku commands)
    # Maps both Symbols and Named Keys to cliclick modifier codes
    MODIFIER_MAP = {
        # Symbols
        '^': 'ctrl', '⌃': 'ctrl',
        '+': 'shift', '⇧': 'shift',
        '!': 'alt', '⌥': 'alt',
        '#': 'cmd', '⌘': 'cmd',
        
        # Names
        '{Cmd}': 'cmd', '{Command}': 'cmd',
        '{Option}': 'alt', '{Alt}': 'alt',
        '{Control}': 'ctrl', '{Ctrl}': 'ctrl',
        '{Shift}': 'shift',
        '{Fn}': 'fn'
    }
    
    # Initialization
    def __init__(self, host: str, username: str, port: int = 2222):
        """Initialize macOS VM controller with connection details"""
        self.host = host
        self.username = username
        self.port = port
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.connected = False
        self.cliclick_path = None
    
    # Establish SSH connection
    def connect(self, password: str) -> bool:
        """Establish persistent SSH connection"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            print(f"[*] Connecting to {self.username}@{self.host}:{self.port}...")
            self.ssh_client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10
            )
            
            # Find cliclick
            cliclick_path = self._find_cliclick()
            
            if not cliclick_path:
                print("[✗] cliclick not found. Please install it:")
                print("    brew install cliclick")
                print("\nOr download from: https://github.com/BlueM/cliclick")
                return False
            
            self.cliclick_path = cliclick_path
            print(f"[✓] Found cliclick at: {cliclick_path}")
            
            self.connected = True
            print(f"[✓] Connected successfully!")
            return True
            
        except paramiko.AuthenticationException:
            print("[✗] Authentication failed. Invalid credentials.")
            return False
        except paramiko.SSHException as e:
            print(f"[✗] SSH error: {e}")
            return False
        except Exception as e:
            print(f"[✗] Connection failed: {e}")
            return False
    
    # Find cliclick executable on remote macOS VM
    def _find_cliclick(self) -> Optional[str]:
        """Find cliclick executable"""
        known_path = '/usr/local/bin/cliclick'
        if self._test_cliclick(known_path):
            return known_path
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(
                'export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"; which cliclick'
            )
            path = stdout.read().decode().strip()
            if path and self._test_cliclick(path):
                return path
        except:
            pass

        # Check common installation paths
        common_paths = [
            '/opt/homebrew/bin/cliclick',
            '~/bin/cliclick',
            '/usr/bin/cliclick',
            '$HOME/.local/bin/cliclick',
        ]
        
        for path in common_paths:
            if self._test_cliclick(path):
                return path
        
        return None
    
    # Test if cliclick exists and is executable
    def _test_cliclick(self, path: str) -> bool:
        """Test if cliclick exists and is executable"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(f'test -x {path} && echo OK')
            return stdout.read().decode().strip() == 'OK'
        except:
            return False
    
    # Disconnect SSH
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            self.connected = False
            print("[*] Disconnected from macOS VM")
    
    # Detect command type
    def detect_command_type(self, command: str) -> Tuple[str, str]:
        """
        Smart detection of command type (mouse/keyboard)
        Returns: (type, command)
        """
        tokens = command.strip().split()
        
        if not tokens:
            return 'invalid', command
        
        # Check if starts with coordinates (numbers)
        if len(tokens) >= 2:
            try:
                int(tokens[0])
                int(tokens[1])
                # Has coordinates - likely mouse command
                if len(tokens) >= 3 and tokens[2] in self.MOUSE_ACTIONS:
                    return 'mouse', command
                elif len(tokens) == 2:
                    # Just coordinates, assume move
                    return 'mouse', f"{command} move"
            except ValueError:
                pass
        
        # Check for "here" keyword (mouse)
        if tokens[0] == 'here':
            if len(tokens) >= 2 and tokens[1] in self.MOUSE_ACTIONS:
                return 'mouse', command
            else:
                return 'invalid', command
        
        # Check for explicit keyboard actions
        if tokens[0] in self.KEYBOARD_ACTIONS:
            return 'keyboard', command
        
        # Check for modifier keys at start (supporting Unicode symbols)
        modifier_pattern = r'^[⌘⌥⌃⇧^+!#]'
        if re.match(modifier_pattern, command):
            return 'keyboard', f"press {command}"
        
        # Check for special keys OR modifiers (fix for press {Cmd})
        if any(key in command for key in self.SPECIAL_KEYS.keys()) or any(key in command for key in self.MODIFIER_MAP.keys()):
            if not command.startswith(tuple(self.KEYBOARD_ACTIONS)):
                return 'keyboard', f"press {command}"
            return 'keyboard', command
        
        # If first token is mouse action
        if tokens[0] in self.MOUSE_ACTIONS:
            return 'mouse', command
        
        # Default: assume it's text to type
        return 'keyboard', f"type {command}"
    
    # Build scroll command
    def build_scroll_command(self, x: Optional[int], y: Optional[int], 
                              direction: str, amount: int) -> str:
        """
        Helper: Simulates scrolling using an AppleScript repeat loop.
        Arguments:
            x, y: Optional coordinates to click (focus) before scrolling.
            direction: scroll_up/down/left/right
            amount: Number of 'notches' (key presses) to scroll.
        """
        # Map direction to AppleScript Key Codes
        # 126=Up, 125=Down, 123=Left, 124=Right
        if direction in ['scroll_up', 'scroll-up', 'scrollup']:
            key_code = 126
        elif direction in ['scroll_down', 'scroll-down', 'scrolldown']:
            key_code = 125
        elif direction in ['scroll_left', 'scroll-left', 'scrollleft']:
            key_code = 123
        elif direction in ['scroll_right', 'scroll-right', 'scrollright']:
            key_code = 124
        else:
            return ""
        
        # 1. Build Focus Command (Click to ensure window receives keys)
        if x is not None and y is not None:
            focus_cmd = f"{self.cliclick_path} c:{x},{y} w:50"
        else:
            focus_cmd = f"{self.cliclick_path} c:. w:50"
        scroll_cmd = (
            f"osascript -e 'tell application \"System Events\" to "
            f"repeat {amount} times' "
            f"-e 'key code {key_code}' "
            f"-e 'delay 0.02' "
            f"-e 'end repeat'"
        )
        return f"{focus_cmd} && {scroll_cmd}"
    
    # Build mouse command
    def build_mouse_command(self, command: str) -> str:
        """
        Build command for mouse actions.
        Routes scroll actions to the osascript helper for smooth scrolling.
        """
        tokens = command.strip().split()
        
        if not tokens or not self.cliclick_path:
            return ""
        
        cli = self.cliclick_path
        
        # --- CASE A: "here <action> [amount]" ---
        if tokens[0] == 'here':
            action = tokens[1] if len(tokens) > 1 else 'left'
            
            # Simple clicks
            if action in ['left', 'click']: return f"{cli} c:."
            elif action == 'right':         return f"{cli} rc:."
            elif action == 'double':        return f"{cli} dc:."
            elif action == 'triple':        return f"{cli} tc:."
            elif action == 'middle':        return f"{cli} mc:."
            elif action == 'hold':          return f"{cli} dd:."
            elif action == 'release':       return f"{cli} du:."
            
            # Scrolling (No coords needed)
            elif 'scroll' in action:
                # Parse amount (default to 5 if missing)
                amount = int(tokens[2]) if len(tokens) > 2 else 5
                return self.build_scroll_command(None, None, action, amount)
            return ""
        
        # --- CASE B: "x y <action> [amount]" ---
        try:
            x = int(tokens[0])
            y = int(tokens[1])
        except (ValueError, IndexError):
            return ""
        
        action = tokens[2].lower() if len(tokens) > 2 else 'move'
        
        if action == 'move':            return f"{cli} m:{x},{y}"
        elif action in ['left','click']: return f"{cli} c:{x},{y}"
        elif action == 'right':         return f"{cli} rc:{x},{y}"
        elif action == 'double':        return f"{cli} dc:{x},{y}"
        elif action == 'triple':        return f"{cli} tc:{x},{y}"
        elif action == 'middle':        return f"{cli} mc:{x},{y}"
        elif action == 'hold':          return f"{cli} dd:{x},{y}"
        elif action == 'release':       return f"{cli} du:{x},{y}"
        
        # Scrolling (With coords)
        elif 'scroll' in action:
            # Parse amount (default to 5 if missing)
            amount = int(tokens[3]) if len(tokens) > 3 else 5
            return self.build_scroll_command(x, y, action, amount)
        
        elif action == 'drag':
            if len(tokens) >= 5:
                try:
                    x2, y2 = int(tokens[3]), int(tokens[4])
                    return f"{cli} dd:{x},{y} m:{x2},{y2} du:{x2},{y2}"
                except ValueError: return ""
            return ""
        
        return ""
    
    # Parse keyboard command
    def parse_keyboard_command(self, command: str) -> str:
        """
        Parse keyboard command and convert to cliclick format
        Handles typing text and pressing keys with modifiers
        """
        tokens = command.strip().split(None, 1)
        
        if not tokens or not self.cliclick_path:
            return ""
        
        action = tokens[0]
        content = tokens[1] if len(tokens) > 1 else ""
        cli = self.cliclick_path
        
        if action == 'type':
            # Use cliclick for typing text
            # Escape special characters for shell
            escaped = content.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`').replace("'", "\\'")
            return f'{cli} t:"{escaped}"'
        
        elif action in ['press', 'key']:
            return self.build_key_press_command(content)
        
        return ""
    
    # Build key press command
    def build_key_press_command(self, key_combo: str) -> str:
        """
        FIXED: Robust translation from Shortcuts -> Cliclick sequences
        Correctly handles modifiers (kd/ku) and key presses
        """
        if not self.cliclick_path:
            return ""
        
        cli = self.cliclick_path
        modifiers = []
        main_key = key_combo
        
        # 1. Parse Modifier Symbols (^, +, !, #, and Unicode variants)
        i = 0
        while i < len(key_combo):
            char = key_combo[i]
            if char in self.MODIFIER_MAP:
                mod = self.MODIFIER_MAP[char]
                if mod not in modifiers:
                    modifiers.append(mod)
                i += 1
            else:
                break
        main_key = key_combo[i:]
        
        # 2. Handle Named Modifiers as the main key (e.g. "press {Cmd}")
        if main_key in self.MODIFIER_MAP:
            mod = self.MODIFIER_MAP[main_key]
            # To "tap" a modifier: hold, wait briefly, release
            return f"{cli} kd:{mod} w:50 ku:{mod}"
        
        # osascript handling for certain special keys
        osascript_map = {
            'return': 36, 'tab': 48, 
            'delete': 51, 'fwd-delete': 117,
            'page-up': 116, 'page-down': 121,
            'arrow-left': 123, 'arrow-right': 124,
            'arrow-down': 125, 'arrow-up': 126,
            'home': 115, 'end': 119
        }
        
        # Determine the normalized key name
        normalized_key = None
        if main_key in self.SPECIAL_KEYS:
            normalized_key = self.SPECIAL_KEYS[main_key]
            
        # Check against requested keys
        target_keys = [
            'return', 'tab', 'delete', 'fwd-delete', 
            'page-up', 'page-down', 'home', 'end',
            'arrow-left', 'arrow-right', 'arrow-down', 'arrow-up',
        ]
        
        if normalized_key in target_keys:
            code = osascript_map[normalized_key]
            
            # Build AppleScript command
            cmd = f'osascript -e \'tell application "System Events" to key code {code}'
            
            if modifiers:
                # Map cliclick modifiers to AppleScript syntax
                osa_mods = {
                    'cmd': 'command down', 'alt': 'option down',
                    'ctrl': 'control down', 'shift': 'shift down'
                }
                mod_list = [osa_mods[m] for m in modifiers if m in osa_mods]
                if mod_list:
                    cmd += f' using {{{", ".join(mod_list)}}}'
            
            cmd += "'"
            return cmd

        # 3. Handle Special Keys (cliclick fallback)
        if main_key in self.SPECIAL_KEYS:
            key_code = self.SPECIAL_KEYS[main_key]
            
            if modifiers:
                # Special key WITH modifiers: kd:cmd kp:tab ku:cmd
                mod_str = ','.join(modifiers)
                return f"{cli} kd:{mod_str} kp:{key_code} ku:{mod_str}"
            else:
                # Special key alone: kp:return
                return f"{cli} kp:{key_code}"
        
        # 4. Handle Single Characters (a, c, 1, space as text)
        if len(main_key) == 1:
            if modifiers:
                # Character WITH modifiers: kd:cmd t:c ku:cmd
                mod_str = ','.join(modifiers)
                return f"{cli} kd:{mod_str} t:{main_key} ku:{mod_str}"
            else:
                # Just a character alone: t:c
                return f"{cli} t:{main_key}"
        
        # 5. Handle "space" as a special case (when written as word)
        if main_key.lower() == 'space':
            if modifiers:
                mod_str = ','.join(modifiers)
                return f"{cli} kd:{mod_str} kp:space ku:{mod_str}"
            else:
                return f"{cli} kp:space"
        
        # 6. Handle Only Modifiers (e.g. "press #")
        if not main_key and modifiers:
            mod_str = ','.join(modifiers)
            return f"{cli} kd:{mod_str} w:50 ku:{mod_str}"
        
        # 7. Fallback: Unknown key - try typing it
        if main_key:
            if modifiers:
                mod_str = ','.join(modifiers)
                return f"{cli} kd:{mod_str} t:{main_key} ku:{mod_str}"
            else:
                return f"{cli} t:{main_key}"
        
        return ""
    
    def execute_command(self, command: str) -> bool:
        """Execute command on macOS VM"""
        if not self.connected:
            print("[✗] Not connected to VM")
            return False
        
        # Detect command type
        cmd_type, processed_cmd = self.detect_command_type(command)
        
        if cmd_type == 'invalid':
            print(f"[✗] Invalid command: {command}")
            return False
        
        # Build the appropriate command
        if cmd_type == 'mouse':
            remote_cmd = self.build_mouse_command(processed_cmd)
            prefix = "[MOUSE]"
        else:
            remote_cmd = self.parse_keyboard_command(processed_cmd)
            prefix = "[KEYBOARD]"
        
        if not remote_cmd:
            print(f"[✗] Failed to build command: {processed_cmd}")
            return False
        
        try:
            full_cmd = f'export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"; {remote_cmd}'
            
            # Execute command
            stdin, stdout, stderr = self.ssh_client.exec_command(full_cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            error_output = stderr.read().decode().strip()
            
            if exit_status != 0 and error_output:
                print(f"[✗] Command failed: {error_output}")
                return False
            
            # Enhanced feedback
            print(f"{prefix} Executed: {processed_cmd}")
            
            # Add smart delays for UI-opening commands
            ui_opening_patterns = [
                'cmd', 'spotlight', '#', '⌘',
                'kp:space -m cmd', 
                'kp:tab -m cmd',
                'kd:cmd'
            ]
            
            if any(pattern in remote_cmd for pattern in ui_opening_patterns):
                time.sleep(0.3)
            
            return True
            
        except Exception as e:
            print(f"[✗] Execution failed: {e}")
            return False
    
    # Batch mode execution
    def batch_mode(self, commands: List[str], delay: float = 0.1):
        """Execute a batch of commands with optional delays"""
        print(f"\n[*] Batch mode: Executing {len(commands)} commands...")
        
        for i, command in enumerate(commands, 1):
            if not command.strip() or command.strip().startswith('#'):
                continue
            
            print(f"\n[{i}/{len(commands)}] ", end="")
            self.execute_command(command.strip())
            
            if i < len(commands):
                time.sleep(delay)
        
        print("\n[✓] Batch execution complete!")
    
    # Interactive mode
    def interactive_mode(self):
        """Interactive command loop"""
        print("\n" + "="*70)
        print("  macOS VM Control - Interactive Mode")
        print("="*70)
        print("\nCommands:")
        print("  Mouse:    <x> <y> <action>     (e.g., 500 500 right)")
        print("  Mouse:    here <action>        (e.g., here left)")
        print("  Keyboard: type <text>          (e.g., type Hello World)")
        print("  Keyboard: press <keys>         (e.g., press #c)")
        print("  Special:  exit, quit           (disconnect)")
        print("  Special:  help                 (show detailed help)")
        print("="*70 + "\n")
        
        while self.connected:
            try:
                user_input = input("macOS> ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit']:
                    print("[*] Exiting...")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # Execute user command
                self.execute_command(user_input)
                
            except KeyboardInterrupt:
                print("\n[*] Interrupted. Type 'exit' to disconnect.")
            except EOFError:
                print("\n[*] EOF detected. Disconnecting...")
                break
        
        self.disconnect()
    
    # Display help information
    def show_help(self):
        """Display comprehensive help information"""
        help_text = """
╔══════════════════════════════════════════════════════════════════╗
║                   macOS COMMAND REFERENCE                        ║
╠══════════════════════════════════════════════════════════════════╣
║ MOUSE COMMANDS                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║ <x> <y> move              → Move cursor to coordinates           ║
║ <x> <y> click / left      → Move and left-click                  ║
║ <x> <y> right             → Move and right-click                 ║
║ <x> <y> double            → Move and double-click                ║
║ <x> <y> triple            → Move and triple-click                ║
║ <x> <y> middle            → Move and middle-click                ║
║ <x> <y> scroll_up [n]     → Move and scroll up                   ║
║ <x> <y> scroll_down [n]   → Move and scroll down                 ║
║ <x> <y> scroll_left [n]   → Move and scroll left                 ║
║ <x> <y> scroll_right [n]  → Move and scroll right                ║
║ <x> <y> drag <x2> <y2>    → Drag from (x,y) to (x2,y2)           ║
║ <x> <y> hold              → Press and hold at position           ║
║ <x> <y> release           → Release mouse button                 ║
║ here <action>             → Action at current cursor position    ║
╠══════════════════════════════════════════════════════════════════╣
║ KEYBOARD COMMANDS                                                ║
╠══════════════════════════════════════════════════════════════════╣
║ type <text>               → Type literal text                    ║
║ press <keys>              → Press keys/shortcuts                 ║
║                                                                  ║
║ Modifiers:                                                       ║
║   ^ or ⌃    → Control                                            ║
║   + or ⇧    → Shift                                              ║
║   ! or ⌥    → Option/Alt                                         ║
║   # or ⌘    → Command                                            ║
║                                                                  ║
║ Special Keys:                                                    ║
║   {Enter}, {Return}, {Tab}, {Esc}, {Space}                       ║
║   {Backspace}, {Delete}, {Up}, {Down}, {Left}, {Right}           ║
║   {Home}, {End}, {PgUp}, {PgDn}                                  ║
║   {F1}-{F16}, {Cmd}, {Option}, {Control}, {Shift}                ║
║   {VolumeUp}, {VolumeDown}, {Mute}                               ║
║   {BrightnessUp}, {BrightnessDown}                               ║
╠══════════════════════════════════════════════════════════════════╣
║ EXAMPLES                                                         ║
╠══════════════════════════════════════════════════════════════════╣
║ 960 540 right             → Right-click at center                ║
║ here left                 → Left-click at current position       ║
║ here right                → Right-click at current position      ║
║ 640 360 double            → Double-click at coordinates          ║
║ 640 360 triple            → Triple-click at coordinates          ║
║ 100 100 drag 500 500      → Drag from (100,100) to (500,500)     ║
║ 800 400 scroll_down 10    → Scroll down at position              ║
║ 800 400 scroll_left 5     → Scroll left at position              ║
║                                                                  ║
║ type Hello World          → Type text                            ║
║ press #c                  → Copy (Cmd+C)                         ║
║ press #v                  → Paste (Cmd+V)                        ║
║ press #+q                 → Force quit (Cmd+Shift+Q)             ║
║ press #space              → Open Spotlight (Cmd+Space)           ║
║ press ^!{Delete}          → Empty Trash (Ctrl+Option+Delete)     ║
║ press {F11}               → Show Desktop                         ║
║ {Enter}                   → Press Enter                          ║
║ {Cmd}                     → Press Command key                    ║
╠══════════════════════════════════════════════════════════════════╣
║ COMMON macOS SHORTCUTS                                           ║
╠══════════════════════════════════════════════════════════════════╣
║ #space                    → Spotlight Search                     ║
║ #tab                      → Application Switcher                 ║
║ #q                        → Quit Application                     ║
║ #w                        → Close Window                         ║
║ #m                        → Minimize Window                      ║
║ #h                        → Hide Application                     ║
║ #,                        → Preferences                          ║
║ #+3                       → Screenshot (selection)               ║
║ #+4                       → Screenshot (area)                    ║
║ ^{Up}                     → Mission Control                      ║
║ ^{Down}                   → Application Windows                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(help_text)

# Main entry point
def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='macOS VM Control CLI')
    parser.add_argument('-f', '--file', help='Execute commands from file (batch mode)')
    parser.add_argument('-c', '--command', help='Execute single command and exit')
    parser.add_argument('-d', '--delay', type=float, default=0.1, 
                       help='Delay between batch commands (seconds)')
    parser.add_argument('--host', help='Host (default: localhost)')
    parser.add_argument('--username', help='Username for SSH connection')
    parser.add_argument('--password', help='Password (not recommended, use prompt instead)')
    parser.add_argument('--port', type=int, default=2222, help='SSH port (default: 2222)')
    
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║             macOS VM Control CLI - CUA Integration               ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")
    
    # Get connection details
    host = args.host or input("Host (default: localhost): ").strip() or "localhost"
    username = args.username or input("Username: ").strip()
    
    if not username:
        print("[✗] Username is required")
        sys.exit(1)
    
    password = args.password or getpass.getpass("Password: ")
    
    # Create controller
    controller = MacOSVMController(host=host, username=username, port=args.port)
    
    # Connect
    if not controller.connect(password):
        sys.exit(1)
    
    # Execute based on mode
    if args.command:
        # Single command mode
        controller.execute_command(args.command)
        controller.disconnect()
    elif args.file:
        # Batch mode from file
        try:
            with open(args.file, 'r') as f:
                commands = f.readlines()
            controller.batch_mode(commands, delay=args.delay)
            controller.disconnect()
        except FileNotFoundError:
            print(f"[✗] File not found: {args.file}")
            sys.exit(1)
    else:
        # Interactive mode
        controller.interactive_mode()

# Entry point
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Interrupted. Exiting...")
        sys.exit(0)
