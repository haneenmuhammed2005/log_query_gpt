import requests
import os
from tqdm import tqdm


def download_file(url, filename):
    """Download a file from a URL with a progress bar"""

    print(f"📥 Downloading {filename}...")

    response = requests.get(url, stream=True)
    response.raise_for_status()  # stop if error

    total_size = int(response.headers.get("content-length", 0))

    # Create folder if it doesn't exist
    os.makedirs("data/raw_logs", exist_ok=True)

    filepath = os.path.join("data", "raw_logs", filename)

    # Download file in chunks
    with open(filepath, "wb") as file, tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        desc=filename
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                pbar.update(len(chunk))

    print(f"✅ Saved to {filepath}")


# LogHub dataset URLs
urls = {
    "HDFS_2k.log": "https://raw.githubusercontent.com/logpai/loghub/master/HDFS/HDFS_2k.log",
    "BGL_2k.log": "https://raw.githubusercontent.com/logpai/loghub/master/BGL/BGL_2k.log"
}


# Download all datasets
for filename, url in urls.items():
    download_file(url, filename)

print("\n✅ All datasets downloaded!")
