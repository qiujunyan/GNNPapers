import requests
from bs4 import BeautifulSoup as bs
import urllib.request
import os
from multiprocessing import Pool


def html2text(url):
    req = requests.get(url)
    text = req.text
    return text


def get_name(a):
    for p in a.parents:
        if p.name == "ol":
            if len(p.attrs) == 0:
                sibling = p.find_previous_sibling("h2").find("a", attrs={"href": "#content"})
            else:
                p = p.find_parent("details")
                sibling = p.find_previous_sibling("h2").find("a", attrs={"href": "#content"})
            return sibling.text


def parse(url):
    saved_dir = os.path.join(os.getcwd(), "GNN")
    if not os.path.isdir(saved_dir):
        os.mkdir(saved_dir)

    text = html2text(url)
    soup = bs(text, "lxml")

    downld_info = []
    for i, a in enumerate(soup.find_all("a", attrs={"rel": "nofollow"}, string="paper")):
        category = os.path.join(saved_dir, get_name(a))
        if not os.path.isdir(category):
            os.mkdir(category)
        downld_info.append((a["href"], os.path.join(category, a.parent.text[:-6]+"pdf")))
    return downld_info


def download(url, file):
    # print("downloading {}".format(url))
    # urllib.request.urlretrieve(url, file)
    try:
        print("downloading {}".format(url))
        urllib.request.urlretrieve(url, file)
    except Exception as _:
        bad_downloads.append(url)
        print("{} not download".format(url))
        os.remove(file)


def main(raw_url):
    downld_info = parse(raw_url)
    p = Pool()
    for url, file in downld_info:
        p.apply_async(download, args=(url, file))
        # download(url, file)
    p.close()
    p.join()


if __name__ == "__main__":
    bad_downloads = []
    main("https://github.com/thunlp/GNNPapers")
    print("total bad downloads: {}".format(len(bad_downloads)))
    with open("bad_downloads.txt", "w") as file:
        for bad_downld in bad_downloads:
            file.write(bad_downld)
