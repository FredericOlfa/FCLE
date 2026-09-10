## FCLE (Fred Check Log and Email)

Un utilitaire pour scanner une liste de logs et envoyer des alertes quand des mots clefs sont trouvés (ex : 'ERROR')

usage : 

```python
smtp = Smtp(...)
checker = FCLE(log_files=['log_file1.log', 'log_file2.log'], pattern = 'ERROR')
errors = checker.check()
if errors:
    smtp.send('toto@gmail.com', 'Errors founds','\n'.join(errors))
#vérification continue
checker.run(interval = 10, callback = lambda errors:print(errors))
#alternative
for errors in checker.gen_check(30):
    print(errors)
```

Ou en ligne de commande

```
python fcle.py log1.log log2.log -i 5 -p "EXCEPTION|FATAL|CRITICAL" \
    --smtp-recipient "tech@olfa.fr" \
    --smtp-host "smpt.olfa.fr" \
    --smtp-port 587 \
    --smtp-sender "alertes@olfa.fr"
```

On peut aussi mettre les fichiers log dans un fichier txt:

```
python fcle.py logs_files.txt -i 30
```
avec logs
```
# Fichiers de log du serveur Web
/var/log/nginx/access.log
/var/log/nginx/error.log

# Fichiers applicatifs
app_prod.log
```