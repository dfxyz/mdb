from markdown import Extension, util
from markdown.inlinepatterns import dequote, handleAttributes, IMAGE_LINK_RE, \
    ImagePattern


class MyImagePattern(ImagePattern):
    def handleMatch(self, m):
        div = util.etree.Element('div')
        div.set('class', 'image')

        img = util.etree.SubElement(div, 'img')
        src_parts = m.group(9).split()
        if src_parts:
            src = src_parts[0]
            if src[0] == "<" and src[-1] == ">":
                src = src[1:-1]
            img.set('src', self.sanitize_url(self.unescape(src)))
        else:
            img.set('src', "")
        if len(src_parts) > 1:
            img.set('title', dequote(self.unescape(" ".join(src_parts[1:]))))

        if self.markdown.enable_attributes:
            alt = handleAttributes(m.group(2), img)
        else:
            alt = m.group(2)

        if alt:
            description = util.etree.SubElement(div, 'div')
            description.set('class', 'description')
            description.text = alt

        return div


class MyImageExtension(Extension):
    """简书式的图片显示方式"""

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['image_link'] = MyImagePattern(IMAGE_LINK_RE, md)
