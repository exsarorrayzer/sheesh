import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from pathlib import Path
import threading
import time
import sys
import os
import subprocess
import shutil
from importlib import util

BASE = Path(__file__).resolve().parent
OBF_DIR = BASE / 'obsufucators'
RESULT_DIR = BASE / 'result'
if not RESULT_DIR.exists():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

def discover_module(name):
    path = OBF_DIR / f'{name}.py'
    if not path.exists():
        return None
    spec = util.spec_from_file_location(f'sheesh.obsufucators.{name}', str(path))
    if spec is None:
        return None
    m = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
        return m
    except Exception:
        return None

def apply_module_safe(source, module_name, callback=None):
    m = discover_module(module_name)
    if m is None:
        if callback:
            callback(f'⚠ Missing module: {module_name}')
        return source
    fn = getattr(m, 'obfuscate', None)
    if not callable(fn):
        if callback:
            callback(f'⚠ No obfuscate() in: {module_name}')
        return source
    try:
        result = fn(source)
        if callback:
            callback(f'✓ Applied: {module_name}')
        return result
    except Exception as e:
        if callback:
            callback(f'✗ Error in {module_name}: {e}')
        return source
COLORS = {'bg_dark': '#0A0A0F', 'bg_secondary': '#12121A', 'bg_tertiary': '#1A1A25', 'bg_card': '#141420', 'bg_card_hover': '#1C1C2E', 'red_primary': '#E63946', 'red_bright': '#FF4757', 'red_dark': '#B91C1C', 'red_glow': '#FF6B6B', 'red_muted': '#3D1111', 'red_muted2': '#5C1A1A', 'accent': '#FF2D2D', 'accent2': '#FF5252', 'text_primary': '#FFFFFF', 'text_secondary': '#A3A3B8', 'text_muted': '#555566', 'border': '#2A2A3A', 'border_active': '#E63946', 'success': '#22C55E', 'success_muted': '#0F3D1C', 'warning': '#F59E0B', 'warning_muted': '#3D2E0B', 'info': '#3B82F6', 'info_muted': '#0F1F3D', 'purple': '#A855F7', 'purple_muted': '#2E1065', 'gradient_start': '#1a0005', 'gradient_end': '#0A0A0F', 'tab_active': '#E63946', 'tab_inactive': '#1A1A25'}
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')
OBFUSCATION_MODULES = [
    ('variable_content_hider', 'Variable Content Hiding', '🔒', 'Encodes variable values with base64', True),
    ('comment_remover', 'Comment Removal', '🧹', 'Strips all comments and docstrings', True),
    ('print_hider', 'Print Removal', '🔇', 'Removes all print() statements', False),
    ('variable_randomizer', 'Variable Randomizer', '🎲', 'Randomizes all variable names', True),
    ('homoglyphs', 'Homoglyph Variables', '🔤', 'Randomizes variables with invisible homoglyphs', False),
    ('class_randomizer', 'Class Randomizer', '🏗️', 'Randomizes class names', True),
    ('string_encryptor', 'String Encryption', '🔐', 'Encrypts strings with XOR cipher', True),
    ('constant_pool', 'Constant Pool Table', '🗄️', 'Extracts and encrypts strings/ints into a dictionary', False),
    ('control_flow', 'Control Flow Flatten', '🌀', 'Flattens control flow into state machines', False),
    ('opaque_predicates', 'Opaque Predicates', '🧱', 'Injects always-true mathematical conditions', False),
    ('dead_code_injector', 'Dead Code Injection', '💀', 'Injects fake functions and classes', True),
    ('outlining', 'Function Outlining', '🧩', 'Moves inline math into dynamically created functions', False),
    ('anti_debug', 'Anti-Debug Protection', '🛡️', 'Adds debugger detection', False),
    ('anti_vm', 'Anti-VM & Sandbox', '🖥️', 'Detects VirtualBox, VMware and Sandboxes', False),
    ('integer_obfuscator', 'Integer Obfuscation', '🔢', 'Replaces integers with expressions', True),
    ('type_juggling', 'AST Type Juggling', '🎭', 'Replaces integers with bitwise XOR math', False),
    ('dynamic_imports', 'Dynamic Imports', '📦', 'Converts imports to __import__() calls', False),
    ('rename_builtins', 'Builtin Renaming', '🏷️', 'Aliases built-in function names', False),
    ('watermark', 'Watermark', '💧', 'Adds unique tracking watermark', False)
]
ENCRYPTION_MODULES = [('base64', 'Base64 Encoding', '📦'), ('hash', 'Hash Obfuscation (XOR)', '🔑'), ('marshallobf', 'Marshal Bytecode', '⚙️'), ('zlib_compressor', 'Zlib Compression', '📚')]

class PulseFrame(ctk.CTkFrame):

    def __init__(self, *args, pulse_color=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._pulse_color = pulse_color
        self._pulse_alpha = 0
        self._pulse_dir = 1

class SheeshObfuscatorApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title('🔥 SHEESH Obfuscator v3.0 PREMIUM')
        self.geometry('1300x850')
        self.configure(fg_color=COLORS['bg_dark'])
        self.resizable(True, True)
        self.minsize(1100, 700)
        self.selected_file = None
        self.encrypt_method = ctk.StringVar(value='all')
        self.processing = False
        self.module_vars = {}
        self.encryption_layers = ctk.IntVar(value=1)
        self.exe_onefile = ctk.BooleanVar(value=True)
        self.exe_noconsole = ctk.BooleanVar(value=False)
        self.exe_icon_path = ''
        self.exe_name = ctk.StringVar(value='')
        self.exe_extra_data = []
        self.exe_hidden_imports = []
        self._create_ui()

    def _create_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.main_frame.pack(fill='both', expand=True, padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_tab_view()
        self._create_footer()

    def _create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS['bg_card'], corner_radius=0, border_width=0)
        header_frame.grid(row=0, column=0, sticky='ew')
        gradient_bar = ctk.CTkFrame(header_frame, fg_color=COLORS['red_primary'], height=3, corner_radius=0)
        gradient_bar.pack(fill='x', side='top')
        inner = ctk.CTkFrame(header_frame, fg_color='transparent')
        inner.pack(fill='x', padx=30, pady=18)
        title_container = ctk.CTkFrame(inner, fg_color='transparent')
        title_container.pack(side='left')
        logo_label = ctk.CTkLabel(title_container, text='🔥', font=ctk.CTkFont(size=42))
        logo_label.pack(side='left', padx=(0, 15))
        title_text = ctk.CTkFrame(title_container, fg_color='transparent')
        title_text.pack(side='left')
        main_title = ctk.CTkLabel(title_text, text='SHEESH OBFUSCATOR', font=ctk.CTkFont(family='Segoe UI', size=32, weight='bold'), text_color=COLORS['red_primary'])
        main_title.pack(anchor='w')
        subtitle = ctk.CTkLabel(title_text, text='Advanced Python Protection Suite', font=ctk.CTkFont(size=13), text_color=COLORS['text_secondary'])
        subtitle.pack(anchor='w')
        right_frame = ctk.CTkFrame(inner, fg_color='transparent')
        right_frame.pack(side='right')
        version_frame = ctk.CTkFrame(right_frame, fg_color=COLORS['red_muted'], corner_radius=20, border_width=1, border_color=COLORS['red_primary'])
        version_frame.pack(side='right', padx=(10, 0))
        version_label = ctk.CTkLabel(version_frame, text='  v3.0 PREMIUM  ', font=ctk.CTkFont(size=11, weight='bold'), text_color=COLORS['red_bright'])
        version_label.pack(padx=15, pady=7)
        stats_frame = ctk.CTkFrame(right_frame, fg_color=COLORS['bg_tertiary'], corner_radius=20)
        stats_frame.pack(side='right', padx=(0, 10))
        module_count = len(OBFUSCATION_MODULES) + len(ENCRYPTION_MODULES)
        stats_label = ctk.CTkLabel(stats_frame, text=f'  {module_count} Modules Available  ', font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'])
        stats_label.pack(padx=12, pady=7)

    def _create_tab_view(self):
        tab_container = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        tab_container.grid(row=1, column=0, sticky='nsew', padx=20, pady=(15, 10))
        self.tabview = ctk.CTkTabview(tab_container, fg_color=COLORS['bg_card'], segmented_button_fg_color=COLORS['bg_tertiary'], segmented_button_selected_color=COLORS['red_primary'], segmented_button_selected_hover_color=COLORS['red_bright'], segmented_button_unselected_color=COLORS['bg_tertiary'], segmented_button_unselected_hover_color=COLORS['red_muted'], text_color=COLORS['text_primary'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        self.tabview.pack(fill='both', expand=True)
        self.tab_obfuscate = self.tabview.add('⚡ Obfuscator')
        self.tab_exe = self.tabview.add('📦 EXE Builder')
        self.tab_console = self.tabview.add('📟 Console')
        self._create_obfuscator_tab()
        self._create_exe_builder_tab()
        self._create_console_tab()

    def _create_obfuscator_tab(self):
        self.tab_obfuscate.grid_columnconfigure(0, weight=1, minsize=380)
        self.tab_obfuscate.grid_columnconfigure(1, weight=1, minsize=380)
        self.tab_obfuscate.grid_rowconfigure(0, weight=1)
        left_scroll = ctk.CTkScrollableFrame(self.tab_obfuscate, fg_color='transparent', scrollbar_button_color=COLORS['red_muted'], scrollbar_button_hover_color=COLORS['red_primary'])
        left_scroll.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)
        self._create_section_header(left_scroll, '📁 FILE SELECTION')
        file_card = self._create_card(left_scroll)
        self.file_label = ctk.CTkLabel(file_card, text='No file selected', font=ctk.CTkFont(size=13), text_color=COLORS['text_muted'], wraplength=320)
        self.file_label.pack(pady=(0, 12))
        select_btn = ctk.CTkButton(file_card, text='🔍 Browse Python File', font=ctk.CTkFont(size=14, weight='bold'), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], border_width=1, border_color=COLORS['red_primary'], corner_radius=10, height=45, command=self._select_file)
        select_btn.pack(fill='x')
        self._create_section_header(left_scroll, '🛠️ OBFUSCATION MODULES')
        for mod_id, mod_name, mod_icon, mod_desc, mod_default in OBFUSCATION_MODULES:
            var = ctk.BooleanVar(value=mod_default)
            self.module_vars[mod_id] = var
            self._create_module_toggle(left_scroll, mod_id, mod_name, mod_icon, mod_desc, var)
        right_scroll = ctk.CTkScrollableFrame(self.tab_obfuscate, fg_color='transparent', scrollbar_button_color=COLORS['red_muted'], scrollbar_button_hover_color=COLORS['red_primary'])
        right_scroll.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
        self._create_section_header(right_scroll, '🔐 ENCRYPTION METHOD')
        encrypt_card = self._create_card(right_scroll)
        all_radio = ctk.CTkRadioButton(encrypt_card, text='💎 All Methods (Maximum Protection)', variable=self.encrypt_method, value='all', font=ctk.CTkFont(size=13, weight='bold'), fg_color=COLORS['red_primary'], hover_color=COLORS['red_bright'], border_color=COLORS['red_muted'], text_color=COLORS['accent2'])
        all_radio.pack(anchor='w', pady=(0, 8))
        sep = ctk.CTkFrame(encrypt_card, fg_color=COLORS['border'], height=1)
        sep.pack(fill='x', pady=8)
        for value, label, icon in ENCRYPTION_MODULES:
            radio = ctk.CTkRadioButton(encrypt_card, text=f'{icon} {label}', variable=self.encrypt_method, value=value, font=ctk.CTkFont(size=13), fg_color=COLORS['red_primary'], hover_color=COLORS['red_bright'], border_color=COLORS['red_muted'], text_color=COLORS['text_primary'])
            radio.pack(anchor='w', pady=4)
        self._create_section_header(right_scroll, '🔄 ENCRYPTION LAYERS')
        layers_card = self._create_card(right_scroll)
        layers_label = ctk.CTkLabel(layers_card, text='Number of encryption passes:', font=ctk.CTkFont(size=13), text_color=COLORS['text_secondary'])
        layers_label.pack(anchor='w', pady=(0, 8))
        layers_frame = ctk.CTkFrame(layers_card, fg_color='transparent')
        layers_frame.pack(fill='x')
        self.layers_display = ctk.CTkLabel(layers_frame, text='1', font=ctk.CTkFont(size=24, weight='bold'), text_color=COLORS['red_primary'], width=50)
        self.layers_display.pack(side='left', padx=(0, 15))
        self.layers_slider = ctk.CTkSlider(layers_frame, from_=1, to=5, number_of_steps=4, variable=self.encryption_layers, fg_color=COLORS['bg_tertiary'], progress_color=COLORS['red_primary'], button_color=COLORS['red_bright'], button_hover_color=COLORS['accent'], command=self._on_layers_change)
        self.layers_slider.pack(side='left', fill='x', expand=True)
        layers_info = ctk.CTkFrame(layers_card, fg_color=COLORS['warning_muted'], corner_radius=8)
        layers_info.pack(fill='x', pady=(12, 0))
        ctk.CTkLabel(layers_info, text='⚠️ More layers = bigger file but harder to reverse', font=ctk.CTkFont(size=11), text_color=COLORS['warning']).pack(pady=6, padx=10)
        self._create_section_header(right_scroll, '🚀 ACTIONS')
        action_card = self._create_card(right_scroll)
        presets_frame = ctk.CTkFrame(action_card, fg_color='transparent')
        presets_frame.pack(fill='x', pady=(0, 12))
        ctk.CTkButton(presets_frame, text='🟢 Light', font=ctk.CTkFont(size=12), fg_color=COLORS['success_muted'], hover_color=COLORS['success'], text_color=COLORS['success'], corner_radius=8, height=32, width=90, command=lambda: self._apply_preset('light')).pack(side='left', padx=(0, 5))
        ctk.CTkButton(presets_frame, text='🟡 Medium', font=ctk.CTkFont(size=12), fg_color=COLORS['warning_muted'], hover_color=COLORS['warning'], text_color=COLORS['warning'], corner_radius=8, height=32, width=90, command=lambda: self._apply_preset('medium')).pack(side='left', padx=(0, 5))
        ctk.CTkButton(presets_frame, text='🔴 Maximum', font=ctk.CTkFont(size=12), fg_color=COLORS['red_muted'], hover_color=COLORS['red_primary'], text_color=COLORS['red_bright'], corner_radius=8, height=32, width=90, command=lambda: self._apply_preset('maximum')).pack(side='left', padx=(0, 5))
        ctk.CTkButton(presets_frame, text='⚪ None', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['border'], text_color=COLORS['text_muted'], corner_radius=8, height=32, width=70, command=lambda: self._apply_preset('none')).pack(side='left')
        self.obfuscate_btn = ctk.CTkButton(action_card, text='⚡ OBFUSCATE NOW', font=ctk.CTkFont(size=18, weight='bold'), fg_color=COLORS['red_primary'], hover_color=COLORS['red_bright'], corner_radius=12, height=60, command=self._start_obfuscation)
        self.obfuscate_btn.pack(fill='x', pady=(0, 12))
        self.progress_bar = ctk.CTkProgressBar(action_card, fg_color=COLORS['bg_tertiary'], progress_color=COLORS['red_primary'], height=6, corner_radius=3)
        self.progress_bar.pack(fill='x')
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(action_card, text='', font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'])
        self.progress_label.pack(anchor='w', pady=(5, 0))

    def _create_exe_builder_tab(self):
        self.tab_exe.grid_columnconfigure(0, weight=1, minsize=380)
        self.tab_exe.grid_columnconfigure(1, weight=1, minsize=380)
        self.tab_exe.grid_rowconfigure(0, weight=1)
        left_scroll = ctk.CTkScrollableFrame(self.tab_exe, fg_color='transparent', scrollbar_button_color=COLORS['red_muted'], scrollbar_button_hover_color=COLORS['red_primary'])
        left_scroll.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)
        self._create_section_header(left_scroll, '📁 SOURCE FILE')
        src_card = self._create_card(left_scroll)
        self.exe_file_label = ctk.CTkLabel(src_card, text='No file selected (uses obfuscator file or select new)', font=ctk.CTkFont(size=12), text_color=COLORS['text_muted'], wraplength=320)
        self.exe_file_label.pack(pady=(0, 10))
        btn_frame = ctk.CTkFrame(src_card, fg_color='transparent')
        btn_frame.pack(fill='x')
        ctk.CTkButton(btn_frame, text='🔍 Browse .py File', font=ctk.CTkFont(size=13, weight='bold'), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], border_width=1, border_color=COLORS['red_primary'], corner_radius=10, height=40, command=self._select_exe_file).pack(fill='x', pady=(0, 5))
        ctk.CTkButton(btn_frame, text='📂 Use Last Obfuscated Output', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=10, height=35, command=self._use_last_obfuscated).pack(fill='x')
        self._create_section_header(left_scroll, '⚙️ BUILD SETTINGS')
        settings_card = self._create_card(left_scroll)
        name_frame = ctk.CTkFrame(settings_card, fg_color='transparent')
        name_frame.pack(fill='x', pady=(0, 10))
        ctk.CTkLabel(name_frame, text='Output Name:', font=ctk.CTkFont(size=13), text_color=COLORS['text_secondary']).pack(anchor='w', pady=(0, 5))
        self.exe_name_entry = ctk.CTkEntry(name_frame, placeholder_text='output (leave empty for auto)', textvariable=self.exe_name, fg_color=COLORS['bg_dark'], border_color=COLORS['border'], text_color=COLORS['text_primary'], corner_radius=8, height=38)
        self.exe_name_entry.pack(fill='x')
        sep1 = ctk.CTkFrame(settings_card, fg_color=COLORS['border'], height=1)
        sep1.pack(fill='x', pady=10)
        self.onefile_check = ctk.CTkCheckBox(settings_card, text='📁 Single File (--onefile)', variable=self.exe_onefile, font=ctk.CTkFont(size=13), fg_color=COLORS['red_primary'], hover_color=COLORS['red_bright'], border_color=COLORS['red_muted'], checkmark_color=COLORS['text_primary'], text_color=COLORS['text_primary'])
        self.onefile_check.pack(anchor='w', pady=5)
        self.noconsole_check = ctk.CTkCheckBox(settings_card, text='🖥️ No Console (--noconsole)', variable=self.exe_noconsole, font=ctk.CTkFont(size=13), fg_color=COLORS['red_primary'], hover_color=COLORS['red_bright'], border_color=COLORS['red_muted'], checkmark_color=COLORS['text_primary'], text_color=COLORS['text_primary'])
        self.noconsole_check.pack(anchor='w', pady=5)
        right_scroll = ctk.CTkScrollableFrame(self.tab_exe, fg_color='transparent', scrollbar_button_color=COLORS['red_muted'], scrollbar_button_hover_color=COLORS['red_primary'])
        right_scroll.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
        self._create_section_header(right_scroll, '🎨 CUSTOMIZATION')
        custom_card = self._create_card(right_scroll)
        icon_frame = ctk.CTkFrame(custom_card, fg_color='transparent')
        icon_frame.pack(fill='x', pady=(0, 10))
        ctk.CTkLabel(icon_frame, text='Application Icon:', font=ctk.CTkFont(size=13), text_color=COLORS['text_secondary']).pack(anchor='w', pady=(0, 5))
        icon_btn_frame = ctk.CTkFrame(icon_frame, fg_color='transparent')
        icon_btn_frame.pack(fill='x')
        self.icon_label = ctk.CTkLabel(icon_btn_frame, text='No icon selected', font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'])
        self.icon_label.pack(side='left', padx=(0, 10))
        ctk.CTkButton(icon_btn_frame, text='Steal from .exe', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=8, height=30, width=100, command=self._steal_icon).pack(side='right')
        ctk.CTkButton(icon_btn_frame, text='Browse .ico', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=8, height=30, width=100, command=self._select_icon).pack(side='right', padx=(0, 5))
        sep2 = ctk.CTkFrame(custom_card, fg_color=COLORS['border'], height=1)
        sep2.pack(fill='x', pady=10)
        ctk.CTkLabel(custom_card, text='Extra Data Files (--add-data):', font=ctk.CTkFont(size=13), text_color=COLORS['text_secondary']).pack(anchor='w', pady=(0, 5))
        data_btn_frame = ctk.CTkFrame(custom_card, fg_color='transparent')
        data_btn_frame.pack(fill='x')
        ctk.CTkButton(data_btn_frame, text='➕ Add File', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=8, height=30, width=90, command=self._add_extra_data).pack(side='left', padx=(0, 5))
        ctk.CTkButton(data_btn_frame, text='➕ Add Folder', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=8, height=30, width=100, command=self._add_extra_folder).pack(side='left', padx=(0, 5))
        ctk.CTkButton(data_btn_frame, text='🗑️ Clear', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=8, height=30, width=70, command=self._clear_extra_data).pack(side='left')
        self.extra_data_display = ctk.CTkTextbox(custom_card, fg_color=COLORS['bg_dark'], text_color=COLORS['text_secondary'], font=ctk.CTkFont(family='Consolas', size=11), height=60, corner_radius=8)
        self.extra_data_display.pack(fill='x', pady=(8, 0))
        self.extra_data_display.configure(state='disabled')
        sep3 = ctk.CTkFrame(custom_card, fg_color=COLORS['border'], height=1)
        sep3.pack(fill='x', pady=10)
        ctk.CTkLabel(custom_card, text='Manual Hidden Imports:', font=ctk.CTkFont(size=13), text_color=COLORS['text_secondary']).pack(anchor='w', pady=(0, 5))
        hi_btn_frame = ctk.CTkFrame(custom_card, fg_color='transparent')
        hi_btn_frame.pack(fill='x')
        self.manual_import_entry = ctk.CTkEntry(hi_btn_frame, placeholder_text='module_name', width=140, fg_color=COLORS['bg_dark'], border_color=COLORS['border'], height=30)
        self.manual_import_entry.pack(side='left', padx=(0, 5))
        ctk.CTkButton(hi_btn_frame, text='➕ Add', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=8, height=30, width=60, command=self._add_hidden_import).pack(side='left')
        ctk.CTkButton(hi_btn_frame, text='🗑️ Clear', font=ctk.CTkFont(size=12), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], corner_radius=8, height=30, width=60, command=self._clear_hidden_imports).pack(side='right')
        self.hidden_imports_display = ctk.CTkTextbox(custom_card, fg_color=COLORS['bg_dark'], text_color=COLORS['text_secondary'], font=ctk.CTkFont(family='Consolas', size=11), height=60, corner_radius=8)
        self.hidden_imports_display.pack(fill='x', pady=(8, 0))
        self.hidden_imports_display.configure(state='disabled')
        self._create_section_header(right_scroll, '🏗️ BUILD')
        build_card = self._create_card(right_scroll)
        pyinstaller_info = ctk.CTkFrame(build_card, fg_color=COLORS['info_muted'], corner_radius=8)
        pyinstaller_info.pack(fill='x', pady=(0, 12))
        ctk.CTkLabel(pyinstaller_info, text='ℹ️ Requires PyInstaller: pip install pyinstaller', font=ctk.CTkFont(size=11), text_color=COLORS['info']).pack(pady=6, padx=10)
        self.build_btn = ctk.CTkButton(build_card, text='🏗️ BUILD EXE', font=ctk.CTkFont(size=18, weight='bold'), fg_color=COLORS['purple'], hover_color='#C084FC', corner_radius=12, height=60, command=self._start_exe_build)
        self.build_btn.pack(fill='x', pady=(0, 12))
        self.build_progress = ctk.CTkProgressBar(build_card, fg_color=COLORS['bg_tertiary'], progress_color=COLORS['purple'], height=6, corner_radius=3, mode='indeterminate')
        self.build_progress.pack(fill='x')
        self.build_progress.set(0)
        self.build_status = ctk.CTkLabel(build_card, text='', font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'])
        self.build_status.pack(anchor='w', pady=(5, 0))
        obf_then_build_card = self._create_card(right_scroll)
        self.obf_build_btn = ctk.CTkButton(obf_then_build_card, text='⚡ OBFUSCATE + BUILD EXE', font=ctk.CTkFont(size=15, weight='bold'), fg_color=COLORS['red_dark'], hover_color=COLORS['red_primary'], corner_radius=12, height=50, command=self._start_obfuscate_and_build)
        self.obf_build_btn.pack(fill='x')
        ctk.CTkLabel(obf_then_build_card, text='Obfuscates first, then builds EXE from result', font=ctk.CTkFont(size=11), text_color=COLORS['text_muted']).pack(anchor='w', pady=(5, 0))

    def _create_console_tab(self):
        self.tab_console.grid_columnconfigure(0, weight=1)
        self.tab_console.grid_rowconfigure(1, weight=1)
        console_header = ctk.CTkFrame(self.tab_console, fg_color=COLORS['bg_secondary'], corner_radius=10)
        console_header.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        header_inner = ctk.CTkFrame(console_header, fg_color='transparent')
        header_inner.pack(fill='x', padx=15, pady=10)
        console_title = ctk.CTkLabel(header_inner, text='📟 CONSOLE OUTPUT', font=ctk.CTkFont(size=14, weight='bold'), text_color=COLORS['red_primary'])
        console_title.pack(side='left')
        ctk.CTkButton(header_inner, text='📋 Copy', font=ctk.CTkFont(size=11), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], width=60, height=28, corner_radius=8, command=self._copy_console).pack(side='right', padx=(5, 0))
        ctk.CTkButton(header_inner, text='🗑️ Clear', font=ctk.CTkFont(size=11), fg_color=COLORS['bg_tertiary'], hover_color=COLORS['red_muted'], width=60, height=28, corner_radius=8, command=self._clear_console).pack(side='right')
        self.console = ctk.CTkTextbox(self.tab_console, fg_color=COLORS['bg_dark'], text_color=COLORS['text_primary'], font=ctk.CTkFont(family='Consolas', size=12), corner_radius=10, border_width=1, border_color=COLORS['border'], scrollbar_button_color=COLORS['red_muted'], scrollbar_button_hover_color=COLORS['red_primary'])
        self.console.grid(row=1, column=0, sticky='nsew', padx=10, pady=(5, 10))
        self._log_welcome()

    def _create_footer(self):
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS['bg_card'], corner_radius=0, height=40)
        footer_frame.grid(row=2, column=0, sticky='ew')
        inner = ctk.CTkFrame(footer_frame, fg_color='transparent')
        inner.pack(fill='x', padx=30, pady=8)
        credits = ctk.CTkLabel(inner, text='Made with ❤️ by Sheesh Team', font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'])
        credits.pack(side='left')
        self.status_label = ctk.CTkLabel(inner, text='● Ready', font=ctk.CTkFont(size=11), text_color=COLORS['success'])
        self.status_label.pack(side='right')

    def _create_section_header(self, parent, text):
        header = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=13, weight='bold'), text_color=COLORS['red_bright'])
        header.pack(anchor='w', pady=(18, 8))

    def _create_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], corner_radius=12, border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=(0, 5))
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='both', padx=15, pady=15)
        return inner

    def _create_module_toggle(self, parent, mod_id, mod_name, icon, description, var):
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], corner_radius=10, border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=2)
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='x', padx=12, pady=8)
        check = ctk.CTkCheckBox(inner, text=f'{icon} {mod_name}', variable=var, font=ctk.CTkFont(size=12), fg_color=COLORS['red_primary'], hover_color=COLORS['red_bright'], border_color=COLORS['red_muted'], checkmark_color=COLORS['text_primary'], text_color=COLORS['text_primary'], width=30)
        check.pack(anchor='w')
        desc_label = ctk.CTkLabel(inner, text=description, font=ctk.CTkFont(size=10), text_color=COLORS['text_muted'])
        desc_label.pack(anchor='w', padx=(28, 0))

    def _on_layers_change(self, value):
        self.layers_display.configure(text=str(int(value)))

    def _apply_preset(self, preset):
        light_on = {'variable_content_hider', 'comment_remover', 'variable_randomizer'}
        medium_on = light_on | {'class_randomizer', 'string_encryptor', 'dead_code_injector', 'integer_obfuscator'}
        maximum_on = {mod_id for mod_id, _, _, _, _ in OBFUSCATION_MODULES}
        if preset == 'light':
            targets = light_on
            self.encryption_layers.set(1)
        elif preset == 'medium':
            targets = medium_on
            self.encryption_layers.set(2)
        elif preset == 'maximum':
            targets = maximum_on
            self.encryption_layers.set(4)
        else:
            targets = set()
            self.encryption_layers.set(1)
        for mod_id, var in self.module_vars.items():
            var.set(mod_id in targets)
        self._on_layers_change(self.encryption_layers.get())

    def _log_welcome(self):
        self._log_to_console('╔════════════════════════════════════════════════════════════════╗')
        self._log_to_console('║             🔥 SHEESH OBFUSCATOR v3.0 PREMIUM 🔥               ║')
        self._log_to_console('╠════════════════════════════════════════════════════════════════╣')
        self._log_to_console('║  Advanced Python Protection Suite                             ║')
        self._log_to_console('║                                                                ║')
        self._log_to_console('║  Features:                                                     ║')
        self._log_to_console('║  • Variable Content Hiding    • String Encryption              ║')
        self._log_to_console('║  • Comment Removal            • Control Flow Flattening        ║')
        self._log_to_console('║  • Print Removal              • Dead Code Injection            ║')
        self._log_to_console('║  • Variable Randomization     • Anti-Debug Protection          ║')
        self._log_to_console('║  • Class Randomization        • Integer Obfuscation            ║')
        self._log_to_console('║  • Multiple Encryption Layers • Dynamic Import Rewriting       ║')
        self._log_to_console('║  • Builtin Renaming           • Watermarking                   ║')
        self._log_to_console('║  • 🆕 EXE Builder (PyInstaller)                                ║')
        self._log_to_console('║  • 🆕 Preset Modes (Light/Medium/Maximum)                      ║')
        self._log_to_console('║  • 🆕 Multi-Layer Encryption (1-5 passes)                      ║')
        self._log_to_console('╚════════════════════════════════════════════════════════════════╝')
        self._log_to_console('')
        self._log_to_console('[*] Ready. Select a Python file to begin...')

    def _select_file(self):
        file_path = filedialog.askopenfilename(title='Select Python File', filetypes=[('Python Files', '*.py'), ('All Files', '*.*')])
        if file_path:
            self.selected_file = Path(file_path)
            display_name = str(self.selected_file)
            if len(display_name) > 45:
                display_name = f'...{display_name[-42:]}'
            self.file_label.configure(text=f'📄 {display_name}', text_color=COLORS['success'])
            self._log_to_console(f'\n[+] Selected file: {self.selected_file}')

    def _select_exe_file(self):
        file_path = filedialog.askopenfilename(title='Select Python File for EXE', filetypes=[('Python Files', '*.py'), ('All Files', '*.*')])
        if file_path:
            self._exe_source = Path(file_path)
            display = str(self._exe_source)
            if len(display) > 45:
                display = f'...{display[-42:]}'
            self.exe_file_label.configure(text=f'📄 {display}', text_color=COLORS['success'])
            self._log_to_console(f'\n[+] EXE source: {self._exe_source}')

    def _use_last_obfuscated(self):
        results = list(RESULT_DIR.glob('*_obfuscated.py'))
        if not results:
            messagebox.showwarning('No Output', 'No obfuscated files found in result directory!')
            return
        latest = max(results, key=lambda f: f.stat().st_mtime)
        self._exe_source = latest
        self.exe_file_label.configure(text=f'📄 {latest.name}', text_color=COLORS['success'])
        self._log_to_console(f'\n[+] Using obfuscated: {latest}')

    def _select_icon(self):
        icon_path = filedialog.askopenfilename(title='Select Icon', filetypes=[('Icon Files', '*.ico'), ('All Files', '*.*')])
        if icon_path:
            self.exe_icon_path = icon_path
            self.icon_label.configure(text=Path(icon_path).name, text_color=COLORS['success'])

    def _steal_icon(self):
        file_path = filedialog.askopenfilename(title='Select EXE to Steal Icon From', filetypes=[('Executables', '*.exe'), ('All Files', '*.*')])
        if not file_path:
            return
        try:
            from PIL import Image
            output_png = RESULT_DIR / 'temp_icon.png'
            if output_png.exists():
                output_png.unlink()
            escaped_src = str(file_path).replace("'", "''")
            escaped_dst = str(output_png).replace("'", "''")
            ps_script = f"\n            Add-Type -AssemblyName System.Drawing\n            $icon = [System.Drawing.Icon]::ExtractAssociatedIcon('{escaped_src}')\n            $bitmap = $icon.ToBitmap()\n            $bitmap.Save('{escaped_dst}')\n            "
            subprocess.run(['powershell', '-Command', ps_script], check=True, creationflags=134217728)
            if output_png.exists():
                img = Image.open(output_png)
                output_ico_path = RESULT_DIR / f'{Path(file_path).stem}_icon.ico'
                img.save(output_ico_path, format='ICO', sizes=[(256, 256)])
                try:
                    output_png.unlink()
                except Exception:
                    pass
                self.exe_icon_path = str(output_ico_path)
                self.icon_label.configure(text=output_ico_path.name, text_color=COLORS['success'])
                messagebox.showinfo('Success', f'Icon extracted!\nSaved to: {output_ico_path.name}')
            else:
                raise Exception('Failed to extract icon (PowerShell script error)')
        except Exception as e:
            messagebox.showerror('Icon Error', f'Could not extract icon: {e}\nEnsure Pillow is installed (pip install pillow).')

    def _add_extra_data(self):
        file_path = filedialog.askopenfilename(title='Select Data File')
        if file_path:
            self.exe_extra_data.append(file_path)
            self._update_extra_data_display()

    def _add_extra_folder(self):
        folder = filedialog.askdirectory(title='Select Data Folder')
        if folder:
            self.exe_extra_data.append(folder)
            self._update_extra_data_display()

    def _clear_extra_data(self):
        self.exe_extra_data.clear()
        self._update_extra_data_display()

    def _update_extra_data_display(self):
        self.extra_data_display.configure(state='normal')
        self.extra_data_display.delete('1.0', 'end')
        for d in self.exe_extra_data:
            self.extra_data_display.insert('end', f'{d}\n')
        self.extra_data_display.configure(state='disabled')

    def _add_hidden_import(self):
        val = self.manual_import_entry.get().strip()
        if val and val not in self.exe_hidden_imports:
            self.exe_hidden_imports.append(val)
            self._update_hidden_imports_display()
            self.manual_import_entry.delete(0, 'end')

    def _clear_hidden_imports(self):
        self.exe_hidden_imports.clear()
        self._update_hidden_imports_display()

    def _update_hidden_imports_display(self):
        self.hidden_imports_display.configure(state='normal')
        self.hidden_imports_display.delete('1.0', 'end')
        for imp in self.exe_hidden_imports:
            self.hidden_imports_display.insert('end', f'{imp}\n')
        self.hidden_imports_display.configure(state='disabled')

    def _log_to_console(self, message):
        self.console.configure(state='normal')
        self.console.insert('end', message + '\n')
        self.console.see('end')
        self.console.configure(state='disabled')

    def _clear_console(self):
        self.console.configure(state='normal')
        self.console.delete('1.0', 'end')
        self.console.configure(state='disabled')
        self._log_to_console('[*] Console cleared.\n')

    def _copy_console(self):
        self.console.configure(state='normal')
        content = self.console.get('1.0', 'end')
        self.console.configure(state='disabled')
        self.clipboard_clear()
        self.clipboard_append(content)
        self._update_status('Copied!', COLORS['success'])

    def _update_status(self, text, color):
        self.status_label.configure(text=f'● {text}', text_color=color)

    def _start_obfuscation(self):
        if self.processing:
            messagebox.showwarning('Processing', 'Already in progress!')
            return
        if not self.selected_file or not self.selected_file.exists():
            messagebox.showerror('Error', 'Please select a valid Python file!')
            return
        self.processing = True
        self.obfuscate_btn.configure(state='disabled', text='⏳ Processing...')
        self._update_status('Obfuscating...', COLORS['warning'])
        self.tabview.set('📟 Console')
        thread = threading.Thread(target=self._run_obfuscation, daemon=True)
        thread.start()

    def _run_obfuscation(self):
        try:
            self._log_to_console('\n' + '═' * 65)
            self._log_to_console('🚀 STARTING OBFUSCATION PIPELINE')
            self._log_to_console('═' * 65)
            self._log_to_console(f'\n[*] Reading source file...')
            src = self.selected_file.read_text(encoding='utf-8')
            self._log_to_console(f'[+] Loaded {len(src):,} characters')
            self._log_to_console('[*] Scanning imports for PyInstaller compatibility...')
            try:
                from utils.import_scanner import scan_imports
                found_imports = scan_imports(src)
                new_imports = [imp for imp in found_imports if imp not in self.exe_hidden_imports]
                if new_imports:
                    count = len(new_imports)
                    display_str = ', '.join(new_imports[:3]) + ('...' if count > 3 else '')
                    self._log_to_console(f'    Found {count} imports: {display_str}')
                    self._log_to_console('    Adding to manual hidden imports list...')
                    self.exe_hidden_imports.extend(new_imports)
                    self.after(0, self._update_hidden_imports_display)
                else:
                    self._log_to_console('    No new hidden imports needed.')
            except Exception as e:
                self._log_to_console(f'    [!] Import scan warning: {e}')
            data = src
            enabled_modules = [mod_id for mod_id in [m[0] for m in OBFUSCATION_MODULES] if mod_id in self.module_vars and self.module_vars[mod_id].get()]
            total_steps = len(enabled_modules) + 2
            current_step = 0

            def log_callback(msg):
                self.after(0, lambda: self._log_to_console(f'    {msg}'))

            def update_progress():
                nonlocal current_step
                current_step += 1
                progress = current_step / total_steps
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                self.after(0, lambda s=current_step, t=total_steps: self.progress_label.configure(text=f'Step {s}/{t}'))
            for i, mod_id in enumerate(enabled_modules, 1):
                mod_info = next((m for m in OBFUSCATION_MODULES if m[0] == mod_id), None)
                display_name = mod_info[1] if mod_info else mod_id
                self._log_to_console(f'\n[*] Step {i}/{len(enabled_modules)} - {display_name}...')
                data = apply_module_safe(data, mod_id, log_callback)
                update_progress()
                time.sleep(0.2)
            method = self.encrypt_method.get()
            layers = self.encryption_layers.get()
            if method == 'all':
                encrypt_order = ['base64', 'hash', 'marshallobf', 'zlib_compressor']
            else:
                encrypt_order = [method]
            self._log_to_console(f'\n[*] Applying encryption ({layers} layer(s))...')
            for layer in range(layers):
                if layers > 1:
                    self._log_to_console(f'\n  ── Layer {layer + 1}/{layers} ──')
                for enc in encrypt_order:
                    self._log_to_console(f'    → Processing: {enc}')
                    data = apply_module_safe(data, enc, log_callback)
                    time.sleep(0.1)
            update_progress()
            self._log_to_console('\n[*] Adding comment bloat...')
            data = apply_module_safe(data, 'comment_adder', log_callback)
            update_progress()
            out_name = f'{self.selected_file.stem}_obfuscated.py'
            out_path = RESULT_DIR / out_name
            out_path.write_text(data, encoding='utf-8')
            self._last_output = out_path
            self._log_to_console('\n' + '═' * 65)
            self._log_to_console('✅ OBFUSCATION COMPLETE!')
            self._log_to_console('═' * 65)
            self._log_to_console(f'\n📁 Output: {out_path}')
            self._log_to_console(f'📊 Original size: {len(src):,} bytes')
            self._log_to_console(f'📊 Obfuscated size: {len(data):,} bytes')
            increase = (len(data) / max(len(src), 1) - 1) * 100
            self._log_to_console(f'📊 Size increase: {increase:.1f}%')
            self._log_to_console(f'🔧 Modules used: {len(enabled_modules)}')
            self._log_to_console(f'🔐 Encryption layers: {layers}')
            self.after(0, lambda: self._update_status('Complete!', COLORS['success']))
            self.after(0, lambda: messagebox.showinfo('Success', f'Obfuscation complete!\n\nOutput saved to:\n{out_path}'))
        except Exception as e:
            self._log_to_console(f'\n❌ ERROR: {e}')
            self.after(0, lambda: self._update_status('Error!', COLORS['red_primary']))
            self.after(0, lambda: messagebox.showerror('Error', str(e)))
        finally:
            self.processing = False
            self.after(0, lambda: self.obfuscate_btn.configure(state='normal', text='⚡ OBFUSCATE NOW'))
            self.after(0, lambda: self.progress_bar.set(0))
            self.after(0, lambda: self.progress_label.configure(text=''))

    def _start_exe_build(self):
        if self.processing:
            messagebox.showwarning('Processing', 'Already in progress!')
            return
        source = getattr(self, '_exe_source', None)
        if source is None or not Path(source).exists():
            messagebox.showerror('Error', 'Please select a Python file for EXE building!')
            return
        self.processing = True
        self.build_btn.configure(state='disabled', text='⏳ Building...')
        self._update_status('Building EXE...', COLORS['warning'])
        self.build_progress.start()
        self.tabview.set('📟 Console')
        thread = threading.Thread(target=self._run_exe_build, args=(Path(source),), daemon=True)
        thread.start()

    def _start_obfuscate_and_build(self):
        if self.processing:
            messagebox.showwarning('Processing', 'Already in progress!')
            return
        if not self.selected_file or not self.selected_file.exists():
            messagebox.showerror('Error', 'Please select a file in the Obfuscator tab first!')
            return
        self.processing = True
        self.obf_build_btn.configure(state='disabled', text='⏳ Processing...')
        self._update_status('Obfuscate + Build...', COLORS['warning'])
        self.tabview.set('📟 Console')

        def combined_task():
            self._run_obfuscation()
            out = getattr(self, '_last_output', None)
            if out and out.exists():
                self.after(0, lambda: self.build_progress.start())
                self._run_exe_build(out)
            self.after(0, lambda: self.obf_build_btn.configure(state='normal', text='⚡ OBFUSCATE + BUILD EXE'))
        thread = threading.Thread(target=combined_task, daemon=True)
        thread.start()

    def _run_exe_build(self, source_path):
        try:
            self._log_to_console('\n' + '═' * 65)
            self._log_to_console('🏗️ STARTING EXE BUILD')
            self._log_to_console('═' * 65)
            try:
                import PyInstaller
                self._log_to_console('[+] PyInstaller module found')
            except ImportError:
                self._log_to_console('\n[!] PyInstaller not found. Installing...')
                install_proc = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], capture_output=True, text=True)
                if install_proc.returncode != 0:
                    self._log_to_console(f'✗ Failed to install PyInstaller: {install_proc.stderr}')
                    raise RuntimeError('PyInstaller installation failed')
                self._log_to_console('[+] PyInstaller installed successfully')
            output_name = self.exe_name.get().strip()
            if not output_name:
                output_name = source_path.stem
            dist_dir = RESULT_DIR / 'dist'
            build_dir = RESULT_DIR / 'build'
            cmd = [sys.executable, '-m', 'PyInstaller', '--name', output_name, '--distpath', str(dist_dir), '--workpath', str(build_dir), '--specpath', str(RESULT_DIR)]
            hidden_imports = ['ctypes', 'os', 'sys', 'struct', 'zlib', 'marshal', 'base64', 'random', 'time', 'platform', 'subprocess', 'threading']
            for imp in hidden_imports:
                cmd.extend(['--hidden-import', imp])
            for imp in self.exe_hidden_imports:
                cmd.extend(['--hidden-import', imp])
            if self.exe_onefile.get():
                cmd.append('--onefile')
            if self.exe_noconsole.get():
                cmd.append('--noconsole')
            if self.exe_icon_path:
                cmd.extend(['--icon', self.exe_icon_path])
            for data_path in self.exe_extra_data:
                p = Path(data_path)
                if p.is_file():
                    cmd.extend(['--add-data', f'{data_path};.'])
                elif p.is_dir():
                    cmd.extend(['--add-data', f'{data_path};{p.name}'])
            cmd.extend(['--clean', '--noconfirm'])
            cmd.append(str(source_path))
            self._log_to_console(f'\n[*] Source: {source_path}')
            self._log_to_console(f'[*] Output name: {output_name}')
            self._log_to_console(f'[*] One-file: {self.exe_onefile.get()}')
            self._log_to_console(f'[*] No-console: {self.exe_noconsole.get()}')
            self._log_to_console(f'\n[*] Running PyInstaller (via python -m)...')
            self._log_to_console(f"    CMD: {' '.join(cmd)}\n")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(RESULT_DIR), bufsize=1)
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    self._log_to_console(f'    {line}')
            process.wait()
            if process.returncode == 0:
                if self.exe_onefile.get():
                    exe_path = dist_dir / f'{output_name}.exe'
                else:
                    exe_path = dist_dir / output_name / f'{output_name}.exe'
                self._log_to_console('\n' + '═' * 65)
                self._log_to_console('✅ EXE BUILD COMPLETE!')
                self._log_to_console('═' * 65)
                if exe_path.exists():
                    file_size = exe_path.stat().st_size
                    self._log_to_console(f'\n📁 EXE Location: {exe_path}')
                    self._log_to_console(f'📊 EXE Size: {file_size / 1024 / 1024:.2f} MB')
                else:
                    self._log_to_console(f'\n📁 Output directory: {dist_dir}')
                spec_file = RESULT_DIR / f'{output_name}.spec'
                if spec_file.exists():
                    try:
                        spec_file.unlink()
                    except Exception:
                        pass
                if build_dir.exists():
                    try:
                        shutil.rmtree(build_dir)
                    except Exception:
                        pass
                self.after(0, lambda: self._update_status('EXE Built!', COLORS['success']))
                self.after(0, lambda: messagebox.showinfo('Success', f'EXE built successfully!\n\nLocation:\n{(exe_path if exe_path.exists() else dist_dir)}'))
            else:
                self._log_to_console(f'\n✗ PyInstaller exited with code {process.returncode}')
                self.after(0, lambda: self._update_status('Build Failed!', COLORS['red_primary']))
                self.after(0, lambda: messagebox.showerror('Error', 'EXE build failed! Check console.'))
        except Exception as e:
            self._log_to_console(f'\n❌ BUILD ERROR: {e}')
            self.after(0, lambda: self._update_status('Build Error!', COLORS['red_primary']))
            self.after(0, lambda: messagebox.showerror('Error', str(e)))
        finally:
            self.processing = False
            self.after(0, lambda: self.build_btn.configure(state='normal', text='🏗️ BUILD EXE'))
            self.after(0, lambda: self.build_progress.stop())
            self.after(0, lambda: self.build_progress.set(0))
            self.after(0, lambda: self.build_status.configure(text=''))

def main():
    app = SheeshObfuscatorApp()
    app.mainloop()
if __name__ == '__main__':
    main()