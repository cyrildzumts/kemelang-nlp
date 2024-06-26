from django.conf import settings
from django.apps import apps
from django.utils import timezone
from nlp import constants as Constants
import logging
import datetime
import csv, os


logger = logging.getLogger(__name__)


def add_definitions(writer, definitions):
    for definition in definitions.all():
        writer.writerow(definition.as_row())


def generate_lang_csv(lang):
    try:
        filename = f"datasets/{lang.slug}/{lang.slug}-{timezone.datetime.now().isoformat(sep='-',timespec='seconds')}.csv"
        words = Constants.Word.objects.filter(langage=lang)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(getattr(settings, Constants.WORD_FIELDS_KEY))
            ## generate headers
            for word in words:
                writer.writerow(word.as_row())
                if word.definitions:
                    add_definitions(writer, word.definitions)

            logger.info(f"csv datasets for langage {lang} generated in file {filename}")
    except Exception as e:
        logger.error(f"Error while generating csv datasets for langage {lang}: {e}", e)


def generate_all_datasets():
    try:
        langages = Constants.Langage.objects.filter(is_active=True)
        for lang in langages:
            generate_lang_csv(lang)
    except Exception as e:
        logger.warning(f"Error while generating datasets csv files : {e}", e)