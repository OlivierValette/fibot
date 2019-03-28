from bs4 import BeautifulSoup
import re

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
target_tag = "div"
target_class = "snapshotTitleBox"
index = ""
sub_target_tag = "h1"
sub_target_class = ""
sub_index = ""
output = "string"
name = soup.find(target_tag, class_=target_class).find(sub_target_tag).string

target_tag = "span"
target_class = "rating_sprite"
index = ""
sub_target_tag = ""
sub_target_class = ""
sub_index = 1
output = "class"
rating = soup.find(target_tag, class_=target_class)[output][sub_index]
print(name)
print(rating)

# PERFORMANCES ANNUELLES DU FONDS
# 1) Date de référence
# <table class="snapshotTextColor snapshotTextFontStyle snapshotTable overviewPerformanceTable" border="0">
#     <tr>
#        <td class="titleBarHeading">Performance du fonds</td>
#        <td class="titleBarNote">28/02/2019</td>
target_tag = "table"
target_class = "overviewPerformanceTable"
index = ""
sub_target_tag = "td"
sub_target_class = "titleBarNote"
sub_index = ""
output = "string"
updated = soup.find(target_tag, class_=target_class).find(sub_target_tag, class_=sub_target_class).string
print(updated)

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
target_tag = "table"
target_class = "overviewCalenderYearReturnsTable"
index = ""
sub_target_tag = "td"
sub_index = ""
output = "string"
performance = []
sub_target_class = "col7"
performance.append(soup.find(target_tag, class_=target_class).find(sub_target_tag, class_=sub_target_class).string)
sub_target_class = "col6"
performance.append(soup.find(target_tag, class_=target_class).find(sub_target_tag, class_=sub_target_class).string)
sub_target_class = "col5"
performance.append(soup.find(target_tag, class_=target_class).find(sub_target_tag, class_=sub_target_class).string)
sub_target_class = "col4"
performance.append(soup.find(target_tag, class_=target_class).find(sub_target_tag, class_=sub_target_class).string)
sub_target_class = "col3"
performance.append(soup.find(target_tag, class_=target_class).find(sub_target_tag, class_=sub_target_class).string)
print(performance)

# BENCHMARK
#           <td colspan="7" class="footer">
#               <span class="label">Benchmark:</span>
#               <span class="value" title="MSCI World Growth NR USD">MSCI World Growth NR USD</span>
#           </td>
target_tag = "table"
target_class = "overviewCalenderYearReturnsTable"
index = ""
sub_target_tag = "td"
sub_target_class = "footer"
sub_index = 0
sub2_target_tag = "span"
sub2_target_class = "value"
sub2_index = 0
output = "string"
category = soup.find(target_tag, class_=target_class).find_all(
    sub_target_tag, class_=sub_target_class)[sub_index].find(
    sub2_target_tag, class_=sub2_target_class).string
print("Catégorie : " + category)
sub_index = 1
benchmark = soup.find(target_tag, class_=target_class).find_all(
    sub_target_tag, class_=sub_target_class)[sub_index].find(
    sub2_target_tag, class_=sub2_target_class).string
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
sub2_target_tag = "a"
sub2_target_class = ""
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