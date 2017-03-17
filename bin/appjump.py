#!/usr/bin/env python

APPS = {
    'Terminal': {
        'criteria': {'winname': b'Terminal'},
        'exec': ['konsole', '--profile', 'Terminal'],
    },
    'Browser': {
        'criteria': {'winname': b'Chromium'},
        'exec': ['chromium']
    },
    'Docs': {
        'criteria': {'winname': b'Zeal'},
        'exec': ['zeal']
    },
    'Code': {
        'criteria': {'winname': b'Visual Studio Code'},
        'exec': ['code']
    },
    'Draft': {
        'criteria': {'winname': b'Typora'},
        'exec': ['typora', '/home/pma/Projects/manote/inbox.md']
    }

}


if __name__ == '__main__':
    import sys
    from xdo import Xdo
    import subprocess

    if len(sys.argv) == 1:
        app_name = 'Terminal'
    else:
        app_name = sys.argv[1]

    print(app_name)
    
    if app_name not in APPS:
        exit(1)
    

    xdo = Xdo()
    app = APPS[app_name]
    pids = xdo.search_windows(**app['criteria'])
    if pids:
        pid = pids[-1]
        active_pid = xdo.get_active_window()
        if pid == active_pid:
            xdo.minimize_window(pid)
        else:
            xdo.activate_window(pid)
    else:
        subprocess.Popen(app['exec'])
