import pdfkit
from htmldocx import HtmlToDocx


def convert_html_to_png(template):
    image = hti.screenshot(
        html_file=template.content_html,
        save_as=f'template-{template.id}.png',
    )
    return image


def convert_html_to_pdf(html_file):
    return pdfkit.from_file(html_file, f'template-{template.id}.pdf')


def convert_html_to_docx(html_file):
    parser = HtmlToDocx()
    return parser.parse_html_file(html_file, f'template-{template.id}.docx')


def convert_html_to_jpeg(html_file):
    image = hti.screenshot(
        html_file=template.content_html,
        save_as=f'template-{template.id}.jpeg',
    )
    return image