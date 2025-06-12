import json
import os
from rio_tiler.colormap import cmap as default_cmap, parse_color

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
json_path = os.path.join(project_root, 'habitat_colormap.json')

habitat_values = {}
try:
    with open(json_path, "r") as f:
        habitat_values_str_keys = json.load(f)
        habitat_values = {
            int(k): parse_color(v) for k, v in habitat_values_str_keys.items()
        }
    print(f"[DEBUG] Successfully loaded {len(habitat_values)} entries from colormap.")
except Exception as e:
    print(f"[ERROR] Failed to load colormap: {e}")

if habitat_values:
    try:
        custom_cmap = default_cmap.register({"habitat_custom": habitat_values})
        print("[DEBUG] 'habitat_custom' colormap registered.")
    except Exception as e:
        print(f"[ERROR] Failed to register colormap: {e}")
        custom_cmap = default_cmap
else:
    custom_cmap = default_cmap

cmap_store = custom_cmap