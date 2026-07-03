import sys
from pathlib import Path


def convert_tsv_to_anki(input_file_path, output_file_path):
    input_path = Path(input_file_path)
    output_path = Path(output_file_path)

    # 1. Verify the input file exists
    if not input_path.is_file():
        print(f"Error: The input file '{input_file_path}' does not exist.")
        sys.exit(1)

    # 2. Open both files safely using plain text mode
    with open(input_path, mode="r", encoding="utf-8") as infile, open(
        output_path, mode="w", encoding="utf-8"
    ) as outfile:

        # 3. Write Anki setup configuration headers
        outfile.write("#notetype:Chess Opening\n")
        outfile.write("#html:true\n")
        outfile.write("#tags column:3\n")
        outfile.write("#deck column:4\n")

        # Read the first line to get headers and find column positions
        header_line = infile.readline()
        if not header_line:
            print("Error: The file is empty.")
            return

        # Strip newline characters and split by tab (\t)
        headers = header_line.strip("\r\n").split("\t")

        # Map header names to their column index numbers
        try:
            eco_idx = headers.index("eco")
            name_idx = headers.index("name")
            pgn_idx = headers.index("pgn")
            uci_idx = headers.index("uci")
            epd_idx = headers.index("epd")
        except ValueError as e:
            print(f"Error: Missing required column in TSV header. {e}")
            sys.exit(1)

        count = 0

        # 4. Process the remaining lines one by one
        for line in infile:
            # Skip empty lines
            if not line.strip():
                continue

            # Split the line by tabs
            columns = line.strip("\r\n").split("\t")

            # Ensure the row has enough columns to prevent index errors
            if len(columns) <= max(eco_idx, name_idx, pgn_idx, uci_idx, epd_idx):
                continue

            # Extract data using our header index map
            eco = columns[eco_idx]
            name = columns[name_idx]
            pgn = columns[pgn_idx]
            uci = columns[uci_idx]
            epd = columns[epd_idx]

            # Construct Front, Back HTML, Tag, and Deck Name
            front = f"{eco} - {name}"
            back = (
                f"<eco>{eco}</eco>"
                f"<name>{name}</name>"
                f"<pgn>{pgn}</pgn>"
                f"<uci>{uci}</uci>"
                f"<epd>{epd}</epd>"
            )
            tag = eco
            deck_name = f"Chess Openings::{eco}"

            # 5. Write to the output file using tab separation
            outfile.write(f"{front}\t{back}\t{tag}\t{deck_name}\n")
            count += 1

    print(f"Success! Processed {count} openings using plain Python.")
    print(f"Saved Anki-ready file to: {output_path}")


if __name__ == "__main__":
    # 6. Read both input and output file names from the Command Line Interface (CLI)
    if len(sys.argv) < 3:
        print("Usage: python convert_to_anki.py <input_file.tsv> <output_file.txt>")
        sys.exit(1)

    user_input_file = sys.argv[1]
    user_output_file = sys.argv[2]

    convert_tsv_to_anki(user_input_file, user_output_file)
