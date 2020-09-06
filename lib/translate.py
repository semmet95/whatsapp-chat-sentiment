#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------
# module to translate text not in English language
# the module can even translate (to varying degree of success) text written in Roman script but not is not English
#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

from google.cloud import translate_v2 as translate
translate_client = translate.Client()

def get_language_code(text, target_language_code='en'):
    """returns the ISO code of the language of the text using GCP Cloud Translate"""

    translate_resp = translate_client.translate(text, target_language=target_language_code)
    return translate_resp['detectedSourceLanguage']

def get_translation(text, target_language_code, source_language_code):
    """returns the translated text"""

    translate_resp = translate_client.translate(text, target_language=target_language_code, source_language=source_language_code)
    return translate_resp['translatedText']

def translate_text(sentiment, text, target_language_code, language_script_code):
    """translates the tet to English if it's not already,
    return None if the translation fails"""

    text_translated = text
    text_language_code = get_language_code(text)

    if text_language_code != 'en':

        # change the text script to its corresponding language's script
        text_source_script = get_translation(text,
                                target_language_code=text_language_code, source_language_code=language_script_code)
        text_translated = get_translation(text_source_script,
                            target_language_code=target_language_code, source_language_code=text_language_code)

    if(len(text_translated) == 0):
        return None
    aws_lang_code = sentiment.get_language_code(text_translated)
    
    return text_translated if (get_language_code(text_translated) == 'en' and \
                                aws_lang_code['LanguageCode'] == 'en' and \
                                aws_lang_code['Score'] > 0.87) \
                                else None

def process_raw_text(sentiment, text_raw, key_exceptions, target_language_code='en', language_script_code='en'):
    """processes raw text and returns sentiment data and key phrases"""
    
    for key in key_exceptions:
        text_raw = text_raw.replace(key, key_exceptions[key])

    text_translated = translate_text(sentiment, text_raw, target_language_code, language_script_code)

    if text_translated is None or len(text_translated) == 0:
        return None
    
    text_sentiment = sentiment.get_sentiment(text_translated)
    text_key_phrase = sentiment.get_key_phrases(text_translated)

    return text_sentiment, text_key_phrase