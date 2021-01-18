# -*- mode: python ; coding: utf-8 -*-

import sys
import os

from kivy_deps import sdl2, glew
import kivymd
from kivymd import hooks_path as kivymd_hooks_path
from os.path import dirname, abspath, join, basename

path = os.path.abspath(".")

a = Analysis(
    ["main.py"],
    pathex=[path],
    binaries=[],
    datas=[(kivymd.fonts_path, join("kivymd", basename(dirname(kivymd.fonts_path)))),(kivymd.images_path, join("kivymd", basename(dirname(kivymd.images_path)))),],
    hiddenimports=['kivymd.vendor.circularTimePicker', 'PIL'],
    hookspath=[kivymd_hooks_path],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    debug=False,
    strip=False,
    upx=True,
    name="app_name",
    console=True,
    onedir=True,
)