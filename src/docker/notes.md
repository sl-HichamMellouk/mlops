# Notes sur le pipeline de test

- Chaque test s’exécute dans un container Docker séparé afin d’isoler les scénarios d’Authentication, d’Authorization et de Content.
- Le service `api` utilise l’image `datascientest/fastapi:1.0.0` qui est exposé sur le port 8000.
- Les tests partagent un volume `./logs:/app/logs` pour écrire un fichier unique `api_test.log`.
- La variable d’environnement `LOG=1` active l’écriture des traces dans le fichier de log.
- Le `docker-compose.yml` enchaîne les tests avec `depends_on` pour garder un ordre logique dans le pipeline.
- `setup.sh` construit les images, lance les services et attend que les trois services de test se terminent.
