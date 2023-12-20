from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import dotenv_values
from colorama import Fore

def connect_to_database():
    # Load MongoDB URI from the .env file using dotenv
    config = dotenv_values('.env')
    MONGO_URI = config['MONGO_URI']
    
    try:
        # Attempt to establish a connection to the MongoDB server
        client = MongoClient(MONGO_URI)
        
        # Check if the connection is successful by calling server_info()
        client.server_info()
        
        # Print a success message if the connection is established
        print(Fore.GREEN + '[+] Connected to MongoDB successfully.')
        
        # Return the MongoDB client object for use in other functions
        return client
    except ConnectionFailure:
        # Handle the case where a connection failure occurs
        print(Fore.RED + '[-] Failed to connect to MongoDB.')
        
        # Exit the program with an error code (1) to indicate the failure
        exit(1)

def post_data(client, data):
    try:
        # Get the 'repacksdb' database from the MongoDB client
        db = client['repacksdb']

        # Get the 'repacks' collection from the database
        collection = db['repacks']

        # Check if a document with the same URL already exists in the collection
        existing_document = collection.find_one({'url': data['url']})

        if existing_document:
            # If a document with the same URL exists, update it with the new data
            collection.update_one({'url': data['url']}, {'$set': data})
            print(Fore.GREEN + '[+] Updated document with URL:', data['url'])
        else:
            # If the URL doesn't exist in the collection, insert a new document
            collection.insert_one(data)
            print(Fore.GREEN + '[+] Inserted new document with URL:', data['url'])

        return True
    except Exception as e:
        # Handle exceptions and print an error message if data posting fails
        print(Fore.RED + '[-] Failed to post data to MongoDB: ' + str(e))
        return False

