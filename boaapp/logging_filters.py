import logging
import re

class SuppressJupyterWidgetAsset404s(logging.Filter):
    def __init__(self):
        super().__init__()
        # Regex to match paths like /courses/ANY_ID/@jupyter-widgets/...
        # This regex is a bit more general for typical jupyter widget asset paths.
        self.jupyter_asset_pattern = re.compile(
            r"^/courses/\d+/@jupyter-widgets/((html-manager/dist/)|(base/)|(controls/)|(output/)|(nbextension/))?.*\.(woff2|woff|ttf|js|css|map)$",
            re.IGNORECASE
        )
        print("[FILTER INIT] SuppressJupyterWidgetAsset404s filter initialized.") # For debugging if filter loads

    def filter(self, record):
        # Target specific loggers that might produce 404 messages
        if record.name in ['django.server', 'django.request']:
            message_content = record.getMessage()
            path_requested = None

            # Attempt to extract path from "Not Found: /actual/path"
            if "Not Found:" in message_content:
                # For django.request, the path is often in the message itself after "Not Found: "
                # Example message_content: "Not Found: /the/actual/path"
                path_parts = message_content.split("Not Found: ", 1)
                if len(path_parts) > 1:
                    path_requested = path_parts[1].strip().split(' ')[0] # Get the path part before any potential extra info
                elif record.args and len(record.args) > 0 and isinstance(record.args[0], str): # Fallback for other loggers
                    path_requested = record.args[0] # This was likely the part not working for django.request
            # Attempt to extract path from "GET /actual/path HTTP/1.1" 404 status_code
            elif " 404 " in message_content:
                # Regex to find the path in a typical HTTP request log line ending in 404
                match = re.search(r'"(?:GET|POST)\s+([^"\s?#]+)[^"]*"\s+404', message_content)
                if match:
                    path_requested = match.group(1)

            if path_requested:
                path_to_check = path_requested.strip()
                print(f"[FILTER DEBUG] Checking path: '{path_to_check}' with regex. Logger: {record.name}") # Debugging line
                is_match = bool(self.jupyter_asset_pattern.search(path_to_check))
                print(f"[FILTER DEBUG] Regex match result: {is_match}") # Debugging line
                if is_match:
                    print(f"[FILTER DEBUG] SUPPRESSED: {path_to_check}") # Debugging line
                    return False  # Suppress this log record
            elif "Not Found:" in message_content or " 404 " in message_content: # If path_requested is None but it's a 404
                print(f"[FILTER DEBUG] 404 message, but path not extracted. Logger: {record.name}, Msg: {message_content[:100]}, Args: {record.args}") # Debugging line

        return True # Allow other log records