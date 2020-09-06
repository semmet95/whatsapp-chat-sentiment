# whatsapp-chat-sentiment
## Whtsapp Chat Sentiment Analyzer

Analyze Whatsapp texts with a friend using AWS Comprehend to get insights into the corresponding sentiments and key phrases of sent and received texts.


## Pre-requisites

The script uses AWS Comprehend to extract emotions and key phrases from texts, and GCP Translate to translate the texts to a target lanuage (English by default). So you need an AWS and GCP account, install the corresponding packages (in Requirements.txt file), enable the corresponding API, and set up the authentication.

#### You can follow these guides
#### To setup **boto3** api: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
#### To setup **gcp translate** api: https://cloud.google.com/translate/docs/setup

**Note** : After activating GCP Translate API, place the json key file in the gcp folder

## Running the script

Install all the dependencies using the **requirements.txt** file.

Update the **config.json** file.
- Add GCP json key file name under **gcp auth file**.
- Add the name of the friend you want to analyze texts with under **chat with**.
- Set **scroll count** to the number of times you want to scroll up to retrience older chats (approximately).
- Set **wait time** to thenumber of seconds you want the script to wait for older texts to load before scrolling up.
- Set **language script code** to the ISO language code of the script used in the texts.

Run the **main.py** file
```
python3 main.py
```
Open Whatsapp app in your phone, scan the QR Code and let Selenium handle the rest.

Once all the texts have been scraped, the script uses GCP Translate and AWS Comprehend API to translate and analyze the texts to extract sentiment data and key phrases, categorized under texts sent by you and texts received.

The sentiment data and key phrases are exported to a csv file in the **exports** folder.