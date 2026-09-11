"""
Point d'entrée WSGI pour le déploiement sur Vercel.
Vercel importe la variable `app` (callable WSGI) depuis ce module.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import app, init_database

# Sur une plateforme serverless (Vercel), il n'y a pas d'étape de démarrage
# persistante : on s'assure donc que les tables existent (et sont peuplées
# avec des données de démo si vides) à chaque démarrage à froid de la fonction.
init_database()
