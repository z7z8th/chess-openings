import sys
import os
import tempfile
import subprocess
import urllib.parse

def main():
    # Update this path to match your En Croissant installation
    if sys.platform == "win32":
        EN_CROISSANT_PATH = r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\en-croissant\En Croissant.exe"
    elif sys.platform == "darwin":
        EN_CROISSANT_PATH = "/Applications/En Croissant.app"
    else: # Linux
        EN_CROISSANT_PATH = "/usr/bin/en-croissant"

    # Ensure an argument was passed (the browser passes the full URL string)
    if len(sys.argv) < 2:
        print("[-] Error: No URL provided.", file=sys.stderr)
        sys.exit(1)

    url_input = sys.argv[1]
    
    # Verify protocol
    if not url_input.startswith("chess://pgn/"):
        print("[-] Error: Invalid protocol scheme. Must start with chess://pgn/", file=sys.stderr)
        sys.exit(1)

    # Extract and decode the PGN string from the URL payload
    raw_payload = url_input.replace("chess://pgn/", "", 1)
    pgn_string = urllib.parse.unquote(raw_payload)

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(pgn_string)
        temp_filepath = temp_file.name

    # Launch En Croissant
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", EN_CROISSANT_PATH, temp_filepath])
        else:
            subprocess.Popen([EN_CROISSANT_PATH, temp_filepath])
    except FileNotFoundError:
        print(f"[-] Error: En Croissant not found at {EN_CROISSANT_PATH}", file=sys.stderr)
        os.unlink(temp_filepath)
        sys.exit(1)

if __name__ == "__main__":
    main()
