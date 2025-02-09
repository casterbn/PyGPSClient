"""
about_dialog.py

About Dialog Box class for PyGPSClient application.

Created on 20 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from platform import python_version
from subprocess import CalledProcessError, run
from sys import platform
from tkinter import Button, Label, Toplevel
from webbrowser import open_new_tab

from PIL import Image, ImageTk
from pygnssutils import version as PGVERSION
from pynmeagps import version as NMEAVERSION
from pyrtcm import version as RTCMVERSION
from pyspartn import version as SPARTNVERSION
from pyubx2 import version as UBXVERSION

from pygpsclient._version import __version__ as VERSION
from pygpsclient.globals import DLGTABOUT, GITHUB_URL, ICON_APP, ICON_EXIT
from pygpsclient.helpers import check_latest
from pygpsclient.strings import ABOUTTXT, COPYRIGHTTXT, DLGABOUT

LIBVERSIONS = {
    "PyGPSClient": VERSION,
    "pygnssutils": PGVERSION,
    "pyubx2": UBXVERSION,
    "pynmeagps": NMEAVERSION,
    "pyrtcm": RTCMVERSION,
    "pyspartn": SPARTNVERSION,
}


class AboutDialog:
    """
    About dialog box class
    """

    def __init__(self, app, **kwargs):
        """
        Initialise Toplevel dialog

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self._dialog = Toplevel()
        self._dialog.title = DLGABOUT
        self._dialog.geometry(
            f"+{self.__master.winfo_rootx() + 50}+{self.__master.winfo_rooty() + 50}"
        )
        self._dialog.attributes("-topmost", "true")
        self._img_icon = ImageTk.PhotoImage(Image.open(ICON_APP))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._updates = []

        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up widgets.
        """

        self._lbl_title = Label(self._dialog, text=DLGABOUT)
        self._lbl_title.config(font=self.__app.font_md2)
        self._lbl_icon = Label(self._dialog, image=self._img_icon)
        self._lbl_desc = Label(
            self._dialog,
            text=ABOUTTXT,
            wraplength=300,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._lbl_python_version = Label(
            self._dialog,
            text=f"Python: {python_version()}",
            font=self.__app.font_sm,
        )
        self._lbl_lib_versions = []
        for nam, ver in LIBVERSIONS.items():
            self._lbl_lib_versions.append(
                Label(
                    self._dialog,
                    text=f"{nam}: {ver}",
                    font=self.__app.font_sm,
                )
            )
        self._btn_checkupdate = Button(
            self._dialog,
            text="Check for updates",
            width=12,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._lbl_copyright = Label(
            self._dialog,
            text=COPYRIGHTTXT,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._btn_ok = Button(
            self._dialog,
            image=self._img_exit,
            width=55,
            command=self._ok_press,
            cursor="hand2",
        )

    def _do_layout(self):
        """
        Arrange widgets in dialog.
        """

        self._lbl_title.grid(column=0, row=0, padx=5, pady=3)
        self._lbl_icon.grid(column=0, row=1, padx=5, pady=3)
        self._lbl_desc.grid(column=0, row=2, padx=15, pady=3)
        self._lbl_python_version.grid(column=0, row=3, padx=5, pady=3)
        i = 0
        for i, _ in enumerate(LIBVERSIONS):
            self._lbl_lib_versions[i].grid(column=0, row=4 + i, padx=5, pady=1)
        self._btn_checkupdate.grid(
            column=0, row=5 + i, ipadx=3, ipady=3, padx=5, pady=3
        )
        self._lbl_copyright.grid(column=0, row=6 + i, padx=15, pady=3)
        self._btn_ok.grid(column=0, row=7 + i, ipadx=3, ipady=3, padx=5, pady=3)

    def _attach_events(self):
        """
        Bind events to dialog.
        """

        self._btn_checkupdate.bind("<Button>", self._check_for_update)
        self._lbl_desc.bind("<Button-1>", lambda e: open_new_tab(GITHUB_URL))
        self._lbl_copyright.bind("<Button-1>", lambda e: open_new_tab(GITHUB_URL))
        self._btn_ok.bind("<Return>", self._ok_press)
        self._btn_ok.focus_set()

    def _ok_press(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle OK button press.
        """

        self.__app.stop_dialog(DLGTABOUT)
        self._dialog.destroy()

    def _check_for_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Check for updates.
        """

        self._updates = []
        for i, (nam, current) in enumerate(LIBVERSIONS.items()):
            latest = check_latest(nam)
            txt = f"{nam}: {current}"
            if latest == current:
                col = "green"
            elif latest == "N/A":
                txt += ". Info not available!"
                col = "red"
            else:
                self._updates.append(nam)
                txt += f". Latest version is {latest}"
                col = "red"
            self._lbl_lib_versions[i].config(text=txt, fg=col)

        if len(self._updates) > 0:
            self._btn_checkupdate.config(text="UPDATE", fg="blue")
            self._btn_checkupdate.bind("<Button>", self._do_update)

    def _do_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Run python update.
        """

        self._btn_checkupdate.config(text="UPDATING...", fg="blue")
        self._dialog.update_idletasks()
        pyc = "python" if platform == "win32" else "python3"
        cmd = [
            pyc,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--user",
            "--force-reinstall",
        ]
        for pkg in self._updates:
            cmd.append(pkg)

        try:
            run(
                cmd,
                check=True,
                capture_output=True,
            )
        except CalledProcessError:
            self._btn_checkupdate.config(text="UPDATE FAILED", fg="red")
            self._btn_checkupdate.bind("<Button>", self._check_for_update)
            return

        self._btn_checkupdate.config(text="RESTART APP", fg="green")
        self._btn_checkupdate.bind("<Button>", self.__app.on_exit)
