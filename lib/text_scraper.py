#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
# module containing functions to scrap whatsapp texts with a friend
# --------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------

import time

def get_msg_divs_all(Keys, driver, body_class_name, div_class_names_in, div_class_names_out, msg_class_name_common, \
                        lock_class_name, scroll_count=100, wait_timer=2):
    """returns list of all texts divs of the input class names"""
    ctr = progress_index = 0
    progress = ['.  ', '.. ', '...']
    all_msg_divs_in = [None] * len(div_class_names_in)
    all_msg_divs_out = [None] * len(div_class_names_out)

    while(ctr < scroll_count):
        ctr += 1
        # not calculate and display this number to speed scraping up?
        visible_msg_div_count = len(driver.find_elements_by_xpath("//div[@class='{}']".format(msg_class_name_common)))

        # print stats
        print('\ttexts scraped so far: {}{}'.format(visible_msg_div_count, \
                progress[progress_index]), end='\r')
        progress_index = 0 if progress_index == 2 else progress_index + 1

        # scroll up and wait
        if(not scroll_up(Keys, driver, body_class_name, lock_class_name)):
            break
        time.sleep(wait_timer)

    # get all the received msgs div content
    for i in range(len(div_class_names_in)):
        all_msg_divs_in[i] = (driver.find_elements_by_xpath("//div[@class='{}']".format(div_class_names_in[i])))
    
    # get all the sent msgs div content
    for i in range(len(div_class_names_out)):
        all_msg_divs_out[i] = (driver.find_elements_by_xpath("//div[@class='{}']".format(div_class_names_out[i])))
    
    # return all the in and out msg divs combined into a single list
    unified_msg_list_in = []
    unified_msg_list_out = []

    for msg_div in all_msg_divs_in:
        unified_msg_list_in.extend(msg_div)

    for msg_div in all_msg_divs_out:
        unified_msg_list_out.extend(msg_div)

    print()
    return unified_msg_list_in, unified_msg_list_out

def scroll_up(Keys, driver, body_class_name, lock_class_name):
    """scroll up if the lock element isn't visible yet and return True, else return False"""
    lock_element = driver.find_elements_by_xpath("//span[@data-testid='{}']".format(lock_class_name))
    driver.find_elements_by_class_name(body_class_name)[0].send_keys(Keys.HOME)

    return len(lock_element) == 0