from django.conf import settings
from django.apps import apps
from nlp import constants as Constants
import logging
import csv, os


logger = logging.getLogger(__name__)




def add_definitions(writer, definitions):
    for definition in definitions.all():
        writer.writerow(definition.as_row())


def generate_lang_csv(lang):
    try:
        langage = Constants.Langage.objects.get(slug=lang)
        filename = f"datasets/{langage.slug}/{langage.slug}.csv"
        words = Constants.Word.objects.filter(langage=langage)
        os.mkdirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(settings[Constants.WORD_FIELDS_KEY])
            ## generate headers
            for word in words:
                writer.writerow(word.as_row())
                if word.definitions:
                    add_definitions(writer, word.definitions)

            logger.info(f"csv datasets for langage {lang} generated in file {filename}")
    except Exception as e:
        logger.error(f"Error while generating csv datasets for langage {lang}: {e}", e)
    