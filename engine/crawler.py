import sys
from lxml import html
import fnmatch
import requests
from urllib.parse import urlparse
from requests.exceptions import (
    ConnectionError, 
    Timeout, 
    TooManyRedirects,
    HTTPError
)

REGEX = '^https?:\/\/.*?\.?ucl\.ac\.uk\/'


def get_host(url):
    p = urlparse(url)
    return "{}://{}".format(p.scheme, p.netloc)

def get_page_links(url, doc):
    host = get_host(url)
    links = doc.xpath('//a[@href]')
    out_links = list()
    for link in links:
        href = link.attrib['href']

        if not href.startswith(('http://', 'https://')):
            if href.startswith('//'):
                href = 'http:' + href
            elif href.startswith('/'):
                href = host + href
            else:
                parent_url = url.rsplit('/', 1)[0]
                href = '{}/{}'.format(parent_url, href)
        
        if (fnmatch.fnmatch(href, '*cs.ucl.ac.uk*') 
            and not fnmatch.fnmatch(href, '*search2.ucl.ac.uk*')):
            out_links.append(href)

    return out_links


def get_page(url, single=False):
    status = 0
    try:
        req = requests.get(url, stream=True, timeout=5)
        req.raise_for_status()
    except ConnectionError:
        status = 520
    except Timeout:
        status = 408
    except TooManyRedirects:
        status = 310
    except HTTPError:
        status = req.status_code
    except:
        status = 999
    else:
        status = req.status_code
        print(status)
        print(req.headers.get('content-type'))
        if not req.headers.get('content-type'):
            return True, status, {
                    'raw': None,
                    'out_links': None,
                    'content_type': 'Unknown'
                }
        elif req.headers.get('content-type') and not 'html' in req.headers.get('content-type'):
            return True, status, {
                    'raw': None,
                    'out_links': None,
                    'content_type': req.headers.get('content-type')
                }
        else:
            if single:
                return True, status, {
                    'raw': req.text,
                    'out_links': [],
                    'content_type': req.headers.get('content-type')
                }

            try:
                doc = html.fromstring(req.content)
                out_links = get_page_links(url, doc)
            except:
                return False, status
            else:
                return True, status, {
                    'raw': req.text,
                    'out_links': out_links,
                    'content_type': req.headers.get('content-type')
                }
    return False, status


#http://pinterest.com/pin/create/button/?url=https://www.ucl.ac.uk/catalytic-enviro-group/?p=2209
#https://www.ucl.ac.uk/catalytic-enviro-group/wp-content/uploads/2016/03/SUSC18231.pdf
