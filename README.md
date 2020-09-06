# whatsapp-chat-sentiment
## Whtsapp Chat Sentiment Analyzer

Analyze Whatsapp texts with a friend using AWS Comprehend to get insights into the corresponding sentiments and key phrases of sent and received texts.


## Pre-requisites

The script uses AWS Comprehend to extract emotions and key phrases from texts, and GCP Translate to translate the texts to a target lanuage (English by default). So you need an AWS and GCP account, install the corresponding packages (in Requirements.txt file), enable the corresponding API, and set up the authentication.

You can follow these guides:-
To setup **boto3** api: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
To setup **gcp translate** api: https://cloud.google.com/translate/docs/setup