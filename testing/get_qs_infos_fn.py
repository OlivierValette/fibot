from bs4 import BeautifulSoup


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
    return


# read the file back to retrieve saved page
with open("pages/qs.html") as f:
    # use the html parser to parse the url content and store it in a variable
    soup = BeautifulSoup(f, "html.parser")

# NOM DU FONDS ISIN
# <title>Comgest Monde C | FR0000284689</title>
title = soup.title.string.strip()
print(title)

# NAME, ISIN AND RATING
name = lookup(soup, ["div", "h1", "strong"], ["panel-heading", "", ""], ["", "", ""], ["", "", ""], True)
print("Nom : " + name)
ISIN = lookup(soup, ["div", "h1", "small"], ["panel-heading", "", ""], ["", "", ""], ["", "", ""], True)
print("ISIN : " + ISIN)
rating = lookup(soup, ["div", "div"], ["panel-heading", "spritefonds"], ["", 1], ["", "class"], False)
print("Rating : " + rating)

# VALEUR LIQUIDATIVE ET DATE
updated = lookup(soup,
                 ["div", "span"],
                 ["panel-body", "vl-box-date"],
                 ["", ""],
                 ["", ""],
                 True)
updated = updated.strip()
print("Updated on : " + updated)

value = lookup(
    soup,
    ["div", "span"],
    ["panel-body", "vl-box-value"],
    ["", ""],
    ["", ""],
    True
)
value = value.strip()
print("Valeur liq. : " + value)

cvalue = value[value.find('E'):]
lvalue = value[:value.find('E')-2]
print("Valeur liq. : " + lvalue)
print("Devise : " + cvalue)

# BENCHMARK
benchmark = lookup(
    soup,
    ["dl", "dd"],
    ["dl-fichier-identite", ""],
    ["", 4],
    ["", ""],
    True
)
print("Benchmark : " + benchmark)

# CATEGORIE QS
category = lookup(
    soup,
    ["dl", "dd", "a"],
    ["dl-fichier-identite", "", ""],
    ["", 5, 0],
    ["", "", "contents"],
    False
)
print("Catégorie : " + category)

catcode = soup.find(id="id-cat")['value']
print("Code catégorie MS : " + catcode)

# PERFORMANCES ANNUELLES DU FONDS
updated = lookup(
    soup,
    ["table", "td", "strong"],
    ["", "", ""],
    [0, 0, ""],
    ["", "", ""],
    True
)
updated = updated.strip()
updated = updated[updated.find(' ')+1:]
print("Updated on : " + updated)

performance = []
# YTD performance
performance.append(lookup(soup, ["table", "td"], ["", ""], [0, 10], ["", ""], True))
# Past years performances
performance.append(lookup(soup, ["table", "td"], ["", ""], [0, 29], ["", ""], True))
performance.append(lookup(soup, ["table", "td"], ["", ""], [0, 32], ["", ""], True))
performance.append(lookup(soup, ["table", "td"], ["", ""], [0, 35], ["", ""], True))
print('Performances :', performance)
