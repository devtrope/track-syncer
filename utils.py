import hashlib
import os
import requests # type: ignore

def compute_file_hash(file_path: str) -> str:
    """Compute the SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()

def get_files_list(folder_path: str, accepted_extensions: list) -> list:
    """Get a list of files in the specified folder with their metadata."""
    files_infos = []

    for (root, dirs, files) in os.walk(folder_path):
        for file in files:
            if not any(file.lower().endswith(ext) for ext in accepted_extensions):
                continue

            absolute_path = os.path.join(root, file)
            relative_path = os.path.relpath(absolute_path, folder_path)

            file_info = {
                'path': relative_path,
                'hash': compute_file_hash(absolute_path),
            }

            files_infos.append(file_info)

    return files_infos

def upload_file_in_chunks(file_info: dict, folder_path: str, api_url: str, chunk_size: int = 1024 * 1024) -> tuple:
    """Upload a file in chunks to the remote server."""
    file_path = os.path.join(folder_path, file_info['path'])
    total_chunks = (os.path.getsize(file_path) + chunk_size - 1) // chunk_size
    filename = os.path.basename(file_info['path'])

    with open(file_path, 'rb') as f:
        for chunk_index in range(total_chunks):
            chunk_data = f.read(chunk_size)

            files = {
                'chunk': (f'{filename}.part{chunk_index}', chunk_data),
            }
            data = {
                'filename': filename,
                'chunk_index': chunk_index,
                'total_chunks': total_chunks,
                'hash': file_info['hash'],
            }

            response = requests.post(api_url + '/upload.php', files=files, data=data, timeout=120)

            if response.status_code != 200:
                raise requests.HTTPError(
                    f"Failed to upload chunk {chunk_index} for {file_info['path']}: {response.text}"
                )
            
    return 200, {"message": f"{filename} uploaded in {total_chunks} chunks."}
         