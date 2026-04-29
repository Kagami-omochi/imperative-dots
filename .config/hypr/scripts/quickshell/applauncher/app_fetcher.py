#!/usr/bin/env python3
import os
import glob
import json

def fetch_apps():
    apps = {}
    home = os.path.expanduser('~')
    
    # 📌 QML側が作成するピン留めリストのJSONファイルを読み込む
    config_dir = f'{home}/.config/hypr/scripts/quickshell/applauncher'
    pinned_file = os.path.join(config_dir, 'pinned_apps.json')
    
    try:
        with open(pinned_file, 'r', encoding='utf-8') as f:
            pinned_names = json.load(f)
    except Exception:
        pinned_names = [] # ファイルが無い場合は空リスト
    
    dirs = [
        '/usr/share/applications',
        '/usr/local/share/applications',
        f'{home}/.local/share/applications',
        '/var/lib/flatpak/exports/share/applications',
        f'{home}/.local/share/flatpak/exports/share/applications',
        f'{home}/.nix-profile/share/applications',
        '/run/current-system/sw/share/applications'
    ]
    
    for d in dirs:
        if not os.path.exists(d):
            continue
            
        for f in glob.glob(os.path.join(d, '**/*.desktop'), recursive=True):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    app = {'name': '', 'exec': '', 'icon': ''}
                    is_desktop = False
                    no_display = False
                    
                    for line in file:
                        line = line.strip()
                        if line == '[Desktop Entry]':
                            is_desktop = True
                        elif line.startswith('['):
                            is_desktop = False
                            
                        if is_desktop:
                            if line.startswith('Name=') and not app['name']:
                                app['name'] = line[5:]
                            elif line.startswith('Exec=') and not app['exec']:
                                app['exec'] = line[5:].split(' %')[0].split(' @@')[0]
                            elif line.startswith('Icon=') and not app['icon']:
                                app['icon'] = line[5:]
                            elif line.startswith('NoDisplay=true') or line.startswith('NoDisplay=1'):
                                no_display = True
                                
                    if app['name'] and app['exec'] and not no_display:
                        apps[app['name']] = app
            except Exception:
                pass
                
    pinned_list = []
    unpinned_list = []

    # 保存された順序・完全一致でピン留めアプリを抽出
    for app_name in pinned_names:
        if app_name in apps:
            app = apps[app_name]
            app['pinned'] = True
            pinned_list.append(app)
            del apps[app_name]

    remaining_apps = list(apps.values())
    remaining_apps.sort(key=lambda x: x['name'].lower())
    
    for app in remaining_apps:
        app['pinned'] = False
        unpinned_list.append(app)

    final_res = pinned_list + unpinned_list
    print(json.dumps(final_res))

if __name__ == "__main__":
    fetch_apps()