"""Copies the menu data pack (RCDATA IDR_MENU_DATA) out of a released
CharacterCreator.asi, so the plugin can be built without the game's
unpacked data (build_data.py needs it).

Usage: python extract_data_pack.py <CharacterCreator.asi> [build/CharacterCreator.data]
"""
import os
import sys

import pefile

IDR_MENU_DATA = 101
RT_RCDATA = 10


def extract(asi_path, out_path):
    pe = pefile.PE(asi_path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
    for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if kind.id != RT_RCDATA:
            continue
        for entry in kind.directory.entries:
            if entry.id != IDR_MENU_DATA:
                continue
            data_entry = entry.directory.entries[0].data.struct
            data = pe.get_data(data_entry.OffsetToData, data_entry.Size)
            if not data.startswith(b'CCDATA1\0'):
                sys.exit('resource %d is not a menu data pack' % IDR_MENU_DATA)
            version = data[8:data.index(b'\0', 8)].decode()
            os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(data)
            print('menu data %s: %d bytes -> %s' % (version, len(data), out_path))
            return
    sys.exit('no menu data pack in %s' % asi_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    extract(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join('build', 'CharacterCreator.data'))
