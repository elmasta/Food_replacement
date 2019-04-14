# -*- coding: Utf-8 -*

import json
import requests
import mysql.connector

CATEGORIES = ["pizzas", "non-alcoholic-beverages", "ravioli", "sweet-spreads",
              "cheeses", "frozen-ready-made-meals", "yogurts", "sweet-snacks",
              "salty-snacks"]
STORE_LIST = ["PICARD", "CARREFOUR", "CASINO", "CORA", "LECLERC",
              "MAGASINS U", "FRANPRIX", "LEADER PRICE", "LIDL", "MONOPRIX",
              "DELHAIZE", "INTERMARCHÉ", "AUCHAN", "LA VIE CLAIRE",
              "SIMPLY MARKET"]
PRODUCT_NO = 1

# connection to mysql
MYDB = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd=input("Enter the mysql root password and press enter: ")
)
CURSORDB = MYDB.cursor()

# database and tables creation
CURSORDB.execute("CREATE DATABASE food_replacement CHARACTER SET 'utf8'")
CURSORDB.execute("USE food_replacement")
CURSORDB.execute("""CREATE TABLE Product (id INT UNSIGNED AUTO_INCREMENT,
                 product_name VARCHAR(200) NOT NULL,
                 nutrition_grades CHAR(1) NOT NULL, ingredients TEXT NOT NULL,
                 url VARCHAR(200) NOT NULL,
                 PRIMARY KEY(id)) ENGINE=InnoDB""")
CURSORDB.execute("""CREATE TABLE Store (id INT UNSIGNED AUTO_INCREMENT,
                 store_name VARCHAR(200) NOT NULL, PRIMARY KEY(id))
                 ENGINE=InnoDB""")
CURSORDB.execute("""CREATE TABLE Research_history
                 (id INT UNSIGNED AUTO_INCREMENT,
                 product_researched_name VARCHAR(200),
                 product_id_replaced INT UNSIGNED,
                 store_id_replaced INT UNSIGNED, PRIMARY KEY(id))
                 ENGINE=InnoDB""")
CURSORDB.execute("""CREATE TABLE Store_availability (product_id INT UNSIGNED,
                 store_id INT UNSIGNED, PRIMARY KEY(product_id, store_id))
                 ENGINE=InnoDB""")
CURSORDB.execute("""CREATE TABLE Category (id INT UNSIGNED AUTO_INCREMENT,
                 category_name VARCHAR(80), PRIMARY KEY(id)) ENGINE=InnoDB""")
CURSORDB.execute("""CREATE TABLE Product_category (product_id INT UNSIGNED,
                 category_id INT UNSIGNED,
                 PRIMARY KEY(product_id, category_id)) ENGINE=InnoDB""")

for each_store in STORE_LIST:
    sql = "INSERT INTO Store (store_name) VALUES (%s)"
    val = (each_store,)
    CURSORDB.execute(sql, val)

# Data import from open food fact.
for each_categories in CATEGORIES:
    sql = "INSERT INTO Category (category_name) VALUES (%s)"
    val = (each_categories,)
    CURSORDB.execute(sql, val)
    MYDB.commit()
    # We select the first 60 product pages from each categories.
    for category_page in range(60):
        category_page_str = str(category_page)
        url = "https://fr-en.openfoodfacts.org/category/" + each_categories +\
              "/" + category_page_str + ".json"
        response = requests.get(url)
        found = json.loads(response.text)
        product_comp = found["products"]
        # We scan each product on a page
        for each_product in product_comp:
            try:
                # We check if each product is: French, has at least one
                # store, has the ingredients and a bare code. if
                # something is missing, we go to the next.
                if each_product["countries_tags"].count("en:france") >= 1 and\
                   each_product["stores"] != "" and\
                   each_product["ingredients_text_fr"] != "" and\
                   each_product["id"] != "" and\
                   each_product["nutrition_grades"] != "" and\
                   each_product["url"] != "":
                    store_counter = 0
                    store_upper = each_product["stores"].upper()
                    current_store_list = store_upper.split(",")
                    for each_store in current_store_list:
                        # Now we check if at least one store is in our
                        # store list.
                        each_store = each_store.strip()
                        if each_store in STORE_LIST:
                            store_counter += 1
                            try:
                                sql = """INSERT INTO Store_availability
                                      (product_id, store_id) VALUES (%s, %s)
                                      """
                                val = (PRODUCT_NO,
                                       STORE_LIST.index(each_store) + 1)
                                CURSORDB.execute(sql, val)
                                MYDB.commit()
                            except mysql.connector.Error as err:
                                print(err)
                    # We check if there was at least on correct store
                    # for that product.
                    if store_counter != 0:
                        clean_product_name =\
                        each_product["product_name"].replace("\\n", " ")
                        clean_product_name =\
                        clean_product_name.replace("\\r", " ")
                        clean_ingredient =\
                        each_product["ingredients_text_fr"].replace(
                            "\\n", " ")
                        clean_ingredient =\
                        clean_ingredient.replace("\\r", " ")
                        sql = """INSERT INTO Product (product_name,
                              nutrition_grades, ingredients, url)
                              VALUES (%s, %s, %s, %s)"""
                        val = (clean_product_name,
                               each_product["nutrition_grades"],
                               clean_ingredient, each_product["url"])
                        CURSORDB.execute(sql, val)
                        MYDB.commit()
                        sql = """INSERT INTO Product_category
                              (product_id, category_id) VALUES (%s, %s)"""
                        val = (PRODUCT_NO,
                               CATEGORIES.index(each_categories) + 1)
                        CURSORDB.execute(sql, val)
                        MYDB.commit()
                        PRODUCT_NO += 1
            except KeyError:
                print("No French ingredients list, nutrition grade or ID")
