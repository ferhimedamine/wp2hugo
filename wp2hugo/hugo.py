import os
import sys
import logging

import yaml

from .html2md import HTML2MarkdownConverter

logger = logging.getLogger(__name__)


class HugoWriter(object):
    """HugoWriter"""

    def __init__(self, root_dir):
        """__init__

        :param root_dir:
        """
        self.root_dir = root_dir
        self.content_dir = os.path.join(root_dir, 'content')
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)

    def write_posts(self, posts, lang='zh'):
        post_dir = os.path.join(self.content_dir, lang, 'post')
        os.makedirs(post_dir, exist_ok=True)

        pages_dir = os.path.join(self.content_dir, lang, 'pages')
        os.makedirs(pages_dir, exist_ok=True)

        drafts_dir = os.path.join(self.content_dir, lang, 'drafts')
        os.makedirs(drafts_dir, exist_ok=True)

        html2md_converter = HTML2MarkdownConverter()

        for post in posts:
            if not post.date or post.status == 'draft':
                root_dir = drafts_dir
            elif post.post_type == 'page':
                root_dir = pages_dir
            elif post.status == 'private' or post.status == 'publish':
                root_dir = os.path.join(post_dir, post.date[:4])
            else:
                logger.error('unknown status: %s', post.status)
                sys.exit(1)

            os.makedirs(root_dir, exist_ok=True)

            meta_info = {
                'title': post.title,
                'categories': post.categories,
                'tags': post.tags,
                'date': post.date,
            }
            if post.status == 'private' or post.status == 'draft':
                meta_info['draft'] = True

            if post.slug:
                meta_info['slug'] = post.slug
                page_path = os.path.join(root_dir, post.slug + '.md')
            else:
                logger.warning('slug not present, use title: %s', post.title)
                page_path = os.path.join(root_dir, post.title + '.md')
            with open(page_path, 'w') as outfile:
                outfile.write(
                    yaml.dump(
                        meta_info,
                        default_flow_style=False,
                        explicit_start=True,
                        allow_unicode=True))
                outfile.write("---\n")
                if post.text:
                    logger.warning('> convert %s', page_path)
                    outfile.write(html2md_converter.process(post.text))
                    logger.warning('> done')

    def write_config(self, title, base_url, description, author, lang='zh'):
        """write_config

        :param title:
        :param base_url:
        :param description:
        :param author:
        :param lang:
        """
        conf = {
            'baseURL': base_url,
            'title': title,
            'defaultContentLanguage': lang,
            'author': {
                'name': author
            },
            'params': {
                'description': description,
            },
        }

        config_path = os.path.join(self.root_dir, 'config.yaml')
        with open(config_path, 'w') as outfile:
            outfile.write(
                yaml.dump(
                    conf,
                    default_flow_style=False,
                    explicit_start=True,
                    allow_unicode=True))
