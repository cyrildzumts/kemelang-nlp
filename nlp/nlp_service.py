from django.conf import settings
from django.apps import apps
from django.db.models import F, Q, Sum, Count, Max, Min, Avg
from django.utils import timezone
from nlp import constants as Constants
import shutil
import zipfile
import logging
import datetime
import csv, os, pathlib, json


logger = logging.getLogger(__name__)


def add_definitions(writer, definitions):
    for definition in definitions.annotate(unaccent=F('word__word__unaccent')):
        writer.writerow(definition.as_row())


def create_zipfile_from_directory(dir_path, archive_name):
    if not os.path.isdir(dir_path):
        return None
    
    if not archive_name:
        return None
    
    return shutil.make_archive(archive_name, 'zip', dir_path)


def create_zipfile(file_path_list, archive_name):
    for path in file_path_list:
        if not os.path.isfile(path):
            return None
    
    if not archive_name:
        return None
    
    try:
        base_dir = "datasets/archives"
        basename = f"{Constants.ARCHIVE_PREFIX}-{archive_name.lower()}"
        os.makedirs(base_dir, exist_ok=True)

        with zipfile.ZipFile(f"{base_dir}/{basename}.zip", 'w') as file:
            for path in file_path_list:
                file.write(path, os.path.basename(path))
                
    except Exception as e:
        logger.error(f"Error when creating archive for dataset : {archive_name} : {e}")
    
    return True


def get_archive(archive_name):
    if not archive_name:
        return None
    file_path = f"datasets/archives/{Constants.ARCHIVE_PREFIX}-{archive_name.lower()}.zip"
    path = pathlib.Path(file_path)
    if not path.exists():
            return None
    
    return file_path

def generate_lang_csv(lang):
    try:
        filename = f"datasets/vocabularies/{lang.slug}/{lang.slug}-{timezone.datetime.now().isoformat(sep='-',timespec='seconds')}.csv"
        words = Constants.Word.objects.filter(langage=lang).annotate(unaccent=F('word__unaccent')).order_by('word')
        dir_name = os.path.dirname(filename)
        os.makedirs(dir_name, exist_ok=True)
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(getattr(settings, Constants.WORD_FIELDS_KEY))
            ## generate headers
            for word in words:
                writer.writerow(word.as_row())
                if word.definitions:
                    add_definitions(writer, word.definitions)

            logger.info(f"csv datasets for langage {lang} generated in file {filename}")
        create_zipfile([filename], lang.slug)
        
    except Exception as e:
        logger.error(f"Error while generating csv datasets for langage {lang}: {e}", e)
        




def generate_word_grouped_data(words):
    grouped_data = {}
    count = 0
    for word in words:
        count += 1
        entry = word.as_kle_dict()
        key =(entry['word'], entry['type'])
        if key not in grouped_data:
            grouped_data[key] = {
                "word": entry['word'],
                "unaccent": entry['unaccent'],
                "definitions": [],
                "type": entry['type'],
                "verb_type": entry['verb_type'],
                "adverb_type": entry['adverb_type'],
                "contexts": set(),
                "plural": entry['plural'],
                "prefix_class": entry['prefix_class'],
                "class": entry['class'],
                "transliteration": entry['transliteration'],
                "audio": entry['audio'],
            }
            
        grouped_data[key]["definitions"].append(entry['definition'])
        if entry.get('context'):
            grouped_data[key]["contexts"].add(entry['context'])
    
    for key in grouped_data:
        
        grouped_data[key]["contexts"] = ",".join(sorted(grouped_data[key]["contexts"]))

        grouped_data[key]["definitions"] = ",".join(sorted(grouped_data[key]["definitions"]))

    
    return grouped_data
        
            

def generate_kle_lang_csv(lang):
    try:
        filename = f"datasets/vocabularies/{lang.slug}/kle-{lang.slug}-{timezone.datetime.now().isoformat(sep='-',timespec='seconds')}.csv"
        words = Constants.Word.objects.filter(langage=lang).annotate(unaccent=F('word__unaccent')).order_by('word')
        definitions = Constants.Definition.objects.filter(word__langage=lang).annotate(unaccent=F('word__word__unaccent'))
        dir_name = os.path.dirname(filename)
        if not words.exists():
            logger.warning(f"KLE - No words found for langage {lang}")
            return
        word_list = list(words) + list(definitions)
        grouped_data = generate_word_grouped_data(word_list)
        word_list = list(grouped_data.values())
        size = len(word_list)
        
        entry = word_list[0]
        os.makedirs(dir_name, exist_ok=True)
        
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, delimiter=";", fieldnames= entry.keys())
            writer.writeheader()
            writer.writerows(word_list)
            
            ## generate headers
            #for word in words:
            #    writer.writerow(word.as_row())
            #    if word.definitions:
            #        add_definitions(writer, word.definitions)

            logger.info(f"KLE - csv datasets for langage {lang} generated in file {filename} - size {size} entries")
        create_zipfile([filename], lang.slug)
        
    except Exception as e:
        logger.error(f"KLE - Error while generating csv datasets for langage {lang}: {e}", e)


def generate_lang_word_list_csv(lang):
    try:
        filename = f"datasets/vocabularies/{lang.slug}/{lang.slug}-word-list-{timezone.datetime.now().isoformat(sep='-',timespec='seconds')}.txt"
        words = Constants.Word.objects.filter(langage=lang).order_by('word')
        dir_name = os.path.dirname(filename)
        os.makedirs(dir_name, exist_ok=True)
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter="\n")
            #writer.writerow(getattr(settings, Constants.WORD_FIELDS_KEY))
            ## generate headers
            for word in words:
                writer.writerow([word.word])

            logger.info(f"csv word list for langage {lang} generated in file {filename}")
        create_zipfile([filename], f"{lang.slug}-word-list")
        
    except Exception as e:
        logger.error(f"Error while generating csv word list for langage {lang}: {e}", e)


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




def generate_lang_list():
    try:
        filename = f"datasets/languages/languages-{timezone.datetime.now().isoformat(sep='-',timespec='seconds')}.csv"
        queryset = Constants.Langage.objects.filter(is_active=True).exclude(code=None)
        dir_name = os.path.dirname(filename)
        os.makedirs(dir_name, exist_ok=True)
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(getattr(settings, Constants.LANG_CODES_FIELDS))
            ## generate headers
            for lang in queryset:
                writer.writerow([lang.name, lang.code])

            logger.info(f"csv list for langage codes generated in file {filename}")
        
    except Exception as e:
        logger.error(f"Error while generating csv word list for langage {lang}: {e}", e)


def generate_all_datasets():
    try:
        langages = Constants.Langage.objects.filter(is_active=True)
        for lang in langages:
            generate_kle_lang_csv(lang)
            generate_lang_csv(lang)
            generate_lang_word_list_csv(lang)
            generate_lang_sentences_csv(lang)
    except Exception as e:
        logger.warning(f"Error while generating datasets csv files : {e}", e)
        

def generate_datasets_for_language(lang_set):
    try:
        for lang in lang_set:
            generate_kle_lang_csv(lang)
            generate_lang_csv(lang)
            generate_lang_word_list_csv(lang)
            generate_lang_sentences_csv(lang)
    except Exception as e:
        logger.warning(f"Error while generating datasets csv files : {e}", e)