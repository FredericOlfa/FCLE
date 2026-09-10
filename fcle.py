import os
import re
import hashlib
import argparse

class FCLE:
    def __init__(self, log_files, pattern):
        if isinstance(log_files, str):
            self.log_files = [log_files]
        else:
            self.log_files = log_files
            
        self.pattern = re.compile(pattern)
        self.last_seen_hashes = {}

        # Initialisation des repères sur la fin de chaque fichier existant
        for file_path in self.log_files:
            self.last_seen_hashes[file_path] = self._get_last_line_hash(file_path)

    def _hash_line(self, line):
        return hashlib.md5(line.strip().encode('utf-8')).hexdigest()

    def _get_last_line_hash(self, file_path):
        """Récupère le hash de la dernière ligne non vide du fichier."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line in reversed(lines):
                    clean_line = line.strip()
                    if clean_line:
                        return self._hash_line(clean_line)
        except Exception as e:
            print(f"Erreur lors de l'initialisation de '{file_path}' : {e}")

        return None

    def check(self):
        found_errors = []
        
        for file_path in self.log_files:
            if not os.path.exists(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                if not lines:
                    continue

                last_hash = self.last_seen_hashes.get(file_path)
                start_index = 0

                if last_hash is not None:
                    found_anchor = False
                    # Recherche du point d'ancrage en partant de la fin
                    for i in range(len(lines) - 1, -1, -1):
                        if self._hash_line(lines[i]) == last_hash:
                            start_index = i + 1  # Reprendre après la dernière ligne vue
                            found_anchor = True
                            break
                    
                    # Si la ligne repère a été purgée par la rotation
                    if not found_anchor:
                        start_index = max(0, len(lines) - 50)

                # Traitement des nouvelles lignes uniquement
                new_lines = lines[start_index:]
                for line in new_lines:
                    clean_line = line.strip()
                    if clean_line and self.pattern.search(clean_line):
                        found_errors.append(f"[{file_path}] {clean_line}")

                # Mise à jour du hash avec la dernière ligne lue
                self.last_seen_hashes[file_path] = self._get_last_line_hash(file_path)

            except Exception as e:
                print(f"Erreur lors de la lecture de '{file_path}' : {e}")

        return found_errors

    def gen_check(self, interval=60):
        """Génère un itérateur qui vérifie les fichiers de log à intervalles réguliers.
        param interval: Intervalle en secondes entre chaque vérification.
        """
        import time
        while True:
            errors = self.check()
            if errors:
                yield errors
            time.sleep(interval)

    def run(self, interval=60, callback=None):
        """Exécute la vérification des fichiers de log à intervalles réguliers.
        param interval: Intervalle en secondes entre chaque vérification.
        param callback: Fonction à appeler avec les erreurs trouvées.
        """
        for errors in self.gen_check(interval):
            if callback:
                callback(errors)
            else:
                print("Erreurs trouvées :")
                for error in errors:
                    print(error)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analyse des fichiers de log en continu et envoie d'alertes SMTP.")
    
    # Arguments obligatoires
    parser.add_argument('logs', nargs='+', help="Liste des fichiers de log à surveiller (ex: app.log web.log)")
    
    # Options optionnelles avec valeurs par défaut
    parser.add_argument('-p', '--pattern', default=r'ERROR|CRITICAL', help="Motif Regex à rechercher (défaut: 'ERROR|CRITICAL')")
    parser.add_argument('-i', '--interval', type=int, default=60, help="Intervalle entre chaque vérification en secondes (défaut: 60)")
    
    # Configuration SMTP via la CLI
    parser.add_argument('--smtp-host', default='smtp-mutualise.hexanet.fr', help="Serveur SMTP")
    parser.add_argument('--smtp-port', type=int, default=587, help="Port SMTP (défaut: 587)")
    parser.add_argument('--smtp-sender', default='noreply@olfa.fr', help="Adresse de l'expéditeur")
    parser.add_argument('--smtp-recipient', default='frederic.thome@olfa.fr', help="Adresse du destinataire")

    args = parser.parse_args()

    # Initialisation de la classe FCLE
    fcle = FCLE(args.logs, args.pattern)

    # Import du module SMTP local
    from smtp import Smtp
    smtp = Smtp(args.smtp_host, args.smtp_port, args.smtp_sender, starttls=True)

    def on_error_found(errors):
        subject = "Erreurs détectées dans les fichiers de log"
        body = "\n".join(errors)
        smtp.send(args.smtp_recipient, subject, body)

    # Lancement du scanner
    fcle.run(interval=args.interval, callback=on_error_found)