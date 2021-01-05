import requests
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from datetime import datetime
import re
import sys
from tradingview_ta import TA_Handler, Interval
import os
import time

#A faire : infos action id
# save clée api dans un txt
# ind.tech
# password quand on se co


def get_javascript():
    #api_key = "uPRsMKmSEjVZFZHp9CZjeS1bUWo1"
    try:
        r = requests.get(f'https://proxybot.io/api/v1/{api_key}?render_js=true&url=https://www.etoro.com/people/{people}/portfolio')
        html_doc = r.text
    except:
        print("API ERROR")
    return html_doc

def save_javascript(html_doc):
    fichier = open(f"{people}.html", "w")
    fichier.close()
    fichier = open(f"{people}.html", "a")
    fichier.write(html_doc)
    fichier.close()

def open_javascript():
    fichier = open(f"{people}.html", "r")
    html_doc = fichier.read()
    html_doc = str(html_doc)
    fichier.close()
    return html_doc


def bs4(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup

def bs4_main_table(soup):
    main_table = soup.find('ui-table-body', attrs={'class': 'ng-scope'})
    return main_table

def bs4_get_name():
    name = element.find('p', attrs={'class': 'i-portfolio-table-hat-fullname ng-binding ng-scope'}).text
    return name

def bs4_get_tec_symbol():
    tec_symbol = element.find('div', attrs={'class': 'i-portfolio-table-name-symbol ng-binding'}).text
    return tec_symbol

def bs4_get_position():
    position = element.find('ui-table-cell').text
    position = position.strip()
    return position

def bs4_get_pourcent():
    pourcent = element.find('ui-table-cell', attrs={'class': 'ng-binding'}).text
    pourcent = re.sub('%', '', pourcent)
    pourcent = float(pourcent)
    return pourcent

def create_db():
    with connexion: 
        connexion.execute("""CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scraping_id INT,
        id_people INT,
        id_action INT,
        pourcent FLOAT,
        date DATE,
        position TEXT
        );""")

    with connexion: 
        connexion.execute("""CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        status INT,
        max_traders INT,
        tec_symbol TEXT,
        tec_exchange TEXT,
        tec_country TEXT
        );""")

    with connexion: 
        connexion.execute("""CREATE TABLE IF NOT EXISTS peoples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        people TEXT,
        followed INT
        );""")

def add_values_db_positions():
    with connexion:
        c.execute("INSERT INTO positions (scraping_id, id_people, id_action, pourcent, date, position) VALUES (?, ?, ?, ?, ?, ?)", (scraping_id, id_people, id_action, pourcent, date, position))

def add_values_db_actions_if_is_new_and_get_id_action():

    try:
        with connexion:
            c.execute(f"SELECT id FROM actions where name = '{name}';")
            id_action = c.fetchone()[0]
            #print("> ALREADY IN DB :",id_action,name)
    except:
        with connexion:
            c.execute("INSERT INTO actions (name, status, max_traders, tec_symbol) VALUES (?, ?, 0, ?)", (name, status, tec_symbol))
            c.execute(f"SELECT id FROM actions where name = '{name}';")
            id_action = c.fetchone()[0]
            #print("> NEW INSERT DB :",id_action,name)
    return id_action

def add_values_db_peoples():
    with connexion:
        c.execute("INSERT INTO actions (name, status, max_traders, tec_symbol) VALUES (?, ?, 0, ?)", (name, status, tec_symbol))

def check_id_action(id_action):
    try:
        with connexion:
            c.execute(f"SELECT status FROM actions where id = {id_action};")
            status = c.fetchone()[0]
    except:
        print("ERROR 1")
    return status

def console_logs():
    try:
        status = check_id_action(id_action)
        if status == 1:
            print('>>' , people,"|",name,"|",pourcent,"|",position)
        else:
            print('  ',people,"|",name,"|",pourcent,"|",position)
    except:
        print(command)

def get_scraping_id_db():
    with connexion:
        c.execute(f"SELECT scraping_id FROM positions ORDER BY scraping_id DESC;")
        try:
            scraping_id = c.fetchone()[0]
            scraping_id += 1
        except:
            scraping_id = 1
    return scraping_id

def add_trader():
    people = str(command[11:])

    try:
        with connexion:
            c.execute(f"SELECT id FROM peoples where people = '{people}';")
            c.fetchone()[0] #declenche un bug si il existe pas
            c.execute(f"UPDATE PEOPLES SET followed = 1 WHERE people = '{people}' ;")
            print("Activation copy trader :", people)
    except:
        try:
            with connexion:
                c.execute("INSERT INTO peoples (people, followed) VALUES (?, ?)", (people, followed))
                print("[NEW] Activation copy trader :", people)
        except:
            print("ERROR 2")
    


def list_traders():
    try:
        with connexion:
            c.execute("SELECT * FROM peoples;")
            all_peoples = c.fetchall()
            print("id | name | followed")
            for one_people in all_peoples:
                print(one_people[0],"|",one_people[1],"|",one_people[2])
    except:
        print("ERROR 2.5")



def del_trader():
    try:
        with connexion:
            people = str(command[11:])
            c.execute(f"UPDATE PEOPLES SET followed = 0 WHERE people = '{people}' ;")
            print("Désactivation copy trader :", people)
    except:
        print("ERROR 3")

def fdel_trader():
    try:
        with connexion:
            people = str(command[12:])
            c.execute(f"DELETE FROM PEOPLES WHERE people = '{people}' ;")
            print("Suppression trader :", people)
    except:
        print("ERROR 4")

def get_list_traders():
    peoples = []
    with connexion:
        c.execute("SELECT people FROM peoples WHERE followed = 1;")
        list_peoples = c.fetchall()

        for people in list_peoples:
            peoples.append(people[0])
        return peoples


def get_id_people():
    with connexion:
        c.execute(f"SELECT id FROM peoples where people = '{people}';")
        id_people = c.fetchone()[0]
        return id_people


def all_infos():
    try:
        nb_actions_top = 0
        i = 0
        nb_infos = int(command[6:])
        with connexion:
            c.execute(f"SELECT MAX(scraping_id) FROM positions;")
            scraping_id_max = c.fetchone()[0]

            for scraping_id_max in range(1, scraping_id_max +1):
                try:
                    c.execute(f"""SELECT actions.id, actions.name, COUNT(id_action) AS nb_traders, AVG(pourcent) AS avg_pourcent, positions.scraping_id, actions.max_traders
                                FROM positions 
                                INNER JOIN peoples ON positions.id_people = peoples.id
                                INNER JOIN actions ON positions.id_action = actions.id WHERE scraping_id = {scraping_id_max} GROUP BY id_action ORDER BY nb_traders DESC, avg_pourcent DESC LIMIT {nb_infos};""")
                    ladder = c.fetchall()


                    c.execute(f"SELECT date FROM positions where scraping_id = {scraping_id_max};")
                    date = c.fetchone()[0]
                    print("-"*57)
                    print("ID scraping :",scraping_id_max,"| Top", nb_infos,"des actions les plus détenues le",date,":")
                    print("rank | id | action | traders | pourcent | max_traders\n")
                    for one_value in ladder:
                        id_action = one_value[0]
                        status = check_id_action(id_action)
                        i += 1
                        if status == 1:
                            nb_actions_top += 1
                            print('>>',i,"|",one_value[0],"|",one_value[1],"|",one_value[2],"|",round(one_value[3],2),"|",one_value[5])
                        else:
                            print("  ",i,"|",one_value[0],"|",one_value[1],"|",one_value[2],"|",round(one_value[3],2),"|",one_value[5])
                    

                    print("\nVous avez",nb_actions_top,"actions dans le top",nb_infos)
                    i = 0
                    nb_actions_top = 0
                    
                except:
                    pass
    except:
        print("ERROR 6")
    
def add_db_actions_max_traders():
    try:
        with connexion:
            c.execute(f"SELECT MAX(scraping_id) FROM positions;")
            scraping_id_max = c.fetchone()[0]
            c.execute(f"""SELECT actions.id, COUNT(id_action)
                        FROM positions 
                        INNER JOIN peoples ON positions.id_people = peoples.id
                        INNER JOIN actions ON positions.id_action = actions.id WHERE scraping_id = {scraping_id_max} GROUP BY id_action;""")
            ladder = c.fetchall()
            for value in ladder:
                c.execute(f"SELECT max_traders FROM actions where id = {value[0]};")
                max_traders = c.fetchone()[0]
                if value[1] > max_traders:
                    c.execute(f"UPDATE ACTIONS SET max_traders = {value[1]} WHERE id = {value[0]} ;")
    except:
        print("ERROR 7")

def add_action():
    try:
        id_position = int(command[11:])
        with connexion:
            c.execute(f"UPDATE ACTIONS SET status = 1 WHERE id = {id_position};")
            print("Action ID",id_position,"ajoutée !")
    except:
        print("ERROR 8")

def del_action():
    try:
        id_position = int(command[11:])
        with connexion:
            c.execute(f"UPDATE ACTIONS SET status = 0 WHERE id = {id_position};")
            print("Action ID",id_position,"supprimée !")
    except:
        print("ERROR 9")

def my_actions():
    try:
        with connexion:
            c.execute(f"SELECT MAX(scraping_id) FROM positions;")
            scraping_id_max = c.fetchone()[0]
            c.execute("SELECT id, name, max_traders FROM actions WHERE status = 1;")
            my_total_actions = c.fetchall()
            c.execute(f"""SELECT actions.name
                        FROM positions 
                        INNER JOIN peoples ON positions.id_people = peoples.id
                        INNER JOIN actions ON positions.id_action = actions.id WHERE actions.status = 1 AND scraping_id = {scraping_id_max} GROUP BY id_action;""")
            my_actions = c.fetchall()

            print("Nombre d'actions possédées :",len(my_total_actions))
            print("Nombre d'actions possédées qu'aucun trader ne détient :",len(my_total_actions)-len(my_actions))
            print("id | action | traders | pourcent | max_traders\n")

            for one_action in my_total_actions:
                c.execute(f"""SELECT actions.id, actions.name, COUNT(id_action) AS nb_traders, AVG(pourcent) AS avg_pourcent, positions.scraping_id, actions.max_traders
                            FROM positions 
                            INNER JOIN peoples ON positions.id_people = peoples.id
                            INNER JOIN actions ON positions.id_action = actions.id WHERE actions.status = 1 AND scraping_id = {scraping_id_max} AND id_action = {one_action[0]};
                            """)
                my_actions = c.fetchone()
                try:
                    print('>>',my_actions[0],"|",my_actions[1],"|",my_actions[2],"|",round(my_actions[3],2),"|",my_actions[5])
                except:
                    print(' [ALERT] >>',one_action[0],"|",one_action[1],"| 0 | 0 |",one_action[2])
    except:
        print("ERROR 10")

def del_infos():
    try:
        with connexion:
            del_id = int(command[11:])
            c.execute(f"DELETE FROM positions WHERE scraping_id = {del_id};")
            print("Suppression de l'historique scraping_id :", del_id)
    except:
        print("ERROR 11")

def tech():
    id_focus = input("ID action > ")
    symbol = input("entreprise symbole > ")
    exchange = input("place bourisère > ")
    country = input("pays > ")

    print("Analyse technique :")



    try :
        _object = TA_Handler()
        _object.set_symbol_as(symbol)
        _object.set_exchange_as_crypto_or_stock(exchange)
        _object.set_screener_as_stock(country)
        _object.set_interval_as(Interval.INTERVAL_1_DAY)
        tradingview_result = _object.get_analysis().summary
        print("1 jour >",tradingview_result)

        _object.set_interval_as(Interval.INTERVAL_1_WEEK)
        tradingview_result = _object.get_analysis().summary
        print("1 sem >",tradingview_result)

        _object.set_interval_as(Interval.INTERVAL_1_MONTH)
        tradingview_result = _object.get_analysis().summary
        print("1 mois >",tradingview_result)

        print("Infos ajoutée en DB")
        with connexion:
            c.execute(f"UPDATE ACTIONS SET tec_exchange = '{exchange}', tec_country = '{country}' WHERE id = {id_focus};")
    except:
        print("ERREUR > une ou plusieures données sont érronées.")

def all_actions():
    try:
        with connexion:
            c.execute("SELECT id,name,tec_symbol FROM actions ORDER BY name;")
            all_actions = c.fetchall()
            print("id | name | symbol")
            for action in all_actions:
                id_action = action[0]
                status = check_id_action(id_action)
                if status == 1:
                    print('>>',action[0],"|",action[1],"|",action[2])
                else:
                    print('  ',action[0],"|",action[1],"|",action[2])
    except:
        print("ERROR 12")

def analyse_technique(id_infos):

    print("Analyse technique :")


    try:
        with connexion:
            c.execute(f"SELECT tec_symbol, tec_exchange, tec_country FROM actions where id = {id_infos};")
            result = c.fetchone()
            tec_symbol = result[0]
            tec_exchange = result[1]
            tec_country = result[2]


            try : #1- on tente avec ce qui est stocké en db
                _object = TA_Handler()
                _object.set_symbol_as(tec_symbol)
                _object.set_exchange_as_crypto_or_stock(tec_exchange)
                _object.set_screener_as_stock(tec_country)
                
                _object.set_interval_as(Interval.INTERVAL_1_DAY)
                tradingview_result = _object.get_analysis().summary

                _object.set_interval_as(Interval.INTERVAL_1_WEEK)
                tradingview_result2 = _object.get_analysis().summary

                _object.set_interval_as(Interval.INTERVAL_1_MONTH)
                tradingview_result3 = _object.get_analysis().summary

                c.execute(f"UPDATE ACTIONS SET tec_exchange = '{tec_exchange}', tec_country = '{tec_country}' WHERE id = {id_infos};")

                print("1 jour >",tradingview_result)
                print("1 sem >",tradingview_result2)
                print("1 mois >",tradingview_result3)
            except:
                tec_country = "AMERICA"
                tec_exchange = "NYSE"

                try :
                    _object = TA_Handler()
                    _object.set_symbol_as(tec_symbol)
                    _object.set_exchange_as_crypto_or_stock(tec_exchange)
                    _object.set_screener_as_stock(tec_country)

                    _object.set_interval_as(Interval.INTERVAL_1_DAY)
                    tradingview_result = _object.get_analysis().summary

                    _object.set_interval_as(Interval.INTERVAL_1_WEEK)
                    tradingview_result2 = _object.get_analysis().summary

                    _object.set_interval_as(Interval.INTERVAL_1_MONTH)
                    tradingview_result3 = _object.get_analysis().summary

                    c.execute(f"UPDATE ACTIONS SET tec_exchange = '{tec_exchange}', tec_country = '{tec_country}' WHERE id = {id_infos};")

                    print("1 jour >",tradingview_result)
                    print("1 sem >",tradingview_result2)
                    print("1 mois >",tradingview_result3)
                        
                except:
                    tec_country = "AMERICA"
                    tec_exchange = "NASDAQ"
                    try :
                        _object = TA_Handler()
                        _object.set_symbol_as(tec_symbol)
                        _object.set_exchange_as_crypto_or_stock(tec_exchange)
                        _object.set_screener_as_stock(tec_country)
                        
                        _object.set_interval_as(Interval.INTERVAL_1_DAY)
                        tradingview_result = _object.get_analysis().summary

                        _object.set_interval_as(Interval.INTERVAL_1_WEEK)
                        tradingview_result2 = _object.get_analysis().summary

                        _object.set_interval_as(Interval.INTERVAL_1_MONTH)
                        tradingview_result3 = _object.get_analysis().summary

                        c.execute(f"UPDATE ACTIONS SET tec_exchange = '{tec_exchange}', tec_country = '{tec_country}' WHERE id = {id_infos};")

                        print("1 jour >",tradingview_result)
                        print("1 sem >",tradingview_result2)
                        print("1 mois >",tradingview_result3)

                    except:
                        print("Aucune donnée d'analyse technique, utilisez .tech")

    except:
        print("ERROR 14")


def analyse_fondamentale(id_infos):

    print("Analyse fondamentale :")
    a = -1

    try:
        with connexion:
            c.execute(f"SELECT name FROM actions where id = {id_infos};")
            result = c.fetchone()
            name = result[0]
            print(name)
            name = name.replace(" ", "+")

            link = f"https://www.zonebourse.com/recherche/?mots={name}&RewriteLast=recherche&noredirect=0&type_recherche=0"
            #print(link)

            pagelink = urllib.request.urlopen(link)
            soup = BeautifulSoup(pagelink, 'html.parser')
            results = soup.find('table', attrs={'class': 'tabBodyLV17'})
            results = list(results)
            results = results[3]
            results = list(results)
            results = results[2]
            url = results.find('a')
            url = url['href']
            
            url = "https://www.zonebourse.com" + url + "fondamentaux/"
            #print(url)


            pagelink = urllib.request.urlopen(url)
            soup = BeautifulSoup(pagelink, 'html.parser')

            results = soup.find('table', attrs={'class': 'tabElemNoBor overfH'})
            results = list(results)
            results = results[2]

            annees = results.findAll('tr')

            for column in annees:
                # ME SUIS ARETTER ICI
                print("----------------------------------")
                a += 1
                print(a)
                print(column)

            # print("Top 50 sociétés par capitalisation boursière :")
            # print("rank | capitation (milions $) | variations 1janv | société | secteur | cours actuel\n")


    except:
        print("ERREUR : impossible de charger les données")




def all_infos_action():
    try:
        id_infos = int(command[7:])
        with connexion:
            c.execute(f"SELECT MAX(scraping_id) FROM positions;")
            scraping_id_max = c.fetchone()[0]
            c.execute(f"""SELECT peoples.people, pourcent, position, actions.name, actions.tec_symbol, actions.tec_exchange, actions.tec_country, date, scraping_id, max_traders FROM positions
                        INNER JOIN peoples ON positions.id_people = peoples.id
                        INNER JOIN actions ON positions.id_action = actions.id WHERE id_action = {id_infos} AND scraping_id = {scraping_id_max} ORDER BY pourcent DESC;""")
            result = c.fetchall()




            for scraping_id_max in range(1, scraping_id_max +1):
                try:
                    c.execute(f"""SELECT peoples.people, pourcent, position, actions.name, actions.tec_symbol, actions.tec_exchange, actions.tec_country, date, scraping_id, max_traders FROM positions
                                INNER JOIN peoples ON positions.id_people = peoples.id
                                INNER JOIN actions ON positions.id_action = actions.id WHERE id_action = {id_infos} AND scraping_id = {scraping_id_max} ORDER BY pourcent DESC;""")
                    result = c.fetchall()
                    c.execute(f"""SELECT AVG(pourcent)
                            FROM positions 
                            INNER JOIN peoples ON positions.id_people = peoples.id
                            INNER JOIN actions ON positions.id_action = actions.id WHERE scraping_id = {scraping_id_max} AND id_action = {id_infos};""")
                    avg_pourcent = c.fetchone()
                    error_declenchement = result[0][8]
                    print("-"*57)
                    print("ID scraping :",scraping_id_max,"|",len(result),"traders possèdent cette action le",result[0][7],"avec en moyenne",round(avg_pourcent[0],2),'% investis')
                    print("name | pourcent | link\n")

                    for one_value in result:
                        print(one_value[0],"|",one_value[1],f"| https://www.etoro.com/people/{one_value[0]}/portfolio/{one_value[4]}")
                except:
                    try:
                        c.execute(f"""SELECT date FROM positions WHERE scraping_id = {scraping_id_max};""")
                        date = c.fetchone()
                        print("-"*57)
                        print("ID scraping :",scraping_id_max,"| 0 trader possèdent cette action le",date[0])
                    except:
                        print("ERROR 497255")




            print("-"*57)
            analyse_technique(id_infos)
            #print("-"*57)
            #analyse_fondamentale(id_infos)

            try:
                c.execute(f"""SELECT peoples.people, pourcent, position, actions.name, actions.tec_symbol, actions.tec_exchange, actions.tec_country, date, scraping_id, max_traders FROM positions
                            INNER JOIN peoples ON positions.id_people = peoples.id
                            INNER JOIN actions ON positions.id_action = actions.id WHERE id_action = {id_infos} AND scraping_id = {scraping_id_max} ORDER BY pourcent DESC;""")
                result = c.fetchall()
            except:
                print("error 458736")
            print("-"*57)

            print("Action :",result[0][3])
            print("ID :",id_infos)
            print("Max traders:",result[0][9])
            print("Tec Symbol :",result[0][4])
            print("Tec Exchange :",result[0][5])
            print("Tec Country :",result[0][6])
            print("Position :",result[0][2])






    except:
        print("ERROR 15")

def check_expiration():
    if date >= date_expiration:
        os.system('cls' if os.name=='nt' else 'clear')
        print("-"*100) 
        print("Bienvenue",account,"! Votre abonnement Tradyglo est expiré !")
        print("-"*100)
        time.sleep(1)
        print("Fermeture de Tradyglo en cours...") 
        time.sleep(4)
        sys.exit()
    else:
        print("Bienvenue",account,"! Votre abonnement Tradyglo expire le :",date_expiration)

def login(infinity):
    while infinity:
        command = input("User > ")
        if command == account1:
            command = input("Password > ")
            if command == password1:
                account = account1
                return account
            else:
                print("Password not found")
        elif command == account2:
            command = input("Password > ")
            if command == password2:
                account = account2
                return account
            else:
                print("Password not found")
        elif command == account3:
            command = input("Password > ")
            if command == password3:
                account = account3
                return account
            else:
                print("Password not found")
        else:
            print("User not found")


def new_api_key():
    api_key = str(command[8:])
    fichier = open("API_KEY.txt", "w")
    fichier.close()
    fichier = open("API_KEY.txt", "a")
    fichier.write(api_key)
    fichier.close()
    print("New API KEY :",api_key)

def load_api_key():
    fichier = open("API_KEY.txt", "r")
    api_key = str(fichier.read())
    fichier.close()
    return api_key

def top_capitalisations():
    link = "https://www.zonebourse.com/bourse/actions/"
    oneontwo = -2
    exept_first = True
    rank = 0

    pagelink = urllib.request.urlopen(link)
    soup = BeautifulSoup(pagelink, 'html.parser')
    results = soup.find('table', attrs={'class': 'tabBodyLV17'})
    # news = soup.findall('table', attrs={'id': 'ZBS_restab_2b'})
    #news = soup.find('table id="ZBS_restab_2b"', attrs={'class': 'tabBodyLV17'})

    print("Top 50 sociétés par capitalisation boursière :")
    print("rank | capitalisation (milions $) | variations 1janv | société | secteur | cours actuel\n")

    for result in results:
        
        a = -1
        for resu in result:
            a+= 1
            try:
                if a == 1:
                    societe = resu.text
                elif a == 2:
                    cours = resu.text
                elif a == 4:
                    capitation = resu.text
                elif a == 5:
                    variation = resu.text
                elif a == 6:
                    secteur = resu.text
            except:
                print("ERROR")
                pass
        try:

            oneontwo += 1
            if oneontwo == 0:
                if exept_first == False :
                    rank += 1
                    print(rank,"|",capitation,"|",variation,"|",societe,"|",secteur,"|",cours)
                exept_first = False
                oneontwo = -2
        except:
            pass

def tool_rental():
    a = 0
    b = 0
    capital_depart = int(input("Capital départ > "))
    rajout_mois = int(input("Montant dépôt mensuel > "))
    pourcent = int(input("Pourcentage gain annuel> "))
    max_annee = 51
    plus_values = 0
    total_plus_values = 0
    capital = capital_depart
    print("-"*60)
    for annee in range(0, max_annee):
        if a < 16 :
            print("Année :",annee,"|  Total capital :",int(capital),"| Plus-values anuelle :",int(plus_values),"| Total plus-values :",int(total_plus_values))
        else :
            b += 1
            if b == 5:
                print("Année :",annee,"|  Total capital :",int(capital),"| Plus-values anuelle :",int(plus_values),"| Total plus-values :",int(total_plus_values))
                b = 0




        a += 1
        last_capital = capital
        capital = capital + (12*rajout_mois)
        capital *= ((pourcent/100)+1)
        plus_values = capital - last_capital
        plus_values = plus_values - (rajout_mois*12)
        total_plus_values = total_plus_values + plus_values

#------------------------------  script  -------------------------------
os.system('cls' if os.name=='nt' else 'clear')
#api_key = "xbGDgilmZgN87vbBtcbSjfQE8tw1"

account1 = "myg"
password1 = "pea"
account2 = "pirlo"
password2 = "pokemon"
account3 = "tommy"
password3 = "987"
date_expiration = '2021-12-01'

bug = True
infinity = True
peoples = [] 
followed = 1
date = datetime.now().strftime('%Y-%m-%d')
list_commands="""Commandes disponibles:
    traders : Voir la liste des traders suivis
    add trader [NAME] : Follow un trader
    del trader [NAME] : Unfollow un trader
    fdel trader [NAME] : Supprime un trader

    copy : Lance la copie de tout les traders suivis

    infos [NB] : Classement des [NB] actions les plus achetées
    fdel infos [ID] : Supprime les infos liées à l'ID scraping

    action [ID] : Affiche toutes les infos liées à l'action
    actions : Voir la liste des actions possédées
    all actions : Voir la liste de toutes les actions
    add action [ID] : Ajoute une action
    del action [ID] : Supprime une action

    tech : Ajouter manuellement le module d'analyses techniques pour la commande action [ID]

    capit : Top 50 temps réel des plus grosses capitalisations

    api key [API_KEY] : Change la cléf API

    tool renta : Lance le tool pour calculer votre bénéfice moyen

    help : Liste des commandes
    clear : Nettoie la console
    exit : Sauvegarde et quitte proprement"""

connexion = sqlite3.connect("copy_trading.db")
c = connexion.cursor()
create_db()
api_key = load_api_key()

print("-"*100)
print("                                   Bienvenue sur Tradyglo V.1.1")
print("-"*100)

#--- login ---#
#account = login(infinity)
account = "Myg"


os.system('cls' if os.name=='nt' else 'clear')

print("-"*100)
print("                                   Bienvenue sur Tradyglo V.1.1")
print("-"*100)

print(list_commands)
print("-"*100)  


check_expiration()



while infinity:
    print("-"*100)  
    command = input("> ")


    if command == "copy":
        #try:
        scraping_id = get_scraping_id_db()

        peoples = get_list_traders()

        for people in peoples:
            while bug is True:
                try:
                    #get & save test réel [ACTIVIER SI REEL]
                    html_doc = get_javascript()

                    #load test local [ACTIVIER SI TEST]  ATTENTION, ne créé pas automatiquement les fichier html, si ils n'existent pas ça bug
                    #save_javascript(html_doc)
                    #html_doc = open_javascript()

                    #load obligatoire [TOUJURS ACTIVER]
                    soup = bs4(html_doc)
                    main_table = bs4_main_table(soup)

                    id_people = get_id_people()

                    
                    for element in main_table:

                        name = "Null"
                        pourcent = "Null"
                        position = "Null"
                        tec_symbol = "Null"
                        
                        id_action = 0
                        status = 0

                        try:
                            name = bs4_get_name()
                            pourcent = bs4_get_pourcent()
                            position = bs4_get_position()
                            tec_symbol = bs4_get_tec_symbol()

                            id_action = add_values_db_actions_if_is_new_and_get_id_action()
                            add_values_db_positions()
                            console_logs()
                        except:
                            pass
                    add_db_actions_max_traders()
                    #print("Début attente 300 secondes ...",datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    #time.sleep(120)
                    print("-"*100)
                    print("Fin chargement :",datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    print("-"*100)
                    bug = False
                except:
                    bug = True
                    print("ERROR, l'API KEY ne fonctionne pas ou les crédits sont épuisés, on relance le scraping ...")
            bug = True


    elif command == "traders":
        list_traders()

    elif command == "tool renta":
        tool_rental()

    elif command[:7] == "api key":
        new_api_key()
        api_key = load_api_key()

    elif command == "actions":
        my_actions()

    elif command == "capit":
        top_capitalisations()

    elif command[:6] == "action":
        all_infos_action()

    elif command[:10] == "add trader":
        add_trader()

    elif command[:10] == "del trader":
        del_trader()

    elif command[:11] == "fdel trader":
        fdel_trader()

    elif command[:5] == "infos":
        all_infos()

    elif command[:10] == "fdel infos":
        del_infos()

    elif command[:10] == "add action":
        add_action()

    elif command[:10] == "del action":
        del_action()

    elif command == "all actions":
        all_actions()

    elif command == "tech":
        tech()

    elif command == "exit":
        sys.exit()

    elif command == "clear":
        os.system('cls' if os.name=='nt' else 'clear')

    elif command == "help":
        print(list_commands)

    else:
        print("Commande inconnue, tapez 'help'")



