"""
download_images.py
==================

Crawl all local images on Wordpress.com.
"""
import re
import os
import logging
import argparse

import tqdm
import requests

logger = logging.getLogger(__name__)


def download_images(name, input_file, output_dir, overwrite):
    """download_images

    :param name: user id
    :param input_file: xml file
    :param output_dir: output images to this directory
    :param overwrite: whether not to skip existing files
    """
    regex = re.compile(
        r'"(https?://{}.files.wordpress.com[^?"]*)("|\?)'.format(name))
    with open(input_file) as infile:
        content = infile.read()

    urls = set([m[0] for m in regex.findall(content)])
    logger.warning('found %d urls.', len(urls))

    for url in tqdm.tqdm(urls):
        dirs = os.path.dirname(url).split('/', 3)
        image_dir = os.path.join(output_dir, dirs[-1])
        os.makedirs(image_dir, exist_ok=True)

        image_path = os.path.join(image_dir, os.path.basename(url))
        if overwrite or not os.path.exists(image_path):
            with open(image_path, 'wb') as outfile:
                outfile.write(requests.get(url).content)


def parse_args():
    """parse_args
    Get command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--name', required=True, help='user id of the Wordpress.com blog')
    parser.add_argument(
        '--input-file', required=True, help='xml file of Wordpress.com export')
    parser.add_argument(
        '--output-dir',
        default='hugo/static/images',
        help='output dir for images')
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='do not skip images that already exist')
    return parser.parse_args()


def main():
    """main
    Entry point."""
    download_images(**vars(parse_args()))


if __name__ == '__main__':
    main()
