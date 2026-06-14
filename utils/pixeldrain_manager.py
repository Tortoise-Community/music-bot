import os
import time
import requests


def sync_music(api_key, list_id, download_dir="music"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    auth = ("", api_key)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    list_url = f"https://pixeldrain.com/api/list/{list_id}"
    print(f"Fetching list data from: {list_url}")

    # ADDED: Retry logic for the initial API fetch
    data = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(list_url, auth=auth, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            break  # Success, exit the retry loop
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Fetch attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                print("❌ Failed to fetch list from Pixeldrain after retries.")
                return []

    if not data or not data.get("success"):
        error_val = data.get("value", "unknown_error") if data else "no_data"
        error_msg = data.get("message", "Unknown error occurred") if data else "Connection failed entirely"
        print(f"API Error [{error_val}]: {error_msg}")
        return []

    if "files" not in data:
        print("No files array found in the list response.")
        return []

    local_playlist = []

    for f in data["files"]:
        file_name = f.get("name", "")
        mime_type = f.get("mime_type", "")

        if not (file_name.lower().endswith(".mp3") or mime_type == "audio/mp3"):
            continue

        file_id = f.get("id")
        if not file_id:
            continue

        safe_name = "".join(c for c in file_name if c.isalnum() or c in " ._-")
        local_filename = f"{file_id}_{safe_name}"
        local_path = os.path.join(download_dir, local_filename)

        local_playlist.append({
            "name": file_name,
            "path": local_path
        })

        if os.path.exists(local_path):
            print(f"Skipping: {file_name} (Already exists)")
            continue

        print(f"Downloading: {file_name}...")
        download_url = f"https://pixeldrain.com/api/file/{file_id}"

        for attempt in range(max_retries):
            try:
                dl_resp = requests.get(download_url, auth=auth, headers=headers, stream=True, timeout=30)
                dl_resp.raise_for_status()

                with open(local_path, "wb") as out_file:
                    for chunk in dl_resp.iter_content(chunk_size=8192):
                        if chunk:
                            out_file.write(chunk)

                print(f"✅ Successfully downloaded: {file_name}")
                break

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Download attempt {attempt + 1}/{max_retries} failed for {file_name}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    print(f"❌ Failed to download {file_name}.")
                    local_playlist.pop()

        time.sleep(1)

    return local_playlist
