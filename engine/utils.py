import requests

def get_redirected_link(page_url):
    try:
        req = requests.get(page_url, stream=True, timeout=5)
        req.raise_for_status()
    except:
        return page_url
    else:
        return req.url

def get_links(url_list):
    new_urls = list()
    for url in url_list:
        new_urls.append(get_redirected_link(url))
    return new_urls