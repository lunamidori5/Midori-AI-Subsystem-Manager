
import argparse
import requests

from tqdm import tqdm

def download_file_from_midori_ai(filename, username, reponame, modeltype):
    """
    Download the file from the given URL to the given file 

    Args:
    filename: The name of the file to save the downloaded file to.
    username: The username for the Hugging Face account.
    reponame: The name of the Hugging Face repository to download the model from.
    modeltype: The name of the model to download.
    """
    
    url = f"https://tea-cup.midori-ai.xyz/huggingface/model/{modeltype}"

    chunk_size = 1024 * 1024 * 2
    
    headers = {
        'username': username,
        'reponame': reponame,
        'modeltype': modeltype
    }
    
    try:
        response = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=55)
        response.raise_for_status()

        total_size = int(response.headers.get("Content-Length", 0))
        
        with open(filename, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc=f'Downloading Model') as pbar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Download failed: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-un", "--username", type=str, required=True, help="The username for the Hugging Face account.")
    parser.add_argument("-r", "--reponame", type=str, required=True, help="The name of the Hugging Face repository to download the model from.")
    parser.add_argument("-m", "--modeltype", type=str, required=True, help="The name of the model to download.")
    args = parser.parse_args()

    filename = args.modeltype
    username = args.username
    reponame = args.reponame
    modeltype = args.modeltype

    # Download the file
    download_file_from_midori_ai(filename, username, reponame, modeltype)