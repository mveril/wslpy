from wslpy.core.check import get_mount_prefix, get_sys_drive_prefix
from wslpy.core.access import distro_info, registry
from wslpy.exec import winps


def get_current_execuable():
    """
    Get current exes of the current WSL (for ones that have).
    """
    import os
    from wslpy.convert import to_wsl
    from wslpy.exec import winps

    _distro_info = distro_info()
    if "PackageFamilyName" in _distro_info:
        pname = _distro_info["PackageFamilyName"]['value']
        p = winps("[Environment]::GetFolderPath('LocalApplicationData')")
        if p.returncode:
            raise Exception("Failed to get LocalApplicationData")
        raw_win_path = p.stdout.replace("\r\n", "")
        win_path = raw_win_path + "\\Microsoft\\WindowsApps\\" + pname
        exe_real_loc = to_wsl(win_path)
        return os.listdir(exe_real_loc)[0]
    else:
        return None


def get_display_scaling():
    """
    Get Windows Display Scaling
    """
    command = """
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Drawing;

public class DPI {
    [DllImport("gdi32.dll")]
    static extern int GetDeviceCaps(IntPtr hdc, int nIndex);

    public enum DeviceCap {
    VERTRES = 10,
    DESKTOPVERTRES = 117
    }

    public static float scaling() {
    Graphics g = Graphics.FromHwnd(IntPtr.Zero);
    IntPtr desktop = g.GetHdc();
    int LogicalScreenHeight = GetDeviceCaps(desktop, (int)DeviceCap.VERTRES);
    int PhysicalScreenHeight = GetDeviceCaps(desktop,
        (int)DeviceCap.DESKTOPVERTRES);

    return (float)PhysicalScreenHeight / (float)LogicalScreenHeight;
    }
}
'@ -ReferencedAssemblies 'System.Drawing.dll'

[Math]::round([DPI]::scaling(), 2) * 100
"""

    p = winps(command)
    if p.returncode:
        raise Exception("Failed to get display scaling: ", p.stderr)
    dscale = int(p.stdout.rstrip()) / 100
    return dscale


def get_windows_locale():
    """
    Get Windows Locale
    """
    p = winps("(Get-Culture).Name")
    if p.returncode:
        raise Exception("Failed to get Windows Locale: ", p.stderr)
    win_locale = p.stdout.rstrip().replace("-", "_")
    return win_locale


def get_windows_theme():
    """
    Get Windows Theme

    Returns
    -------
    a string of either "light" or "dark"
    """
    raw_theme = registry("HKCU\\SOFTWARE\\Microsoft\\Windows\\Current"
                         "Version\\Themes\\Personalize", "AppsUseLightTheme")
    return "dark" if int(raw_theme, 0) else "light"


__all__ = [
    "get_current_execuable",
    "get_mount_prefix",
    "get_sys_drive_prefix",
    "registry",
    ]
