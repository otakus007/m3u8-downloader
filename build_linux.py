import os
import PyInstaller.__main__
import customtkinter
import sys
import shutil

# Get customtkinter path to include its assets
ctk_path = os.path.dirname(customtkinter.__file__)

build_args = [
    'main.py',
    '--name=M3U8Downloader',
    '--onefile',
    '--windowed',
    f'--add-data={ctk_path}:customtkinter/',
    '--clean'
]

print("Starting Linux build process...")
PyInstaller.__main__.run(build_args)

print("\nBuild complete!")
print("The standalone runnable Linux binary is at: ./dist/M3U8Downloader")
