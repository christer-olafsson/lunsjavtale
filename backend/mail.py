from logging import getLogger

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from django.conf import settings
from django.core.mail import EmailMessage
from django.forms.fields import EmailField
from django.template import Context, Template
from django.template.loader import get_template

from backend.utils import translate_text

SENDER = settings.DEFAULT_FROM_EMAIL
CHARSET = "UTF-8"


def get_cleaned_emails(emails):
    cleaned_emails = []
    e = EmailField()
    for email in emails:
        try:
            e.clean(email)
            cleaned_emails.append(email)
        except Exception as ex:
            print("Invalid Email", ex, email)
    return cleaned_emails


def divide_chunks(recipient, n):
    for i in range(0, len(recipient), n):
        yield recipient[i: i + n]


def send_mail(
    subject,
    body,
    recipient,
    attachments=[],
    attachments_files={},
    bcc=False
) -> None:
    recipient = recipient if type(recipient) == list else [recipient]
    recipient = get_cleaned_emails(recipient)
    print("got recipient")
    for chunk in divide_chunks(recipient, 50):
        print("sending mail to chunk", chunk, bcc)
        to_args = {}
        if bcc:
            to_args["bcc"] = chunk
        else:
            to_args["to"] = chunk
        msg = EmailMessage(
            subject, body, from_email=SENDER, **to_args
        )

        for attachment in attachments:
            msg.attach_file(attachment, mimetype="application/octet-stream")

        for name, attachment in attachments_files.items():
            msg.attach(name, attachment, mimetype="application/octet-stream")

        msg.content_subtype = "html"
        try:
            msg.send()
            print("Successful")
        except Exception as e:
            print(e, flush=True)


def send_direct_mail_by_default_bcc(
    subject,
    body,
    recipient,
    attachments=[],
    attachments_files={}
) -> None:
    recipient = recipient if type(recipient) == list else [recipient]
    recipient = get_cleaned_emails(recipient)
    print("got recipient")
    for chunk in divide_chunks(recipient, 50):
        print("sending mail to chunk by default bcc", chunk)
        to_args = {"to": chunk}
        if settings.DEFAULT_BCC_EMAIL:
            to_args["bcc"] = [settings.DEFAULT_BCC_EMAIL]
        msg = EmailMessage(
            subject, body, from_email=SENDER, **to_args
        )
        for attachment in attachments:
            msg.attach_file(attachment, mimetype="application/octet-stream")

        for name, attachment in attachments_files.items():
            msg.attach(name, attachment, mimetype="application/octet-stream")

        msg.content_subtype = "html"
        try:
            msg.send()
            print("Successful")
        except Exception as e:
            print(e, flush=True)


def send_mail_from_template_old(
    template,
    context_data,
    subject,
    recipient_list,
    attachments=[],
    bcc=False
) -> None:
    template = get_template(template)
    context = context_data
    body = template.render(context)
    print("got template")
    send_mail(subject, body, recipient_list, attachments, bcc=bcc)


def send_mail_from_template(
    template,
    context_data,
    subject,
    recipient_list,
    attachments=[],
    bcc=False,
    language="no"
) -> None:
    subject = translate_text(subject, language)
    body = translate_template(template, context_data, language)
    getLogger().info(f"got template fo ln -> {language}")
    send_mail(subject, body, recipient_list, attachments, bcc=bcc)


def translate_template(template_directory, context_data, target_language="no"):
    # Read the HTML template from the specified directory
    try:
        with open(template_directory, "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        getLogger().error(f"Error: The file at {template_directory} was not found.")
        return None

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Gather all text elements that need translation, ignoring template placeholders
    texts_to_translate = []
    elements_to_replace = []

    for element in soup.find_all(text=True):
        if element.parent.name not in ["script", "style"]:
            original_text = element.strip()
            if original_text and not ("{{" in original_text and "}}" in original_text):
                texts_to_translate.append(original_text)
                elements_to_replace.append(element)

    # Translate all text in a single batch with error handling
    try:
        translations = GoogleTranslator(source='auto', target=target_language).translate_batch(texts_to_translate)
    except Exception as e:
        getLogger().error(f"Translation failed: {e}")
        translations = texts_to_translate  # Fallback to original text if translation fails

    # Replace each original text with the translated text
    for element, translated_text in zip(elements_to_replace, translations):
        if translated_text:  # Ensure the translated text is not None
            element.replace_with(translated_text)
        else:
            getLogger().warning(f"Translation missing for: {element}")
            element.replace_with(element)  # Fallback to original text

    # Convert the translated HTML back to a string
    translated_html = str(soup)

    # Clean up unwanted prefixes or tags
    if translated_html.lower().startswith("<html>"):
        translated_html = translated_html[translated_html.find("<html>") + 6:].strip()
    if translated_html.lower().startswith("html-&gt;"):
        translated_html = translated_html.replace("html-&gt;", "", 1).strip()
    if translated_html.lower().startswith("html"):
        translated_html = translated_html[4:].strip()
    print(translated_html)
    # Load the translated HTML as a Django template
    translated_template = Template(translated_html)

    # Render the translated template with the provided context data
    rendered_template = translated_template.render(Context(context_data))

    return rendered_template
