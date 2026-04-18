import ctypes
import sys
from pathlib import Path
from PIL import Image
import os
import win32ui
import win32gui
import win32con
import win32api

def save_icon(exe_path, output_path):
    try:
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        large, small = win32gui.ExtractIconEx(str(exe_path), 0)
        if not large:
            print('No icon found')
            return False
        hicon = large[0]
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), hicon)
        pass
    except Exception as e:
        print(f'Error: {e}')
        return False
    return True

def extract_icon(exe_path, output_path):
    try:
        User32 = ctypes.windll.user32
        p_icon = ctypes.POINTER(ctypes.c_void_p)
        hicon = ctypes.c_void_p(0)
        import win32gui, win32ui, win32con
        large, small = win32gui.ExtractIconEx(str(exe_path), 0)
        if not large:
            return False
        hicon = large[0]
        dc = win32gui.GetDC(0)
        dc_obj = win32ui.CreateDCFromHandle(dc)
        mem_dc = dc_obj.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        w = win32api.GetSystemMetrics(win32con.SM_CXICON)
        h = win32api.GetSystemMetrics(win32con.SM_CYICON)
        bmp.CreateCompatibleBitmap(dc_obj, 32, 32)
        mem_dc.SelectObject(bmp)
        mem_dc.DrawIcon((0, 0), hicon)
        bmp.SaveBitmapFile(mem_dc, str(output_path).replace('.ico', '.bmp'))
        img = Image.open(str(output_path).replace('.ico', '.bmp'))
        img.save(output_path, format='ICO', sizes=[(256, 256)])
        try:
            os.remove(str(output_path).replace('.ico', '.bmp'))
        except:
            pass
        return True
    except Exception as e:
        return False