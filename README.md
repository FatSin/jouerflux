## JOUERFLUX
### API de gestion des politiques de firewall

Pour lancer l'API :

1. Créer la variable d'environnement **INIT_DB** afin de déployer la database:

`export INIT_DB=True`

2. Lancer l'application Flask avec uvicorn

`python -m venv venv`

`pip install -r requirements`

`uvicorn app:conn_app`

3. Pour se connecter au swagger : http://IP_serveur:8000/api/ui
4. Pour requêter en direct : IP_serveur:8000/api


