import re
import slack_sdk
import os
import csv
from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError

# Charger les variables d'environnement depuis .env
load_dotenv()

# Créer un client Slack avec votre token OAuth
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
client = slack_sdk.WebClient(token=slack_bot_token)

# Demander le lien du message à l'utilisateur et extraire l'ID du canal et le timestamp
message_link = input("Entrez le lien du message Slack : ")
match = re.search(r'\/archives\/(C[A-Z0-9]+)\/p(\d{10})(\d{6})', message_link)
if not match:
    print("Lien invalide.")
    exit(1)

channel_id = match.group(1)
timestamp = match.group(2) + '.' + match.group(3)

# Récupérer les réactions pour le message spécifié
try:
    reactions_response = client.reactions_get(channel=channel_id, timestamp=timestamp, full=True)
    reactions = reactions_response.get('message', {}).get('reactions', [])

    if not reactions:
        print("Aucune réaction trouvée pour ce message.")
        exit(0)

    # Préparer les données pour le CSV
    data_to_export = []

    # Compter les réactions
    reactions_count = {}

    # Parcourir chaque réaction et récupérer les informations des utilisateurs
    for reaction in reactions:
        # Compter les réactions
        reactions_count[reaction['name']] = len(reaction['users'])

        for user_id in reaction['users']:
            # Obtenir les informations de l'utilisateur
            user_info = client.users_info(user=user_id)

            if user_info['user']['profile'].get('email'):
                # Ajouter les informations dans la liste
                data_to_export.append([
                    user_id,
                    user_info['user']['name'],
                    user_info['user']['profile']['email'],
                    reaction['name']
                ])

    # Créer et écrire dans le fichier CSV
    with open('reactions.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['User ID', 'Username', 'Email', 'Reaction'])
        writer.writerows(data_to_export)

    print("Les données ont été exportées dans reactions.csv")

    # Afficher le décompte des réactions
    print("\nRéactions et leur nombre:")
    for reaction, count in reactions_count.items():
        print(f"{reaction}: {count}")

except SlackApiError as e:
    print(f"Slack API Error: {e.response['error']}")
