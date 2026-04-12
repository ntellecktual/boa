import logging
import re


class SuppressJupyterWidgetAsset404s(logging.Filter):
    def __init__(self):
        super().__init__()
        self.jupyter_asset_pattern = re.compile(
            r'^/courses/\d+/@jupyter-widgets/((html-manager/dist/)|(base/)|(controls/)|(output/)|(nbextension/))?.*\.(woff2|woff|ttf|js|css|map)$',
            re.IGNORECASE,
        )

    def filter(self, record):
        if record.name in ['django.server', 'django.request']:
            message_content = record.getMessage()
            path_requested = None

            if 'Not Found:' in message_content:
                path_parts = message_content.split('Not Found: ', 1)
                if len(path_parts) > 1:
                    path_requested = path_parts[1].strip().split(' ')[0]
                elif record.args and len(record.args) > 0 and isinstance(record.args[0], str):
                    path_requested = record.args[0]
            elif ' 404 ' in message_content:
                match = re.search(r'"(?:GET|POST)\s+([^"\s?#]+)[^"]*"\s+404', message_content)
                if match:
                    path_requested = match.group(1)

            if path_requested:
                path_to_check = path_requested.strip()
                if self.jupyter_asset_pattern.search(path_to_check):
                    return False

        return True
