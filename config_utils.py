import yaml
import os
import importlib.util

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'crawler_config.yaml')
PLUGINS_DIR = os.path.join(os.path.dirname(__file__), 'plugins')

def load_config(config_path=CONFIG_PATH):
    """Load YAML config for the crawler."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_plugins(plugin_list, plugins_dir=PLUGINS_DIR):
    """Dynamically import plugins from the plugins directory."""
    plugins = {}
    for plugin in plugin_list:
        name = plugin['name']
        path = os.path.join(plugins_dir, os.path.basename(plugin['path']))
        if not os.path.exists(path):
            continue
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            plugins[name] = mod
    return plugins 