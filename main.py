import os
import time
from tabulate import tabulate
from collections import Counter
import queue
import threading
import concurrent.futures
import json
import csv
import itertools as it
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

##---------------------------------------------------------------------------------------------------------##
##---------------------------------------------------------------------------------------------------------##

curr_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(curr_dir, 'config', 'config.json')) as f:
    config = json.load(f)

webdriver_path = os.path.join(curr_dir, 'bin', 'chromedriver')
auth_json_path = os.path.join(curr_dir, 'gcp', config['gcp']['gcp auth file'])
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = auth_json_path

out_div_class_names = config['selenium']['out div class names']
in_div_class_names = config['selenium']['in div class names']
qrscan_class_name = config['selenium']['qr scan class name']
lock_class_name = config['selenium']['lock class name']
searchbar_class_name = config['selenium']['search bar class name']
msg_class_name_common = config['selenium']['msg class name common']
msg_span_class = config['selenium']['msg span class']
msg_body_class = config['selenium']['msg body class']

chat_with = config['chat with']
url = config['url']

from lib import *

# path to the chromedrive file
driver = webdriver.Chrome(webdriver_path)
driver.get(url)

##---------------------------------------------------------------------------------------------------------##
## helper functions
##---------------------------------------------------------------------------------------------------------##

def texts_from_divs(msgs_divs, class_name):
    """extracts texts from divs"""

    return [msg_div.find_elements_by_css_selector(class_name)[0].text.strip() for msg_div in msgs_divs \
                if len(msg_div.find_elements_by_css_selector(class_name)) > 0]

##---------------------------------------------------------------------------------------------------------##
##---------------------------------------------------------------------------------------------------------##

# wait till the QR code is visible
wait = WebDriverWait(driver, 20)
wait.until(EC.visibility_of_element_located((By.XPATH, "//canvas[@aria-label='" + qrscan_class_name +"']")))

# wait to get the QR code scanned
while(len(driver.find_elements_by_xpath("//canvas[@aria-label='Scan me!']")) > 0):
    time.sleep(1)

# find a way to hide the window??

# wait till the search bar is visible
wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='" + searchbar_class_name + "']")))

# now search for the friend to chat with
search_bar = driver.find_elements_by_xpath("//div[@class='{}']".format('_3FRCZ copyable-text selectable-text'))[0]
search_bar.click()
search_bar.send_keys(chat_with)
wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@title='" + chat_with + "']")))

print('scraping texts with', chat_with)
driver.find_element_by_xpath("//span[@title='" + chat_with + "']").click()

msgs_in, msgs_out = text_scraper.get_msg_divs_all(Keys, driver, msg_body_class, in_div_class_names, out_div_class_names, \
                                            msg_class_name_common, lock_class_name, \
                                            scroll_count=config['scroll count'], wait_timer=config['wait time'])

print('extracting sent and received messages from text divs')
all_sent_msgs = []
all_received_msgs = []

with concurrent.futures.ThreadPoolExecutor() as executor:

    futures = [executor.submit(texts_from_divs, msgs_out, msg_span_class), \
                executor.submit(texts_from_divs, msgs_in, msg_span_class)]
    all_sent_msgs, all_received_msgs = futures[0].result(), futures[1].result() 

print(len(all_sent_msgs), 'and', len(all_received_msgs))
driver.close()

##---------------------------------------------------------------------------------------------------------##
##---------------------------------------------------------------------------------------------------------##
## now let's use the nlp module
##---------------------------------------------------------------------------------------------------------##
##---------------------------------------------------------------------------------------------------------##

target_language_code = config['target language code']
language_script_code = config['language script code']

sentiment_data_you = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
key_phrases_you = {}
ctr_you = [0]
sentiment_data_me = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
key_phrases_me = {}
ctr_me = [0]

key_exceptions = config['key exceptions']

q = queue.Queue()

##---------------------------------------------------------------------------------------------------------##
## helper functions
##---------------------------------------------------------------------------------------------------------##

def api_request():
    """send api requests getting arguments from the queue"""

    while True:
        ctr, text, sentiment_data, key_phrases = q.get()

        text_insights = translate.process_raw_text(sentiment, text, key_exceptions, target_language_code, language_script_code)

        if text_insights is not None:
            # keeping track of number texts received that we're getting insights for
            with threading.Lock():
                ctr[0] += 1
                utils.update_insights(text_insights, sentiment_data, key_phrases, key_exceptions, ctr[0])

            print('\n', tabulate([[list(sentiment_data_you.values()), list(sentiment_data_me.values()), \
                        Counter(key_phrases_you).most_common()[:3], Counter(key_phrases_me).most_common()[:3]]], \
                        headers=['youSentiment(+, -, 0)', 'meSentiment(+, -, 0)', \
                                    'you_key_phrases', 'me_key_phrases']))
            #print('\n\n', ctr_you, ctr_me, ctr, '\n\n')
        q.task_done()

##---------------------------------------------------------------------------------------------------------##
##---------------------------------------------------------------------------------------------------------##

# initiate threads to send api requests parallely
num_threads = 10
for i in range(num_threads):

    request_thread = threading.Thread(target = api_request)
    request_thread.daemon = True
    request_thread.start()

# process the texts
for me_text, you_text in zip(all_sent_msgs, all_received_msgs):

    me_text, you_text = me_text.lower(), you_text.lower()

    q.put((ctr_you, you_text, sentiment_data_you, key_phrases_you))
    q.put((ctr_me, me_text, sentiment_data_me, key_phrases_me))
    
# process the remaining texts for whichever list is the bigger one
bigger_list, sentiment_data, key_phrases = (all_received_msgs[len(all_sent_msgs):], sentiment_data_you, key_phrases_you) \
                                                if len(all_received_msgs) > len(all_sent_msgs) \
                                                else (all_sent_msgs[len(all_received_msgs):], sentiment_data_me, key_phrases_me)

ctr = [0]
for text in bigger_list:

    text = text.lower()
    q.put((ctr, text, sentiment_data, key_phrases))

# wait for all the api calls to finish updating the sentiments and key phrases
q.join()

# export the sentiment data and the key phrases
key_phrases_you_sorted = {k: v for k, v in sorted(key_phrases_you.items(), \
                            key = lambda item: item[1], reverse = True)}
key_phrases_me_sorted = {k: v for k, v in sorted(key_phrases_me.items(), \
                            key = lambda item: item[1], reverse = True)}

sentiment_data_you_sorted = {k: v for k, v in sorted(sentiment_data_you.items(), \
                                key = lambda item: item[0], reverse=True)}
sentiment_data_me_sorted = {k: v for k, v in sorted(sentiment_data_me.items(), \
                                key = lambda item: item[0], reverse=True)}

timestamp = str(datetime.now())
timestamp = timestamp[:timestamp.find('.')]
csv_name = chat_with + "_" + timestamp
csv_path = curr_dir + "/exports/" + csv_name + ".csv"

with open(csv_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['received texts sentiment', 'received texts sentiment value', \
                        'received texts key phrases', 'received texts key phrases value', \
                        'sent texts sentiment', 'sent texts sentiment value', \
                        'sent texts key phrases', 'sent texts key phrases value'])
    writer.writerows(it.zip_longest(sentiment_data_you_sorted.keys(), sentiment_data_you_sorted.values(), \
                            key_phrases_you_sorted.keys(), key_phrases_you_sorted.values(), \
                            sentiment_data_me_sorted.keys(), sentiment_data_me_sorted.values(), \
                            key_phrases_me_sorted.keys(), key_phrases_me_sorted.values(),
                            fillvalue=""))