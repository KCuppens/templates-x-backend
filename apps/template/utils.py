import pdfkit
from html2image import Html2Image
from htmldocx import HtmlToDocx


def convert_html_to_png(template):
    hti = Html2Image()
    image = hti.screenshot(
        html_file=template.content_html,
        save_as=f"template-{template.id}.png",
    )
    return image


def convert_html_to_pdf(template):
    return pdfkit.from_file(
        template.content_html, f"template-{template.id}.pdf"
    )


def convert_html_to_docx(template):
    parser = HtmlToDocx()
    return parser.parse_html_file(
        template.content_html, f"template-{template.id}.docx"
    )


def convert_html_to_jpeg(template):
    hti = Html2Image()
    image = hti.screenshot(
        html_file=template.content_html,
        save_as=f"template-{template.id}.jpeg",
    )
    return image
