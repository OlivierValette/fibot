from bs4 import BeautifulSoup
import re


# general function to find info in soup
def get_ms(bs, t_tag, t_class, ix, attr, sfy):
    p = len(t_tag)
    print(p)
    needle = bs
    for i in range(0, 2):
        # level i
        needle = needle.find(t_tag[i], class_=t_class[i])
        print("===============>", attr[i] if attr[i] else "null", ix[i])
        if attr[i] != "":
            needle = needle[attr[i]]
        if ix[i] != "":
            needle = needle[ix[i]]
        print(needle)
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
name = get_ms(soup, ["div", "h1"], ["snapshotTitleBox", ""], ["", ""], ["", ""], True)
print("Nom : " + name)

rating = get_ms(soup, ["span"], ["rating_sprite"], [1], ["class"], False)
print("Rating : " + rating)

# PERFORMANCES ANNUELLES DU FONDS
# 1) Date de référence
# <table class="snapshotTextColor snapshotTextFontStyle snapshotTable overviewPerformanceTable" border="0">
#     <tr>
#        <td class="titleBarHeading">Performance du fonds</td>
#        <td class="titleBarNote">28/02/2019</td>
updated = get_ms(soup, ["table","td"], ["overviewPerformanceTable", "titleBarNote"], ["", ""], ["", ""], True)
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
performance.append(get_ms(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col7"], ["", ""], ["", ""], True))
performance.append(get_ms(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col6"], ["", ""], ["", ""], True))
performance.append(get_ms(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col5"], ["", ""], ["", ""], True))
performance.append(get_ms(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col4"], ["", ""], ["", ""], True))
performance.append(get_ms(soup, ["table", "td"], ["overviewCalenderYearReturnsTable", "col3"], ["", ""], ["", ""], True))
print(performance)

# BENCHMARK
#           <td colspan="7" class="footer">
#               <span class="label">Benchmark:</span>
#               <span class="value" title="MSCI World Growth NR USD">MSCI World Growth NR USD</span>
#           </td>
benchmark = get_ms(soup,
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
target_tag = "table"
target_class = "overviewKeyStatsTable"
index = ""
sub_target_tag = "td"
sub_target_class = "line heading"
sub_index = 0
sub2_target_tag = "span"
sub2_target_class = "heading"
sub2_index = 1
output = "contents"
updated = soup.find(target_tag, class_=target_class).find(
    sub_target_tag, class_=sub_target_class).find(
    sub2_target_tag, class_=sub2_target_class).contents[sub2_index]
print("Date : " + updated)

sub_target_class = "line text"
sub2_target_tag = ""
sub2_target_class = ""
output = "string"
value = soup.find(target_tag, class_=target_class).find(sub_target_tag, class_=sub_target_class).string
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
target_tag = "table"
target_class = "overviewKeyStatsTable"
index = ""
sub_target_tag = "td"
sub_target_class = "line value text"
sub_index = 0
sub2_target_tag = "a"
sub2_target_class = ""
sub2_index = 1
output = "string"
category = soup.find(target_tag, class_=target_class).find(
    sub_target_tag, class_=sub_target_class).find(
    sub2_target_tag).string.strip()
# Special use of regex to clean special characters
category = re.sub('\W+', ' ', category)
print("Catégorie : " + category)

output = "href"
catcode = soup.find(target_tag, class_=target_class).find(
    sub_target_tag, class_=sub_target_class).find(
    sub2_target_tag)[output]
catcode = catcode[catcode.find("=")+1:]
print("Code catégorie MS : " + catcode)

# ISIN
#                  <tr><td class="line heading">ISIN</td>
#                      <td class="line"> </td>
#                      <td class="line text">FR0000284689</td>
#                  </tr>
target_tag = "table"
target_class = "overviewKeyStatsTable"
index = ""
sub_target_tag = "td"
sub_target_class = "line text"
sub_index = 2
sub2_target_tag = ""
sub2_target_class = ""
sub2_index = ""
output = "string"
ISIN = soup.find(target_tag, class_=target_class).find_all(sub_target_tag, class_=sub_target_class)[2].string
print("Isin : " + ISIN)
ISIN = get_ms(soup, 2, target_tag, target_class, index, sub_target_tag, sub_target_class, 2, "string")
print("Isin : " + ISIN)
