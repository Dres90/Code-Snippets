import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
from os.path import exists


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_images(url):

    if is_valid(url):
        soup = bs(requests.get(url).content, "html.parser")
    elif exists(url):
        text_file = open(url, "r")
        data = text_file.read()
        text_file.close()
        soup = bs(data, "html.parser")
    else:
        raise Exception("Not a valid URL or file")
    """
    Returns all image URLs on a single `url`
    """
    
    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)
        # remove URLs like '/hsts-pixel.gif?c=3.2.5'
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        # finally, if the url is valid
        if img_url.startswith("//"): img_url = "http:" + img_url
        if is_valid(img_url):
            urls.append(img_url)
        else:
            print("Not valid url %s"%img_url)
    return urls


def download(url, pathname, prefix):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, prefix + "-" + url.split("/")[-1])

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


def main(url, path):
    # get all images
    imgs = get_all_images(url)
    length = len(str(len(imgs)))
    for idx, img in enumerate(imgs):
        # for each img, download it
        download(img, path, str(idx+1).zfill(length))
    


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="This script downloads all images from a web page")
    parser.add_argument("url", help="The URL of the web page you want to download images")
    parser.add_argument("-p", "--path", help="The Directory you want to store your images, default is the domain of URL passed")
    
    args = parser.parse_args()
    url = args.url
    path = args.path

    if not path:
        # if path isn't specified, use the domain name of that url as the folder name
        path = urlparse(url).netloc
    
    main(url, path)