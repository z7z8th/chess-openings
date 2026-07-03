import sys
from pathlib import Path
import os
import re
import urllib.parse  # Built-in tool to clean up strings for web URLs
from multiprocessing import Pool, cpu_count

# Third-party libraries used specifically for the graphics compilation
import chess
import chess.svg
import cairosvg
from apng import APNG

# --- GLOBAL CONFIGURATION VARIABLES ---
BOARD_SIZE = 400  # Change this number to resize your chess boards (e.g., 400, 500, 600)


def generate_single_board_animation(args):
    """
    Worker function executed by multiple processes.
    Parses a single row's UCI string, draws frames, and saves the APNG.
    """
    uci_sequence, output_path_str, eco, name = args
    output_image_path = Path(output_path_str)

    # --- TARGET SKIPPING CHECK ---
    # Check if the file already exists inside the folder to save processor time
    if output_image_path.is_file():
        return "skipped"

    print(f"Generating animation for: {eco} - {name}...")
    
    board = chess.Board()
    frame_files = []
    
    try:
        # 1. Render the initial blank starting board layout (Move 0) using the BOARD_SIZE variable
        start_svg = chess.svg.board(board=board, size=BOARD_SIZE)
        temp_start_frame = f"{output_image_path.stem}_frame_0.png"
        cairosvg.svg2png(bytestring=start_svg, write_to=temp_start_frame)
        frame_files.append(temp_start_frame)
        
        # 2. Iterate through and push each UCI move step
        moves = uci_sequence.split()
        for index, move_str in enumerate(moves, start=1):
            move = chess.Move.from_uci(move_str)
            if move in board.legal_moves:
                board.push(move)
                
                # Render state, highlighting the last played piece move
                board_svg = chess.svg.board(board=board, lastmove=move, size=BOARD_SIZE)
                temp_frame_path = f"{output_image_path.stem}_frame_{index}.png"
                
                cairosvg.svg2png(bytestring=board_svg, write_to=temp_frame_path)
                frame_files.append(temp_frame_path)
    except Exception as e:
        # Clean up any partial frames if rendering fails mid-way
        for frame in frame_files:
            if os.path.exists(frame):
                os.remove(frame)
        return "error"

    # 3. Compile all individual frames into a single, seamless APNG file
    if frame_files:
        # delay=1000 sets each animation move step to pause for 1 second (1000ms)
        APNG.from_files(frame_files, delay=1000).save(str(output_image_path))
        
        # Clean up the individual temporary frame files from disk
        for frame in frame_files:
            if os.path.exists(frame):
                os.remove(frame)
        return "generated"
    
    return "error"


def convert_tsv_to_anki(input_file_path, output_file_path):
    """
    Reads TSV using plain Python, collects tasks for the multi-process engine, 
    and exports formatted Anki card data.
    """
    input_path = Path(input_file_path)
    output_path = Path(output_file_path)

    # Verify that the input file actually exists before starting
    if not input_path.is_file():
        print(f"Error: The input file '{input_file_path}' does not exist.")
        sys.exit(1)

    # Automatically set up your target media asset storage folder
    images_dir = Path("chess-openings-apng")
    images_dir.mkdir(exist_ok=True)

    # Read the entire file into memory first to organize tasks for multiprocessing
    with open(input_path, mode="r", encoding="utf-8") as infile:
        header_line = infile.readline()
        if not header_line:
            print("Error: The file is empty.")
            return

        # Clean line breaks and separate by tab markers
        headers = header_line.strip("\r\n").split("\t")

        # Map field name text tokens dynamically to index coordinates
        try:
            eco_idx = headers.index("eco")
            name_idx = headers.index("name")
            pgn_idx = headers.index("pgn")
            uci_idx = headers.index("uci")
            epd_idx = headers.index("epd")
        except ValueError as e:
            print(f"Error: Missing required column in TSV header field setup. {e}")
            sys.exit(1)

        tasks = []
        rows_data = []

        # Parse text rows one single line at a time
        for line in infile:
            if not line.strip():
                continue

            columns = line.strip("\r\n").split("\t")

            # Guard condition to make sure row parsing index bounds are safe
            if len(columns) <= max(eco_idx, name_idx, pgn_idx, uci_idx, epd_idx):
                continue

            eco = columns[eco_idx]
            name = columns[name_idx]
            pgn = columns[pgn_idx]
            uci = columns[uci_idx]
            epd = columns[epd_idx]

            # Generate uniform, operating-system-safe filenames
            safe_name = "".join(c for c in name if c.isalnum() or c in "._- ").strip().replace(" ", "_")
            image_filename = f"{eco}_{safe_name}.png"
            target_image_path = images_dir / image_filename

            # Package data for the multiprocessing pool and rows for writing later
            tasks.append((uci, str(target_image_path), eco, name))
            rows_data.append((eco, name, pgn, uci, epd, image_filename))

    # --- MULTIPROCESSING ENGINE START ---
    num_cores = cpu_count()
    print(f"Launching processing engine utilizing {num_cores} CPU cores...")
    
    with Pool(processes=num_cores) as pool:
        # map runs tasks simultaneously across cores and preserves dataset order
        results = pool.map(generate_single_board_animation, tasks)

    # Count our processing actions
    generated_count = results.count("generated")
    skipped_count = results.count("skipped")
    
    # --- WRITE OUT THE ANKI TEXT FILE ---
    print("\nWriting out finalized Anki card collection records...")
    with open(output_path, mode="w", encoding="utf-8") as outfile:
        # Configuration lines to lock in your custom note type, columns, and decks
        outfile.write("#notetype:Chess Opening\n")
        outfile.write("#html:true\n")
        outfile.write("#tags column:3\n")
        outfile.write("#deck column:4\n")

        for eco, name, pgn, uci, epd, image_filename in rows_data:
            # Clean the opening name to match Lichess's specific directory URL format
            # --- START UNIFIED REGEX LICHESS SLUG ALGORITHM ---
            # This single regex acts like a switchboard:
            # - If it catches a colon (Group 1), it replaces it with '_-_'
            # - If it catches any other non-alphanumeric/non-dash symbol (Group 2), it replaces it with '_'
            slug = re.sub(
                r'([^a-zA-Z0-9\-]+)', 
                '_', 
                name
            )
            
            # Clean up double underscores or trailing boundary dashes
            slug = re.sub(r'_{2,}', '_', slug)
            slug = re.sub(r'_*-_*', '-', slug)
            slug = slug.strip('-').strip('_')
            
            # Encode for safe web transmission
            web_safe_name = urllib.parse.quote(slug)
            # --- END UNIFIED REGEX LICHESS SLUG ALGORITHM ---
            lichess_url = f"https://lichess.org/opening/{web_safe_name}"

            front = f"{eco} - {name}"
            
            # Formulate card back. The <name> element now wraps a link to Lichess.
            back = (
                f"<eco>{eco}</eco>"
                f'<name><a href="{lichess_url}" target="_blank" style="text-decoration: none; color: inherit;">{name}</a></name>'
                f"<pgn>{pgn}</pgn>"
                f"<uci>{uci}</uci>"
                f"<epd>{epd}</epd>"
                f'<div class="chess-board-container"><img src="{image_filename}" /></div>'
            )
            tag = eco
            deck_name = f"Chess Openings::{eco}"

            # Save line using tab separator
            outfile.write(f"{front}\t{back}\t{tag}\t{deck_name}\n")

    print(f"\nSuccess! Processed {len(rows_data)} openings total.")
    print(f"Created {generated_count} new animations. Skipped {skipped_count} items (already existed).")
    print(f"All animated graphics saved to the folder: '{images_dir.resolve()}'")
    print(f"Saved Anki-ready import text file to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_to_anki.py <input_file.tsv> <output_file.txt>")
        sys.exit(1)

    user_input_file = sys.argv[1]
    user_output_file = sys.argv[2]

    convert_tsv_to_anki(user_input_file, user_output_file)
