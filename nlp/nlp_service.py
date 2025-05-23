from django.conf import settings
from django.apps import apps
from django.db.models import F, Q, Sum, Count, Max, Min, Avg
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
        filename = f"datasets/vocabularies/{lang.slug}/{lang.slug}-{timezone.datetime.now().isoformat(sep='-',timespec='seconds')}.csv"
        words = Constants.Word.objects.filter(langage=lang).annotate(unaccent=F('word__unaccent'))
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


def generate_lang_sentences_csv(lang):
    current_datetime = timezone.datetime.now().isoformat(sep='-',timespec='seconds')
    try:
        sentences = Constants.Phrase.objects.filter(langage=lang).annotate(unaccent=F('content__unaccent'))
        for sentence in sentences:
            translations = sentence.translations.all()

            for translation in translations:
                filename = f"datasets/sentences/{lang.slug}/{lang.slug}-{translation.langage.slug}-{current_datetime}.csv"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'a') as f:
                    writer = csv.writer(f, delimiter=";")
                    #writer.writerow(getattr(settings, Constants.PHRASE_FIELDS_KEY))
                    ## generate headers
                    writer.writerow([sentence.content, sentence.unaccent, translation.content])
                    logger.info(f"csv sentences datasets for langages {lang.slug}-{translation.langage.slug} generated in file {filename}")
    except Exception as e:
        logger.error(f"Error while generating csv sentences datasets for langage {lang}: {e}", e)


def generate_all_datasets():
    try:
        langages = Constants.Langage.objects.filter(is_active=True)
        for lang in langages:
            generate_lang_csv(lang)
            generate_lang_sentences_csv(lang)
    except Exception as e:
        logger.warning(f"Error while generating datasets csv files : {e}", e)
        

def generate_datasets_for_language(lang_set):
    try:
        for lang in lang_set:
            generate_lang_csv(lang)
            generate_lang_sentences_csv(lang)
    except Exception as e:
        logger.warning(f"Error while generating datasets csv files : {e}", e)