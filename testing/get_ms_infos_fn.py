from bs4 import BeautifulSoup
import re


def lookup(bs, t_tag, t_class, ix, attr, sfy):
    """general function to find MS info in soup

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
    return


# read the file back to retrieve saved page
with open("pages/ms.html") as f:
    # use the html parser to parse the url content and store it in a variable
    soup = BeautifulSoup(f, "html.parser")

# NOM DU FONDS ISIN
# <title>Comgest Monde C | FR0000284689</title>
title = soup.title.string.strip()
print(title)

# NAME AND RATING
# <div class="snapshotTitleBox">
#    <h1>Comgest Monde C</h1><span class="rating_sprite stars4"></span>
name = lookup(soup, ["div", "h1"], ["snapshotTitleBox", ""], ["", ""], ["", ""], True)
print("Nom : " + name)

rating = lookup(soup, ["span"], ["rating_sprite"], [1], ["class"], False)
print("Rating : " + rating)

# PERFORMANCES ANNUELLES DU FONDS
# 1) Date de référence
# <table class="snapshotTextColor snapshotTextFontStyle snapshotTable overviewPerformanceTable" border="0">
#     <tr>
#        <td class="titleBarHeading">Performance du fonds</td>
#        <td class="titleBarNote">28/02/2019</td>
updated = lookup(soup,
                 ["table", "td"],
                 ["overviewPerformanceTable", "titleBarNote"],
                 ["", ""],
                 ["", ""],
                 True)
print("Updated on : " + updated)

# 2) Valeurs annuelles
# <div id="overviewCalenderYearReturnsDiv">
#     <table class="snapshotTextColor snapshotTextFontStyle snapshotTable overviewCalenderYearReturnsTable" border="0">
#         <tr>
#           <td class="col1">
#              <img src="/includes/images/iconListSmall.gif" class="iconList" style="background-color:#CE0000" alt="">
#              </img>
#            </td>
#           <td class="col2 label">Fonds</td>
#           <td class="col3 value number">11,8</td>   2015   A-4
#           <td class="col4 value number">3,1</td>    2016   A-3
#           <td class="col5 value number">19,4</td>   2017   A-2
#           <td class="col6 value number">3,9</td>    2018   A-1
#           <td class="col7 value number">8,2</td>    2019   A
performance = []
performance.append(lookup(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col7"], ["", ""], ["", ""], True))
performance.append(lookup(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col6"], ["", ""], ["", ""], True))
performance.append(lookup(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col5"], ["", ""], ["", ""], True))
performance.append(lookup(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col4"], ["", ""], ["", ""], True))
performance.append(lookup(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col3"], ["", ""], ["", ""], True))
print(performance)

# BENCHMARK
#           <td colspan="7" class="footer"> --- second one!
#               <span class="label">Benchmark:</span>
#               <span class="value" title="MSCI World Growth NR USD">MSCI World Growth NR USD</span>
#           </td>
benchmark = lookup(soup,
                   ["table", "td", "span"],
                   ["overviewCalenderYearReturnsTable", "footer", "value"],
                   ["", 1, ""],
                   ["", "", ""],
                   True)
print("Benchmark : " + benchmark)

# VALEUR LIQUIDATIVE ET DATE
# <div id="overviewQuickstatsBenchmarkDiv">
#     <div id="overviewQuickstatsDiv" xmlns:funs="funs" xmlns:rtxo="urn:RTExtensionObj" xmlns:erto="urn:ETRObj">
#         <table class="snapshotTextColor snapshotTextFontStyle snapshotTable overviewKeyStatsTable" border="0">
#              <tr><td class="titleBarHeading" colspan="3">Vue d’Ensemble</td></tr>
#              <tr><td class="line heading">VL<span class="heading"><br/>25/03/2019</span></td>
#                  <td class="line"> </td>
#                  <td class="line text">EUR 2023,71</td>
output = "contents"
updated = lookup(soup,
                 ["table", "td", "span"],
                 ["overviewKeyStatsTable", "line heading", "heading"],
                 ["", 0, 1],
                 ["", "", "contents"],
                 False)
print("Date : " + updated)

value = lookup(soup,
               ["table", "td"],
               ["overviewKeyStatsTable", "line text"],
               ["", ""],
               ["", ""],
               True)
lvalue = value[value.find(u'\xa0')+1:]
cvalue = value[:value.find(u'\xa0')-1]
print("Valeur liq. : " + lvalue)
print("Devise : " + cvalue)

# CATEGORIE MS
#              <tr><td class="line heading">Catégorie Morningstar</td>
#                  <td class="line"> </td>
#                  <td class="line value text">
#                      <a href="/fr/fundquickrank/default.aspx?category=EUCA000556" style="width:100%!important;">
#                           Actions Internationales Gdes Cap. Croissance</a>
#                  </td></tr>
category = lookup(soup,
                  ["table", "td", "a"],
                  ["overviewKeyStatsTable", "line value text", ""],
                  ["", "", ""],
                  ["", "", ""],
                  True)
category = category.strip()
# Special use of regex to clean special characters
category = re.sub('\W+', ' ', category)
print("Catégorie : " + category)

output = "href"
catcode = lookup(soup,
                 ["table", "td", "a"],
                 ["overviewKeyStatsTable", "line value text", ""],
                 ["", 0, 1],
                 ["", "", "href"],
                 False)
catcode = catcode[catcode.find("=")+1:]
print("Code catégorie MS : " + catcode)

# ISIN
#                  <tr><td class="line heading">ISIN</td>
#                      <td class="line"> </td>
#                      <td class="line text">FR0000284689</td>
#                  </tr>
ISIN = lookup(soup,
              ["table", "td"],
              ["overviewKeyStatsTable", "line text"],
              ["", 2],
              ["", ""],
              True)
print("Isin : " + ISIN)
