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
    soup = get_soup(s_fund_url + s_code, 15)
    if not soup:
        print("Problème d'accès au site", s_fund_url)
    else:
        # retrieve scraping parameters from table "scraping"
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(buffered=True, dictionary=True)
        query = "SELECT * FROM scraping WHERE source_id = %s"
        cursor.execute(query, (s_id,))
        for row in cursor:
            item = row['item']
            # retrieving parameters according to depth of search in soup
            if row['tag2']:
                p_tag = [row['tag0'], row['tag1'], row['tag2']]
                p_class = [row['class0'] or '', row['class1'] or '', row['class2'] or '']
                p_index = ['' if row['index0'] is None else row['index0'], '' if row['index1'] is None else row['index1'], '' if row['index2'] is None else row['index2']]
                p_attr = [row['attr0'] or '', row['attr1'] or '', row['attr2'] or '']
            elif row['tag1']:
                p_tag = [row['tag0'], row['tag1']]
                p_class = [row['class0'] or '', row['class1'] or '']
                p_index = ['' if row['index0'] is None else row['index0'], '' if row['index1'] is None else row['index1']]
                p_attr = [row['attr0'] or '', row['attr1'] or '']
            else:
                p_tag = [row['tag0']]
                p_class = [row['class0'] or '']
                p_index = ['' if row['index0'] is None else row['index0']]
                p_attr = [row['attr0'] or '']
            p_sfy = row['stringify']
            print('item:', item)
            print('calling lookup:', p_tag, p_class, p_index, p_attr, p_sfy)
            x = lookup(soup, p_tag, p_class, p_index, p_attr, p_sfy)
            print('result:', x)
            # string additional manipulations
            # result var must be 'x' as in moreover column
            if row['moreover']:
                print(row['moreover'])
                texte = row['moreover'].strip()
                print(texte)
                x = eval(texte)
            print('result:', x)
            info[item] = x
        cursor.close()
        cnx.close()
    return info
