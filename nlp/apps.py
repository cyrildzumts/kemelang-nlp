import django
from django.apps import AppConfig, apps
from django.conf import settings
from nlp import constants as Constants
import logging

logger = logging.getLogger(__name__)

class NlpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nlp'

    def ready(self):
        logger.info("kemelang-nlp starting. Checking required settings ...")
        missing_settings = []
        for setting in Constants.REQUIRED_SETTINGS:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
                
        if len(missing_settings) > 0:
            msg = f"kemelang-nlp can not start. Required settings are missing : {missing_settings}. Please provide the settings in the global settings"
            logger.error(msg)
            raise Exception(msg)
        try:
            Constants.Langage = apps.get_model(getattr(settings,Constants.APP_NAME_KEY), getattr(settings, Constants.LANG_MODEL_NAME_KEY))
            Constants.Word = apps.get_model(getattr(settings, Constants.APP_NAME_KEY), getattr(settings, Constants.WORD_MODEL_NAME_KEY))
            Constants.Definition = apps.get_model(getattr(settings, Constants.APP_NAME_KEY), getattr(settings, Constants.DEFINITION_MODEL_NAME_KEY))
        except Exception as e:
            logger.warning("Error on getting required models : {e}. Please check the order on apps in the apps registry.", e)
            raise e
        
        import nlp.signals
        logger.info(f"kemelang-nlp started. Django Version {django.get_version()}")