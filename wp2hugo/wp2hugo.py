import logging
import argparse

from .wordpress import WordpressXMLParser
from .hugo import HugoWriter

logger = logging.getLogger(__name__)


def convert(input_file, output_dir, timezone, lang):
    """convert

    :param input_file: xml file
    :param output_dir: output dir for hugo
    """

    wp = WordpressXMLParser(input_file, timezone=timezone)

    hugo_writer = HugoWriter(output_dir)
    hugo_writer.write_config(
        title=wp.title,
        base_url=wp.base_url,
        description=wp.description,
        author=wp.author,
        lang=lang,
    )
    hugo_writer.write_posts(wp.posts, lang=lang)


def parse_args():
    """parse_args
    Get command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-file', required=True, help='xml file of Wordpress.com export')
    parser.add_argument(
        '--output-dir', default='hugo', help='output dir for hugo')
    parser.add_argument('--timezone', type=int, default=8)
    parser.add_argument('--lang', default='zh')
    return parser.parse_args()


def main():
    """main
    Entry point."""
    convert(**vars(parse_args()))


if __name__ == '__main__':
    main()
