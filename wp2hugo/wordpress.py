import xml.etree.ElementTree as ET
import logging
from io import StringIO
from collections import namedtuple

import html2text

Post = namedtuple('Post',
                  'title slug date status post_type categories tags text')

logger = logging.getLogger(__name__)


class WordpressXMLParser(object):
    def __init__(self, path, timezone=8):
        self.timezone = timezone
        with open(path) as infile:
            content = infile.read().replace('\0', '')
            self.root = ET.parse(StringIO(content))
        self.namespaces = {
            'wp': 'http://wordpress.org/export/1.2/',
            'content': 'http://purl.org/rss/1.0/modules/content/',
        }
        self._parse_meta()
        self.posts = self._parse_posts()

    def _parse_posts(self, allowed_post_types=('post', 'page')):
        if allowed_post_types:
            allowed_post_types = set(allowed_post_types)
        else:
            allowed_post_types = set()

        posts = []
        for item in self.root.findall('./channel/item'):
            post = self._parse_post(item)
            if post.post_type in allowed_post_types:
                posts.append(post)
        return posts

    def _parse_meta(self):
        self.title = self.root.find('./channel/title').text
        self.base_url = self.root.find(
            './channel/wp:base_blog_url', namespaces=self.namespaces).text
        self.description = self.root.find('./channel/description').text
        self.author = self.root.find(
            './channel//wp:author_display_name',
            namespaces=self.namespaces).text

    def _parse_date(self, text):
        date, timestamp = text.split(' ')
        return '{}T{}{:+03d}:00'.format(date, timestamp, self.timezone)

    def _parse_post(self, item):
        title = item.find('./title').text
        slug = item.find('./wp:post_name', namespaces=self.namespaces).text
        date = self._parse_date(
            item.find('./wp:post_date', namespaces=self.namespaces).text)
        status = item.find('./wp:status', namespaces=self.namespaces).text
        post_type = item.find(
            './wp:post_type', namespaces=self.namespaces).text
        tags, categories = [], []
        for category in item.findall('./category'):
            domain = category.attrib['domain']
            if domain == 'category':
                categories.append(category.text)
            elif domain == 'post_tag':
                tags.append(category.text)
            else:
                logger.warning('Unknown category domain: %s', domain)

        text = item.find('./content:encoded', namespaces=self.namespaces).text
        return Post(title, slug, date, status, post_type, categories, tags,
                    text)
