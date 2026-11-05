import json
import ctypes.util
import os
import sys
from pathlib import Path

from cx_Freeze import setup, Executable


project_dir = Path(__file__).resolve().parent
package_metadata = json.loads((project_dir / 'package.json').read_text(encoding='utf-8'))

usb_libraries = []
if sys.platform == "darwin":
    libusb = ctypes.util.find_library("usb-1.0")
    if libusb and os.path.isfile(libusb):
        usb_libraries.append((os.path.realpath(libusb), "lib/libusb-1.0.dylib"))


setup(
    name='Crosstalk',
    version=package_metadata['version'],
    description='A simple mesh network communications app powered by the Reticulum Network Stack',
    executables=[
        Executable(
            script='crosstalk.py', # this script to run
            base=None, # we are running a console application, not a gui
            target_name='Crosstalk', # creates Crosstalk.exe
            shortcut_name='Crosstalk', # name shown in shortcut
            shortcut_dir='ProgramMenuFolder', # put the shortcut in windows start menu
            icon='logo/icon.ico', # set the icon for the exe
        ),
    ],
    options={
        'build_exe': {
            # libs that are required
            'packages': [
                # required for dynamic import fix
                # https://github.com/marcelotduarte/cx_Freeze/discussions/2039
                # https://github.com/marcelotduarte/cx_Freeze/issues/2041
                'RNS',
                # RNS loads bleak dynamically for RNode BLE (ble://) connections
                'bleak',
                'usb',
            ],
            # files that are required
            'include_files': [
                'package.json', # used to determine app version from python
                'public/', # static files served by web server
                (
                    'src/backend/interfaces/IridiumIMTInterface.py',
                    'src/backend/interfaces/IridiumIMTInterface.py',
                ),
                (
                    'src/backend/interfaces/PrnsHopspotInterface.py',
                    'src/backend/interfaces/PrnsHopspotInterface.py',
                ),
            ] + usb_libraries,
            # slim down the build by excluding these unused libs
            'excludes': [
                'PIL', # saves ~200MB
            ],
            # this has the same effect as the -O command line option when executing CPython directly.
            # it also prevents assert statements from executing, removes docstrings and sets __debug__ to False.
            # https://stackoverflow.com/a/57948104
            "optimize": 2,
            # change where exe is built to
            'build_exe': 'build/exe',
        },
    },
)
