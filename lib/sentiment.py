#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
# module to get sentiment data for an input text string
# returns averaged out score of positive , negative, and neutral sentiments across all the texts,
# and key phrases with averaged out confidence
# --------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------

import boto3

sentiment_client = boto3.client('comprehend')

def get_language_code(text):
    """returns the detected dominant language of the text"""

    detected_languages = sentiment_client.detect_dominant_language(Text=text)['Languages']

    max_score = 0
    max_lang = None

    for language in detected_languages:
        if max_score < language['Score']:
            max_score = language['Score']
            max_lang = language['LanguageCode']

    return {'LanguageCode': max_lang, 'Score': max_score}

def get_key_phrases(text):
    """returns key phrases and their confidence in the text"""

    key_phrases_expanded = sentiment_client.detect_key_phrases(Text=text, LanguageCode='en')['KeyPhrases']
    key_phrases = {key_phrase['Text']: round(key_phrase['Score'], 2) for key_phrase in key_phrases_expanded}

    return key_phrases

def get_sentiment(text):
    """returns scores for the sentiments positive, negative, and neutral detected in the text"""

    sentiment_scores = sentiment_client.detect_sentiment(Text=text, LanguageCode='en')['SentimentScore']
    sentiment_scores.pop('Mixed', None)
    sentiment_scores = {sentiment[0]: round(sentiment[1], 2) for sentiment in sentiment_scores.items()}

    return sentiment_scores
