import slack_sdk
import os
import csv
import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Créer un client Slack avec votre token OAuth
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
client = slack_sdk.WebClient(token=slack_bot_token)

# Lister tous les canaux disponibles
try:
    channels_response = client.conversations_list()
    channels = channels_response["channels"]

    for index, channel in enumerate(channels):
        print(f"{index + 1}. {channel['name']} (ID: {channel['id']})")

    # Demander à l'utilisateur de choisir un canal
    choice = int(input("Choisissez un canal (entrez le numéro) : "))
    channel_id = channels[choice - 1]['id']

    # Demander combien de jours en arrière récupérer les messages
    days_back = int(input("Combien de jours en arrière voulez-vous récupérer les messages ? "))
    oldest = datetime.datetime.now() - datetime.timedelta(days=days_back)
    oldest_timestamp = oldest.timestamp()

    # Récupérer les messages dans cet intervalle
    messages_response = client.conversations_history(channel=channel_id, oldest=oldest_timestamp)
    messages = messages_response['messages']

    for index, message in enumerate(messages):
        preview = message['text'][:140] + '...' if len(message['text']) > 50 else message['text']
        print(f"{index + 1}. {preview} (Timestamp: {message['ts']})")

    # Demander à l'utilisateur de choisir un message
    message_choice = int(input("Choisissez un message (entrez le numéro) : "))
    selected_message = messages[message_choice - 1]
    message_timestamp = selected_message['ts']

    # Récupérer les réactions pour ce message
    reactions_response = client.reactions_get(channel=channel_id, timestamp=message_timestamp)

    # Préparer les données pour le CSV
    data_to_export = []

    # Parcourir chaque réaction et récupérer les informations des utilisateurs
    for reaction in reactions_response['message']['reactions']:
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
        writer.writerow(['User ID', 'Alias', 'Email', 'Reaction'])
        writer.writerows(data_to_export)

    print("Les données ont été exportées dans reactions.csv")

except Exception as e:
    print(f"Erreur lors de la récupération des informations : {e}")
