import sys
from pathlib import Path
import os

# Third-party libraries used specifically for the graphics compilation
import chess
import chess.svg
import cairosvg
from apng import APNG


def generate_board_animation(uci_sequence, output_image_path):
    """
    Parses a UCI sequence string, generates individual chess board frames,
    and builds an infinitely looping APNG file.
    """
    board = chess.Board()
    frame_files = []
    
    # 1. Render the initial blank starting board layout (Move 0)
    start_svg = chess.svg.board(board=board, size=400)
    temp_start_frame = f"{output_image_path.stem}_frame_0.png"
    cairosvg.svg2png(bytestring=start_svg, write_to=temp_start_frame)
    frame_files.append(temp_start_frame)
    
    # 2. Iterate through and push each UCI move step
    moves = uci_sequence.split()
    for index, move_str in enumerate(moves, start=1):
        try:
            move = chess.Move.from_uci(move_str)
            if move in board.legal_moves:
                board.push(move)
                
                # Render state, highlighting the last played piece move
                board_svg = chess.svg.board(board=board, lastmove=move, size=400)
                temp_frame_path = f"{output_image_path.stem}_frame_{index}.png"
                
                cairosvg.svg2png(bytestring=board_svg, write_to=temp_frame_path)
                frame_files.append(temp_frame_path)
        except ValueError:
            continue

    # 3. Compile all individual frames into a single, seamless APNG file
    if frame_files:
        APNG.from_files(frame_files, delay=1000).save(str(output_image_path))
        
        # Clean up the individual temporary frame files from disk
        for frame in frame_files:
            if os.path.exists(frame):
                os.remove(frame)


def convert_tsv_to_anki(input_file_path, output_file_path):
    """
    Reads the raw TSV chess database file line by line without csv libraries,
    triggers the APNG generation engine, and formats files for Anki imports.
    """
    input_path = Path(input_file_path)
    output_path = Path(output_file_path)

    if not input_path.is_file():
        print(f"Error: The input file '{input_file_path}' does not exist.")
        sys.exit(1)

    # Set up your target media asset storage folder
    images_dir = Path("chess-openings-apng")
    images_dir.mkdir(exist_ok=True)

    with open(input_path, mode="r", encoding="utf-8") as infile, open(
        output_path, mode="w", encoding="utf-8"
    ) as outfile:

        # --- ANKI FILE CONFIGURATION HEADERS ---
        outfile.write("#notetype:Chess Opening\n")
        outfile.write("#html:true\n")
        outfile.write("#tags column:3\n")
        outfile.write("#deck column:4\n")

        header_line = infile.readline()
        if not header_line:
            print("Error: The file is empty.")
            return

        headers = header_line.strip("\r\n").split("\t")

        try:
            eco_idx = headers.index("eco")
            name_idx = headers.index("name")
            pgn_idx = headers.index("pgn")
            uci_idx = headers.index("uci")
            epd_idx = headers.index("epd")
        except ValueError as e:
            print(f"Error: Missing required column in TSV header field setup. {e}")
            sys.exit(1)

        count = 0

        for line in infile:
            if not line.strip():
                continue

            columns = line.strip("\r\n").split("\t")

            if len(columns) <= max(eco_idx, name_idx, pgn_idx, uci_idx, epd_idx):
                continue

            eco = columns[eco_idx]
            name = columns[name_idx]
            pgn = columns[pgn_idx]
            uci = columns[uci_idx]
            epd = columns[epd_idx]

            # Standardize names to generate filename-safe text strings
            safe_name = "".join(c for c in name if c.isalnum() or c in "._- ").strip().replace(" ", "_")
            image_filename = f"{eco}_{safe_name}.png"
            target_image_path = images_dir / image_filename

            # --- APNG INVOCATION NOW CALLED CORRECTLY ---
            print(f"Generating animation for: {eco} - {name}...")
            generate_board_animation(uci, target_image_path)

            front = eco
            back = (
                f"<eco>{eco}</eco>"
                f"<name>{name}</name>"
                f"<pgn>{pgn}</pgn>"
                f"<uci>{uci}</uci>"
                f"<epd>{epd}</epd>"
                f'<div class="chess-board-container"><img src="{image_filename}" /></div>'
            )
            
            tag = eco
            deck_name = f"Chess Openings::{eco}"

            outfile.write(f"{front}\t{back}\t{tag}\t{deck_name}\n")
            count += 1

    print(f"\nSuccess! Processed {count} openings.")
    print(f"All animated graphics saved to the folder: '{images_dir.resolve()}'")
    print(f"Saved Anki-ready import text file to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_to_anki.py <input_file.tsv> <output_file.txt>")
        sys.exit(1)

    # --- FIXED: sys.argv[0] is the script name. Inputs start at index 1! ---
    user_input_file = sys.argv[1]
    user_output_file = sys.argv[2]

    convert_tsv_to_anki(user_input_file, user_output_file)
