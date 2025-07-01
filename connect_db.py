"""
Module de gestion de la connexion à une base de données PostgreSQL.

Ce module fournit des fonctions et une classe pour gérer les connexions à une base de données PostgreSQL. 
Il simplifie la gestion des connexions en utilisant un gestionnaire de contexte et permet de tester rapidement 
si une connexion à la base de données peut être établie.

Fonctionnalités principales :
- Établir une connexion à une base de données PostgreSQL à l'aide de `psycopg2`.
- Gérer automatiquement la fermeture de la connexion avec un gestionnaire de contexte.
- Tester la connectivité avec la base de données.

Configuration requise :
- Un dictionnaire `DATABASE` contenant les paramètres de connexion.

"""

import psycopg2  # type: ignore


DATABASE = {
    "host": "qg.enzo-palermo.com",
    "database": "mspr502",
    "user": "mspr502",
    "password": "s5t4v5",
    "port": 5432
}

def get_db_connection():
    """
    Établit une connexion à la base de données PostgreSQL.

    Utilise les paramètres définis dans le dictionnaire `DATABASE` pour se connecter 
    à la base de données.

    Returns:
        psycopg2.extensions.connection: Une instance de connexion active à la base de données.
        None: Si la connexion échoue.

    Exceptions:
        Exception: Si une erreur se produit lors de la tentative de connexion.

    Exemple:
        >>> conn = get_db_connection()
        Connexion réussie à la base de données
    """
    try:
        conn = psycopg2.connect(**DATABASE)
        print("Connexion réussie à la base de données")
        return conn
    except Exception as e:
        print("Erreur lors de la connexion à la base de données :", e)
        return None

class DBConnection:
    """
    Gestionnaire de contexte pour la connexion à une base de données PostgreSQL.

    Cette classe permet de gérer automatiquement l'ouverture et la fermeture 
    des connexions à la base de données.

    Exemple:
        >>> with DBConnection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT 1")
    """
    def __init__(self):
        """ Initialise l'attribut conn à None. """
        self.conn = None

    def __enter__(self):
        """
        Établit une connexion lors de l'entrée dans le bloc `with`.

        Returns:
            psycopg2.extensions.connection: Une instance de connexion active.
        """
        self.conn = get_db_connection()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Ferme la connexion lors de la sortie du bloc `with`.

        Args:
            exc_type (type): Type de l'exception levée.
            exc_value (Exception): Instance de l'exception levée.
            traceback (traceback): Traceback de l'exception levée.
        """
        if self.conn:
            self.conn.close()
            print("Connexion fermée")

def test_db_connection():
    """
    Teste la connectivité avec la base de données.

    Cette fonction tente d'établir une connexion à la base de données PostgreSQL 
    en utilisant les paramètres définis dans le dictionnaire `DATABASE`. Si la connexion 
    est réussie, elle est immédiatement fermée.

    Returns:
        None

    Exemple:
        >>> test_db_connection()
        Connexion à la base de données réussie.
    """
    try:
        conn = psycopg2.connect(**DATABASE)
        conn.close()
        print("Connexion à la base de données réussie.")
    except Exception as e:
        print("Erreur lors de la connexion à la base de données :", e)

test_db_connection()
