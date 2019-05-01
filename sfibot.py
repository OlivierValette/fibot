# -*- coding: utf-8 -*-

import mysql.connector
from config import db_config
from scraping import get_soup
from bs4 import BeautifulSoup, NavigableString


# General function to find info in soup
def lookup(bs, t_tag, t_class, ix, attr, sfy):
    """general function to find info in soup
    :type bs: BeautifulSoup
    :param bs: soup
    Search parameters in arrays (one to three values according to depth)
    :param t_tag: target tag
    :param t_class: target class
    :param ix: target index
    :param attr: target attribute or content
    :param sfy: stringify (boolean)
    :return: seeked value
    """

    p = len(t_tag)
    needle = bs

    for i in range(0, 3):
        if ix[i] != "":
            if attr[i] == "":
                if t_class[i] == "":
                    needle = needle.find_all(t_tag[i])[ix[i]]
                else:
                    needle = needle.find_all(t_tag[i], class_=t_class[i])[ix[i]]
            else:
                if attr[i] == "contents":
                    if t_class[i] == "":
                        needle = needle.find_all(t_tag[i])[ix[i]].contents
                    else:
                        needle = needle.find_all(t_tag[i], class_=t_class[i])[ix[i]].contents
                else:
                    needle = needle.find(t_tag[i], class_=t_class[i])[attr[i]][ix[i]]
        else:
            needle = needle.find(t_tag[i], class_=t_class[i])
            if attr[i] != "":
                if attr[i] == "contents":
                    needle = needle.contents
                else:
                    needle = needle[attr[i]]
        if i == p - 1:
            if sfy:
                needle = needle.string
            print(type(needle))
            needle = str(needle).strip()
            return needle

    print("Erreur de profondeur")
    return False


# Collect info on assets with Morningstar/Quantalys given internal id
def get_info(s_id, s_fund_url, s_code):
    # put results in "info" dictionary
    info = {"code": s_code}
    # retrieve page soup
    soup = get_soup(s_fund_url + s_code, 5)
    if not soup:
        print('???:', soup)
    else:
        # retrieve scraping parameters from table "scraping"
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(buffered=True)
        query = "SELECT * FROM scraping WHERE source_id = %s"
        cursor.execute(query, (s_id,))
        for row in cursor:
            item = row[2]
            # retrieving parameters according to depth of search in soup
            if row[5]:
                p_tag = [row[3], row[4], row[5]]
                p_class = [row[6] or '', row[7] or '', row[8] or '']
                p_index = ['' if row[9] is None else row[9], '' if row[10] is None else row[10], '' if row[11] is None else row[11]]
                p_attr = [row[12] or '', row[13] or '', row[14] or '']
            elif row[4]:
                p_tag = [row[3], row[4]]
                p_class = [row[6] or '', row[7] or '']
                p_index = ['' if row[9] is None else row[9], '' if row[10] is None else row[10]]
                p_attr = [row[12] or '', row[13] or '']
            else:
                p_tag = [row[3]]
                p_class = [row[6] or '']
                p_index = ['' if row[9] is None else row[9]]
                p_attr = [row[12] or '']
            p_sfy = row[15]
            print('item:', item)
            print('calling lookup:', p_tag, p_class, p_index, p_attr, p_sfy)
            result = lookup(soup, p_tag, p_class, p_index, p_attr, p_sfy)
            print('result:', result)
            if row[16]:
                print(row[16])
                texte = row[16].replace('x', 'result')
                print(texte)
                result = eval(texte)
            print('result:', result)
            info[item] = result
        cursor.close()
        cnx.close()
    return info
