# -*- coding: Utf-8 -*

import requests
from display import start_screen
from choice import *

SELECTION = UserChoice()
SQL = SqlInit()

# connection to mysql
SQL.db_conection()


def main():
    """Main function"""

    quit = 0
    while quit == 0:
        start_screen()
        choice = input("Votre sélection: ")
        if choice == "1":
            SELECTION.category_choice()
            while SELECTION.quit_err == 1:
                SELECTION.category_choice()
            SELECTION.store_selection()
            while SELECTION.quit_err == 1:
                SELECTION.store_selection()
            SELECTION.replacement(SQL.cursordb)
            if SELECTION.product_found is not False:
                SELECTION.replacement_record(SQL.cursordb, SQL.mydb)
            else:
                print("""
Aucun produit de remplacement trouvé dans ce magasin ou cette catégorie
""")
        elif choice == "2":
            SELECTION.replacement_consult(SQL.cursordb)
        elif choice == "3":
            SELECTION.category_choice()
            SELECTION.db_consult(SQL.cursordb)
        else:
            quit = 1

main()
