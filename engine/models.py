from django.db import models
import hashlib

CRAWLERS = [
    [0, 'Main DB'],
    [1, 'Crawler 1'], 
    [2, 'Crawler 2'],
    [3, 'Crawler 3'],
    [4, 'Crawler 4'],
    [5, 'Crawler 5'],
    [6, 'Crawler 6']
]

class WebPage(models.Model):
    url = models.TextField(verbose_name='Page URL', max_length=1000)
    url_update = models.TextField(verbose_name='Page URL', blank=True)
    raw_html = models.TextField(verbose_name='Raw Html', blank=True)
    url_hash = models.CharField(verbose_name='URL Hash', max_length=255, unique=True)
    content_hash = models.CharField(verbose_name='Content Hash', max_length=255, blank=True)
    status = models.SmallIntegerField(verbose_name='Request status', default=0)
    content_type = models.CharField(verbose_name='Response content type', max_length=200, blank=True)
    crawled = models.BooleanField(verbose_name='Successfully crawled', default=False)
    in_links = models.ManyToManyField('WebPage', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #crawler_ip = models.CharField(max_length=255, default='0')
    indexed = models.BooleanField(verbose_name='Successfully indexed', default=False)

    # Added for performance
    #out_links = models.ManyToManyField('WebPage', blank=True)

    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        # Implement hashing here
        m = hashlib.md5()
        m.update(self.url.encode('utf-8'))
        self.url_hash = m.hexdigest()
        super(WebPage, self).save(*args, **kwargs)

    # def get_raw_html(self):
    #     #client = MongoClient('mongodb://localhost:27017/')
    #     #m_pages = client.crawler_dumps.pages
    #     pass

    # def set_out_links(self, x):
    #     self.out_links = json.dumps(x)

    # def get_out_links(self):
    #     return json.loads(self.out_links)

        




#GoogleScraper -m http --keyword 'site:cs.ucl.ac.uk' --num-workers 10 --search-engines "google" --output-filename output.json -v2




