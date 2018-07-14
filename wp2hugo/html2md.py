import logging
import re
import textwrap

from bs4 import BeautifulSoup, NavigableString

logger = logging.getLogger(__name__)


class HTML2MarkdownConverter(object):
    """HTML2MarkdownConverter

    Convert Wordpress favoured HTML to Hugo favoured Markdown.
    """

    def process(self, html, skip_container=True):
        root = soup = BeautifulSoup(html.strip(), 'html.parser')

        if skip_container:
            # skip outer most div
            children = list(soup.children)
            if len(children) == 1 and children[0].name == 'div':
                root = children[0]

        return self.process_node(
            root, soup=soup, skip_root=True).strip() + '\n'

    def process_node(self, node, soup, skip_root=False):
        content = ''

        # check for anchor
        if not skip_root and 'id' in node.attrs and len(list(
                node.children)) > 0:
            anchor = soup.new_tag('a', id=node.attrs['id'])
            node.insert(0, anchor)

        for item in node.children:
            if isinstance(item, NavigableString):
                next_content = self.convert_text(item.output_ready())
            else:
                next_content = self.process_node(item, soup=soup)

            if content.endswith('\n') and next_content.startswith('\n'):
                next_content = next_content.lstrip('\n')

            content += next_content

        if not skip_root:
            content = self.convert_tag(node, content)

        return content

    def convert_tag(self, node, content):
        if node.name in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            return self.convert_header(node, content, level=int(node.name[-1]))
        elif node.name in {'ol', 'ul'}:
            return self.convert_list(node, content)
        else:
            convert_fn = getattr(self, 'convert_' + node.name, None)
            if convert_fn:
                return convert_fn(node, content)

        logger.warning('unknown tag %s preserved', node.name)
        if content.strip():
            attrs = ' '.join([
                '{}="{}"'.format(key, value)
                for key, value in node.attrs.items()
            ])
            if attrs:
                attrs = ' ' + attrs
            return '<{}{}>{}</{}>'.format(node.name, attrs, content, node.name)
        else:
            return node.prettify()

    def convert_text(self, text):
        text = re.sub(r'\n\n*', '\n\n', text)
        return text.replace('_', r'\_').replace('*', r'\*')

    def convert_p(self, node, content):
        return '{}\n\n'.format(content) if content else ''

    def convert_strong(self, node, content):
        return '**{}**'.format(content) if content else ''

    def convert_b(self, node, content):
        return self.convert_strong(node, content)

    def convert_blockquote(self, node, content):
        return '\n\n' + textwrap.indent(content,
                                        '> ') + '\n\n' if content else ''

    def convert_br(self, node, content):
        return '\n'

    def convert_em(self, node, content):
        return '_%s_' % content if content else ''

    def convert_i(self, node, content):
        return self.convert_em(node, content)

    def convert_img(self, node, content):
        alt = node.attrs.get('alt', '')
        src = node.attrs.get('src', '')
        align = node.attrs.get('align', '')
        if align == '':
            for cls in node.attrs.get('class', []):
                if 'align' in cls and 'none' not in cls:
                    align = cls
        else:
            align = 'align' + align
        title = node.attrs.get('title', '')
        width = node.attrs.get('width', '')
        height = node.attrs.get('height', '')

        matched_src = re.match(r'https?://[^.]*\.files.wordpress.com/(.+)',
                               src)
        if matched_src:
            src = '/images/' + matched_src.group(1)

        if align:
            if alt:
                alt = ' alt="{}"'.format(alt)
            if title:
                title = ' title="{}"'.format(title)
            if width:
                width = ' width="{}"'.format(width)
            if height:
                height = ' height="{}"'.format(height)

            cls = ' class="{}"'.format(align)

            return '{{<figure src="%s"%s%s%s%s%s>}}' % (src, alt, title, cls,
                                                        width, height)
        else:
            logger.warning('image not formatted: %s', src)
            title = ' "{}"'.format(title.replace('"', r'\"')) if title else ''
            return '![%s](%s%s)' % (alt, src, title)

    def convert_a(self, node, content):
        if 'id' in node.attrs and len(list(node.children)) == 0:
            # output anchor
            return node.prettify()

        href = node.attrs.get('href', '')
        title = node.attrs.get('title', '')
        # remove invalid links
        if not href:
            logger.warning('invalid tag a not converted: %s', node.prettify())
            return content

        title = ' "{}"'.format(title.replace('"', r'\"')) if title else ''
        return '[{}]({}{})'.format(content, href, title)

    def convert_header(self, node, content, level=1):
        hashes = '#' * level
        return '\n\n{} {}\n\n'.format(hashes, content)

    def convert_list(self, node, content):
        nested = False
        while node:
            if node.name == 'li':
                nested = True
                break
            node = node.parent
        if nested:
            content = textwrap.indent(content, '  ') if content else ''
        return '\n\n' + content.rstrip() + '\n\n'

    def convert_li(self, node, content):
        if not content:
            logger.warning('invalid tag li not converted: %s', node.prettify())
        parent = node.parent
        if parent is not None and parent.name == 'ol':
            lis = [item for item in parent.children if item.name == 'li']
            bullet = '1.'
            for n, item in enumerate(lis, start=1):
                if item is node:
                    bullet = '{}.'.format(n)
        else:
            bullet = '*'
        return '{} {}\n'.format(bullet, content)
