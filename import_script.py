# -*- coding: Utf-8 -*

import json
import requests
import mysql.connector

categories = ["pizzas", "non-alcoholic-beverages", "alcoholic-beverages", "ravioli", "sweet-spreads", "cheeses", "frozen-ready-made-meals"]
store_list = []
product_no = 0

#connection to mysql
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd=input("Enter the mysql root password and press enter: ")
)
cursordb = mydb.cursor()

#database and tables creation
try:
    cursordb.execute("CREATE DATABASE food_replacement CHARACTER SET 'utf8'")
except:
    print("DATABASE already existe")
cursordb.execute("USE food_replacement")
try:
    cursordb.execute("CREATE TABLE Product (id INT UNSIGNED AUTO_INCREMENT, product_name VARCHAR(200), nutrition_grades CHAR(1), ingredients TEXT, PRIMARY KEY(id)) ENGINE=InnoDB")
    cursordb.execute("CREATE TABLE Store (id INT UNSIGNED AUTO_INCREMENT, store_name VARCHAR(200), PRIMARY KEY(id)) ENGINE=InnoDB")
    cursordb.execute("CREATE TABLE Research_history (id INT UNSIGNED AUTO_INCREMENT, product_id_researched INT UNSIGNED, product_id_replaced INT UNSIGNED, PRIMARY KEY(id)) ENGINE=InnoDB")
    cursordb.execute("CREATE TABLE Store_availability (product_id INT UNSIGNED, store_id INT UNSIGNED, PRIMARY KEY(product_id, store_id)) ENGINE=InnoDB")
except:
    print("TABLES already existe")

#data import from open food fact script
for each_categories in categories:
    category_page = 1
    while category_page != 21:
        category_page_str = str(category_page)
        url = "https://fr-en.openfoodfacts.org/category/" + each_categories + "/" + category_page_str + ".json"
        response = requests.get(url)
        found = json.loads(response.text)
        product_comp = found["products"]
        for each_product in product_comp:
            try:
                for countries in each_product["countries_tags"]:
                    if countries == "en:france" and each_product["stores"] != "" and each_product["ingredients_text_fr"] != "":
                        sql = "INSERT INTO Product (product_name, nutrition_grades, ingredients) VALUES (%s, %s, %s)"
                        val = (each_product["product_name"], each_product["nutrition_grades"], each_product["ingredients_text_fr"])
                        cursordb.execute(sql, val)
                        mydb.commit()
                        product_no += 1
                        store_upper = each_product["stores"].upper()
                        current_store_list = store_upper.split(",")
                        for each_store in current_store_list:
                            each_store = each_store.strip()
                            if each_store not in store_list:
                                store_list.append(each_store)
                                sql = "INSERT INTO Store (store_name) VALUES (%s)"
                                val = (each_store,)
                                cursordb.execute(sql, val)
                            store_no = store_list.index(each_store) + 1
                            sql = "INSERT INTO Store_availability (product_id, store_id) VALUES (%s, %s)"
                            val = (product_no, store_no)
                            cursordb.execute(sql, val)
                            mydb.commit()
                        break
                    else:
                        print("missing infos")
            except KeyError:
                print("no ingredients")
        category_page += 1
