import mysql.connector
from config import db_config
from scraping import get_soup


# General function to find info in soup
def lookup(bs, t_tag, t_class, ix, attr, sfy):
    """general function to find info in soup
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
                    needle = needle.find(t_tag[i], class_=t_class[i]).contents[ix[i]]
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
            return needle.string if sfy else needle

    print("Erreur de profondeur")
    return False


# Collect info on assets with Morningstar/Quantalys given internal id
def get_info(s_id, s_fund_url, s_code):
    # put results in "info" dictionary
    info = {"code": s_code}
    # retrieve page soup
    soup = get_soup(s_fund_url + s_code)
    # TODO: if an error occurred while requesting page
    # retrieve scraping parameters from table "scraping"
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(buffered=True)
    query = "SELECT * FROM scraping WHERE source_id = %s"
    cursor.execute(query, (s_id,))
    for row in cursor:
        item = row[2]
        info[item] = lookup(soup,
                            [row[3], row[4], row[5]],
                            [row[6], row[7], row[8]],
                            [row[9], row[10], row[11]],
                            [row[12], row[13], row[14]], row[15])
    cursor.close()
    cnx.close()
    return info
