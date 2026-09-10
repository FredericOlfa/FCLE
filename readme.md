## FCLE (Fred Check Log and Email)

Un utilitaire pour scanner une liste de logs et envoyer des alertes quand des mots clefs sont trouvés (ex : 'ERROR')

usage : 

```python
smtp = Smtp(...)
checker = FCLE(log_files=['log_file1.log', 'log_file2.log'], pattern = 'ERROR')
errors = checker.check()
if errors:
    smtp.send('toto@gmail.com', 'Errors founds','\n'.join(errors))
```