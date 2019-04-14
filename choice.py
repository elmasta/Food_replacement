from display import cat_selection_screen, store_screen, replacement_method
import mysql.connector


class SqlInit:
    """This class is used to connect the user to the database"""

    def __init__(self):
        self.mydb = ""
        self.cursordb = ""

    def db_conection(self):
        """This methode is used to connect the user to the database"""
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd=input("Enter the mysql root password and press enter: ")
        )
        self.cursordb = self.mydb.cursor()
        self.cursordb.execute("USE food_replacement")


class UserChoice:
    """This class is used to consult the database and to replace a
    product by another."""

    def __init__(self):
        self.category_selected = 0
        self.store_selected = 0
        self.selec_prod = ()
        self.product_found = False
        self.quit_err = 0
        self.name = ""
        self.selection = 0

    def category_choice(self):
        """This methode is used to select a category"""
        cat_selection_screen()
        selection = input("Votre sélection: ")
        if selection.isalpha() is True or int(selection) < 1 or\
           int(selection) > 9:
            print("Erreur à la saisi.")
            self.quit_err = 1
        else:
            self.category_selected = int(selection)
            self.quit_err = 0

    def db_consult(self, cursor):
        """This methode is used if the user want to consult the
        database"""
        cursor.execute("""SELECT Product.product_name,
                       Product.nutrition_grades, Product.ingredients
                       From Product LEFT JOIN Product_category ON
                       Product_category.product_id = Product.id WHERE
                       Product_category.category_id = %s ORDER BY
                       Product.product_name""",
                       (self.category_selected,))
        for row in cursor:
            print("""{0} a pour grade nutritionnel la note de {1} et a pour
ingrédient:\n{2}\n""".format(row[0], row[1], row[2]))

    def replacement_consult(self, cursor):
        """This methode is used if the user want to consult the last
        ten changes made"""
        print("Voici l'historique des remplacements:")
        cursor.execute("""SELECT Research_history.product_researched_name,
                       Product.product_name, Store.store_name,
                       Product.ingredients
                       FROM Product
                       LEFT JOIN Research_history
                       ON Product.id = Research_history.product_id_replaced
                       LEFT JOIN Store
                       ON Research_history.store_id_replaced = Store.id
                       WHERE Research_history.product_researched_name
                       IS NOT NULL
                       ORDER BY Research_history.id DESC""")
        for row in cursor:
            print("""
\n{0} a été remplacé par {1} que vous trouverez chez {2} et qui contient:\n{3}
""".format(row[0], row[1], row[2], row[3]))

    def store_selection(self):
        """This methode let the user select a store"""
        store_screen()
        selection = input("Votre sélection: ")
        if selection.isalpha() is True or int(selection) < 1 or\
           int(selection) > 15:
            print("Erreur à la saisi.")
            self.quit_err = 1
        else:
            self.store_selected = int(selection)
            self.quit_err = 0

    def replacement_method_choice(self):
        """This methode is used to make the user choose his method
        of food swap"""
        replacement_method()
        user_choice = 0
        while user_choice != 1:
            self.selection = input("Votre sélection: ")
            if self.selection.isalpha() is True or int(self.selection) < 1 or\
               int(self.selection) > 2:
                print("Erreur à la saisi.")
            else:
                user_choice = 1

    def list_replacement(self, cursor):
        """This methode is used if the user want to select a product
        from a list"""
        sql = ("""SELECT Product.id, Product.product_name FROM Product
               INNER JOIN Store_availability
               ON Product.id = Store_availability.product_id
               INNER JOIN Product_category
               ON Product.id = Product_category.product_id
               WHERE Store_availability.store_id = %s
               AND Product_category.category_id = %s
               ORDER BY RAND() LIMIT 10""")
        val = (self.store_selected, self.category_selected)
        cursor.execute(sql, val)
        print("Faites un choix parmis les 10 produits proposé:")
        prod_list = []
        prod_list_found = 0
        prod_count = 1
        for row in cursor:
            prod_list_found = 1
            prod_list.append(row[0])
            print(prod_count, ". ", row[1])
            prod_count += 1
        if prod_list_found != 0:
            user_choice = 0
            while user_choice != 1:
                product_choice = input("""
Choissisez un chiffre et appuyez sur "entrée" pour valider votre sélection.: 
""")
                if product_choice.isalpha() is True or\
                   int(product_choice) < 1 or int(product_choice) > 10:
                    print("Erreur à la saisi.")
                else:
                    user_choice = 1
                    sql = ("""SELECT Product.product_name FROM Product
                           WHERE Product.id = %s""")
                    val = (prod_list[int(product_choice) - 1],)
                    cursor.execute(sql, val)
                    for row in cursor:
                        self.name = row[0]
                answer_ing = input("""
Souhaitez vous la liste des ingrédients du produit qui sera le remplaçant?
y pour confirmer 
""")
            if answer_ing not in ("y", "Y"):
                sql = ("""SELECT Product.product_name, product.url
                       FROM Product
                       INNER JOIN Store_availability
                       ON Product.id = Store_availability.product_id
                       INNER JOIN Product_category
                       ON Product.id = Product_category.product_id
                       WHERE Store_availability.store_id = %s
                       AND Product_category.category_id = %s
                       ORDER BY Product.nutrition_grades LIMIT 1""")
                val = (self.store_selected, self.category_selected)
                cursor.execute(sql, val)
                for row in cursor:
                    self.product_found = True
                    print("Nous vous avons sélectionné ceci:")
                    self.selec_prod = row[0]
                    print("la ou le {0} (plus d'info ici: {1})".format(
                        row[0], row[1]))
            else:
                sql = ("""SELECT Product.product_name, Product.ingredients,
                       product.url FROM Product
                       INNER JOIN Store_availability
                       ON Product.id = Store_availability.product_id
                       INNER JOIN Product_category
                       ON Product.id = Product_category.product_id
                       WHERE Store_availability.store_id = %s
                       AND Product_category.category_id = %s
                       ORDER BY Product.nutrition_grades LIMIT 1""")
                val = (self.store_selected, self.category_selected)
                cursor.execute(sql, val)
                for row in cursor:
                    self.product_found = True
                    print("Nous vous avons sélectionné ceci:")
                    self.selec_prod = row[0]
                    print("""
la ou le {0} qui contient:\n{1}\n Plus d'info ici: {2}""".format(
    row[0], row[1], row[2]))

    def manual_replacement(self, cursor):
        """This method is used if the user want to enter a product name
        manually"""
        self.name = input("""Entrez le nom du produit que vous souhaitez
remplacer:
""")
        formated_name = "%" + self.name + "%"
        answer_ing = input("""
Souhaitez vous la liste des ingrédients du produit qui sera le remplaçant?
y pour confirmer 
""")
        if answer_ing not in ("y", "Y"):
            sql = ("""SELECT Product.product_name, product.url
                   FROM Product
                   INNER JOIN Store_availability
                   ON Product.id = Store_availability.product_id
                   INNER JOIN Product_category
                   ON Product.id = Product_category.product_id
                   WHERE Product.product_name LIKE %s
                   AND Store_availability.store_id = %s
                   AND Product_category.category_id = %s
                   ORDER BY Product.nutrition_grades LIMIT 1""")
            val = (formated_name, self.store_selected, self.category_selected)
            cursor.execute(sql, val)
            for row in cursor:
                self.product_found = True
                print("Nous vous avons sélectionné ceci:")
                self.selec_prod = row[0]
                print("la ou le {0} (plus d'info ici: {1})".format(
                    row[0], row[1]))
        else:
            sql = ("""SELECT Product.product_name, Product.ingredients,
                   product.url FROM Product
                   INNER JOIN Store_availability
                   ON Product.id = Store_availability.product_id
                   INNER JOIN Product_category
                   ON Product.id = Product_category.product_id
                   WHERE Product.product_name LIKE %s
                   AND Store_availability.store_id = %s
                   AND Product_category.category_id = %s
                   ORDER BY Product.nutrition_grades LIMIT 1""")
            val = (formated_name, self.store_selected, self.category_selected)
            cursor.execute(sql, val)
            for row in cursor:
                self.product_found = True
                print("Nous vous avons sélectionné ceci:")
                self.selec_prod = row[0]
                print("""
la ou le {0} qui contient:\n{1}\n Plus d'info ici: {2}""".format(
    row[0], row[1], row[2]))

    def replacement_record(self, cursor, mydb):
        """Third part of the replacement process. This methode let the
        user choose to record the product replacement in database. This
        methode is only used if a product replacement was found in the
        first part of the replacement process."""
        self.product_found = False
        answer_selec = input("""
Cela vous convient-il? y pour confirmer
""")
        if answer_selec in ("y", "Y"):
            # searching for the id of the replacement product to record
            # it later in the Research_history table.
            sql = ("""SELECT Product.id FROM Product WHERE
                   Product.product_name = %s""")
            val = (self.selec_prod,)
            cursor.execute(sql, val)
            for row in cursor:
                id_prod = row[0]
            # record the change into the Research_history table.
            sql = """INSERT INTO Research_history (product_researched_name,
                  product_id_replaced, store_id_replaced)
                  VALUES (%s, %s, %s)"""
            val = (self.name, int(id_prod), self.store_selected)
            cursor.execute(sql, val)
            mydb.commit()
