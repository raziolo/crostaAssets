import os
from PIL import Image

# --- CONFIGURATION ---
# IMPORTANT: Set these paths before running the script.
# Use a raw string (r"...") on Windows to avoid issues with backslashes.

# 1. The folder containing your original images.
INPUT_DIRECTORY = r"C:\Users\Brumotti\Desktop\DESKTOP\NewDjangoProjects\scratches\INPUT_FOLDER"

# 2. The folder where clean, metadata-free images will be saved.
#    This folder will be created automatically if it doesn't exist.
OUTPUT_DIRECTORY = r"C:\Users\Brumotti\Desktop\DESKTOP\NewDjangoProjects\scratches\OUTPUT_FOLDER"


# ---------------------


def remove_exif(input_path, output_path):
    """
    Opens an image, removes its EXIF data, and saves it to a new file.
    """
    try:
        with Image.open(input_path) as img:
            # The core of the process: get the raw pixel data and format.
            # We don't copy over the 'info' dictionary which contains EXIF.
            image_data = list(img.getdata())

            # Create a new image with the same mode and size, but no metadata.
            image_without_exif = Image.new(img.mode, img.size)
            image_without_exif.putdata(image_data)

            # Define save parameters to maintain quality.
            save_params = {'format': img.format}
            if img.format.lower() in ['jpeg', 'jpg']:
                # Use high quality for JPEGs. 'subsampling=0' preserves color detail.
                save_params['quality'] = 95
                save_params['subsampling'] = 0
            elif img.format.lower() == 'png':
                save_params['optimize'] = True

            # Save the clean image.
            image_without_exif.save(output_path, **save_params)
            print(f"✅  Successfully stripped and saved: {os.path.basename(output_path)}")

    except Exception as e:
        print(f"❌  ERROR processing {os.path.basename(input_path)}: {e}")


def process_directory(input_dir, output_dir):
    """
    Processes all supported images in the input directory.
    """
    print(f"--- Starting EXIF removal process ---")
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}\n")

    # Create the output directory if it doesn't exist (Safety First)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"❌  FATAL ERROR: Could not create output directory: {e}")
            return

    supported_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.tif')
    file_count = 0
    processed_count = 0

    for filename in os.listdir(input_dir):
        file_count += 1
        if filename.lower().endswith(supported_extensions):
            processed_count += 1
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            remove_exif(input_path, output_path)
        else:
            print(f"⚪  Skipping non-image file: {filename}")

    print("\n--- Process Complete ---")
    print(f"Scanned {file_count} files.")
    print(f"Processed {processed_count} image files.")
    print(f"Clean images are located in: {output_dir}")


if __name__ == "__main__":
    # Check if paths are default, and warn user if so.
    if "YourUser" in INPUT_DIRECTORY or "path\\to" in INPUT_DIRECTORY:
        print("🚨  WARNING: Please update the INPUT_DIRECTORY and OUTPUT_DIRECTORY paths in the script before running.")
    else:
        process_directory(INPUT_DIRECTORY, OUTPUT_DIRECTORY)