import yaml


class ConfigManager:
    """
    配置装载类
    """

    def __init__(self):
        self.config_file = "F://Python-BianceBot/Biance/config/config.yaml"
        self.config = self.load()

    def load(self):
        """Load configuration from file."""
        with open(self.config_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get(self, *keys):
        """Get a nested configuration value."""
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value

# 使用示例
# config = ConfigManager()
#
# api_key = config.get('api', 'key')
# api_secret = config.get('api', 'secret')
#
# print(f"Database Host: {api_key}")
# print(f"Database Port: {api_secret}")
