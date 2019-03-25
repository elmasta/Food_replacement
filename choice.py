from display import cat_selection_screen, store_screen
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
        self.product_found = True
        self.name = ""
        self.quit_err = 0

    def category_choice(self):
        """This methode is used to select a category"""
        cat_selection_screen()
        selection = input("Votre sélection: ")
        if selection.isalpha() is True or int(selection) < 1 or\
           int(selection) > 10:
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
            print("{0} is {1} is {2}\n".format(row[0], row[1], row[2]))

    def replacement_consult(self, cursor):
        """This methode is used if the user want to consult the last
        ten changes made"""
        print("Voici vos dix derniers remplacements:")
        cursor.execute("""SELECT Research_history.product_researched_name,
                       Product.product_name
                       FROM Product 
                       LEFT JOIN Research_history
                       ON Product.id = Research_history.product_id_replaced
                       WHERE Research_history.product_researched_name
                       IS NOT NULL
                       ORDER BY Research_history.id DESC""")
        for row in cursor:
            print("{0} was replaced by {1}".format(row[0], row[1]))

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

    def replacement(self, cursor):
        """This methode is used if the user want to replace one product
        by another. It ends after the search. Another methode is
        used to record that change if the replacement was successful"""
        self.name = input("""Entrez le nom du produit que vous souhaitez
remplacer:
""")
        formated_name = "%" + self.name + "%"
        answer_ing = input("""
Souhaitez vous la liste des ingrédients du produit qui sera le remplaçant?
y ou Y pour oui 
""")
        if answer_ing != "y" or "Y":
            sql = ("""SELECT Product.product_name FROM Product
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
            found = 0
            for row in cursor:
                found = 1
                self.product_found = True
                print("Nous vous avons sélectionné ceci:")
                self.selec_prod = row[0]
                print("la ou le {0}".format(row[0]))
        else:
            sql = ("""SELECT Product.product_name, Product.ingredients
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
                found = 1
                self.product_found = True
                print("Nous vous avons sélectionné ceci:")
                self.selec_prod = row[0]
                print("la ou le {0} qui contient:\n{1}".format(row[0], row[1]))
            if found == 0:
                self.product_found = False

    def replacement_record(self, cursor, mydb):
        """Second part of the replacement process. This methode let the
        user choose to record the product replacement in database. This
        methode is only used if a product replacement was found in the
        first part of the replacement process."""
        answer_selec = input("""
Cela vous convient-il? y ou Y pour valider 
""")
        if answer_selec == "y" or "Y":
            #searching for the id of the replacement product to record
            #it later in the Research_history table.
            sql = ("""SELECT Product.id FROM Product WHERE
                   Product.product_name = %s""")
            val = (self.selec_prod,)
            cursor.execute(sql, val)
            for row in cursor:
                id_prod = row[0]
            #record the change into the Research_history table.
            sql = """INSERT INTO Research_history (product_researched_name,
                  product_id_replaced)
                  VALUES (%s, %s)"""
            val = (self.name, int(id_prod))
            cursor.execute(sql, val)
            mydb.commit()
