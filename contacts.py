import requests

CONTACTS_URL = 'http://contacts:5000'

def get_all_contacts():
    try:
        response = requests.get(f'{CONTACTS_URL}/contacts')
        response.raise_for_status()
        all_contacts = response.json()
        return all_contacts
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch contacts: {e}'}
    except Exception as e:
        return {'error': f'An unexpected error occurred: {e}'}

def get_contacts(cont_id):
    try:
        response = requests.get(f'{CONTACTS_URL}/contacts/{cont_id}')
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch contact from Java API: {e}'}
    except Exception as e:
        return {'error': f'An unexpected error occurred: {e}'}
        

def create_contact_for_resident(contact_data):
    try:
        response = requests.post(f'{CONTACTS_URL}/contacts', json=contact_data)
        
        if response.status_code == 201:
            return {'message': 'Contact created successfully'}
        else:
            return {'error': 'Failed to create contact'}
            
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to create contact through Java API: {e}'}
