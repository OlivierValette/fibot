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
name = title[:title.find('|')]
isin = title[title.find('|')+1:]
print(name)
print(isin)

# RATING
# <div class="snapshotTitleBox">
#    <h1>Comgest Monde C</h1><span class="rating_sprite stars4"></span>
target_class = "snapshotTitleBox"
name = soup.find("div", class_=target_class).find("h1").string
target_class = "rating_sprite"
rating = soup.find("span", class_=target_class)['class'][1]
print(name)
print(rating)

# PERFORMANCES ANNUELLES DU FONDS
# 1) Date de référence
# <table class="snapshotTextColor snapshotTextFontStyle snapshotTable overviewPerformanceTable" border="0">
#     <tr>
#        <td class="titleBarHeading">Performance du fonds</td>
#        <td class="titleBarNote">28/02/2019</td>
target_class = "overviewPerformanceTable"
updated = soup.find("table", class_=target_class).find("td", class_="titleBarNote").string
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
target_class = "overviewCalenderYearReturnsTable"
performance = []
for i in range(7, 3, -1):
    subClassToFind = 'col' + str(i)
    performance.append(soup.find("table", class_=target_class).find("td", class_=subClassToFind).string)
print(performance)

# BENCHMARK
#           <td colspan="7" class="footer">
#               <span class="label">Benchmark:</span>
#               <span class="value" title="MSCI World Growth NR USD">MSCI World Growth NR USD</span>
#           </td>
target_class = "overviewCalenderYearReturnsTable"
category = soup.find("table", class_=target_class).find_all("td", class_="footer")[0].find("span", class_="value").string
benchmark = soup.find("table", class_=target_class).find_all("td", class_="footer")[1].find("span", class_="value").string
print("Catégorie : " + category)
print("Benchmark : " + benchmark)

# VALEUR LIQUIDATIVE ET DATE
# <div id="overviewQuickstatsBenchmarkDiv">
#     <div id="overviewQuickstatsDiv" xmlns:funs="funs" xmlns:rtxo="urn:RTExtensionObj" xmlns:erto="urn:ETRObj">
#         <table class="snapshotTextColor snapshotTextFontStyle snapshotTable overviewKeyStatsTable" border="0">
#              <tr><td class="titleBarHeading" colspan="3">Vue d’Ensemble</td></tr>
#              <tr><td class="line heading">VL<span class="heading"><br/>25/03/2019</span></td>
#                  <td class="line"> </td>
#                  <td class="line text">EUR 2023,71</td>
target_class = "overviewKeyStatsTable"
updated = soup.find("table", class_=target_class).find("td", class_="line heading").find("span", class_="heading").contents[1]
value = soup.find("table", class_=target_class).find("td", class_="line text").string
lvalue = value[value.find(u'\xa0')+1:]
cvalue = value[:value.find(u'\xa0')-1]
print("Date : " + updated)
print("Devise : " + cvalue)
print("Valeur liq. : " + lvalue)

# CATEGORIE MS
#              <tr><td class="line heading">Catégorie Morningstar</td>
#                  <td class="line"> </td>
#                  <td class="line value text">
#                      <a href="/fr/fundquickrank/default.aspx?category=EUCA000556" style="width:100%!important;">
#                           Actions Internationales Gdes Cap. Croissance</a>
#                  </td></tr>
target_class = "overviewKeyStatsTable"
category = soup.find("table", class_=target_class).find("td", class_="line value text").find("a").string.strip()
# Special use of regex to clean special characters
category = re.sub('\W+', ' ', category)
catcode = soup.find("table", class_=target_class).find("td", class_="line value text").find("a")['href']
catcode = catcode[catcode.find("=")+1:]
print("Catégorie : " + category)
print("Code catégorie MS : " + catcode)

# ISIN
#                  <tr><td class="line heading">ISIN</td>
#                      <td class="line"> </td>
#                      <td class="line text">FR0000284689</td>
#                  </tr>
target_class = "overviewKeyStatsTable"
ISIN = soup.find("table", class_=target_class).find_all("td", class_="line text")[2].string
print("Isin : " + ISIN)