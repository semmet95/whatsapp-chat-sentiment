#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
# module containing general purpose functions
# --------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------

import math
import random

def sigmoid(x):
    """returns sigmoid of a value"""

    return 1 / (1 + math.exp(-x))

def update_weights(all_phrases_weights, phrases_weights, phrase):
    """updates/adds weight of a key phrase"""

    if all_phrases_weights.get(phrase) is None:
        all_phrases_weights[phrase] = round(sigmoid(random.random() * phrases_weights[phrase]), 2)

    else:
        all_phrases_weights[phrase] = round(sigmoid(all_phrases_weights[phrase] \
                                            + (random.random() * phrases_weights[phrase])), 2)

def update_insights(text_insights, sentiment_data, key_phrases, key_exceptions, ctr):
    """uses the text insights from Comprehend and updates the over all insights data"""

    text_sentiment, text_key_phrase = text_insights

    for key in text_sentiment.keys():
        # is this the proper way of averaging out weights?
        sentiment_data[key] = round(((text_sentiment[key] + \
                                            sentiment_data[key] * (ctr - 1)) / ctr), 2)

    for key in list(text_key_phrase.keys()):
        # this is to make sure only alphanumeric phrases are included
        if not key.replace(' ', '').isalnum():
            continue

        update_weights(key_phrases, text_key_phrase, key)
