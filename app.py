from flask import Flask, request, jsonify, Response
from hotel import Hotel
from contacts import create_contact_for_resident, get_contacts, get_all_contacts

app = Flask(__name__)
hotel = Hotel()

# Get all contacts
@app.route('/contacts', methods=['GET'])
def get_all_contacts_route():
    all_contacts = get_all_contacts()
    
    return jsonify({'contacts': all_contacts}), 200

# Get a specific contact by resident's id
@app.route('/contacts/residents/<int:resident_id>', methods=['GET'])
def get_resident_contacts(resident_id):
    resident = hotel.get_resident_by_id(resident_id)
    if resident:
        resident_contacts = get_contacts(resident_id)
        
        if 'error' in resident_contacts:
            if '404 Client Error' in resident_contacts['error']:
                return jsonify({'error': 'ID not found in contacts'}), 404  
            else:
                return jsonify({'error': resident_contacts['error']}), 500
                
        return jsonify({'id': resident_id, 'contacts': resident_contacts}), 200
    return jsonify({'error': 'Resident not found'}), 404

# Add a contact - not specific to resident, only shown in "get all contacts"
@app.route('/contacts', methods=['POST'])
def create_contact_route():
    data = request.json
    required_fields = ['id', 'surname', 'name', 'number', 'email']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    response = create_contact_for_resident(data)
    if 'error' in response:
        return jsonify({'error': response['error']}), 500
    
    return response, 201
    
# Add contacts to a resident
@app.route('/contacts/residents/<int:resident_id>', methods=['POST'])
def add_resident_contact(resident_id):
    resident_data = hotel.get_resident_by_id(resident_id)
    if resident_data:
        name, surname = resident_data
        data = request.json

        data['id'] = resident_id
        data['name'] = name
        data['surname'] = surname
        
        response = create_contact_for_resident(data)
        
        if 'error' in response:
            return jsonify({'error': response['error']}), 500
            
        else:
            return jsonify({'message': f'Contact added successfully to resident {resident_id}'}), 201
            
    else:
        return jsonify({'error': 'Resident not found'}), 404

# Get residents
@app.route('/residents', methods=['GET'])
def get_residents_with_contacts():
    residents_with_contacts = []

    for resident in hotel.residents:
        contacts = get_contacts(resident.id)
        
        if 'error' in contacts:
            resident_info = {
                'id': resident.id,
                'name': resident.name,
                'surname': resident.surname,
                'contacts': 'not specified'
            }
        else:
            resident_info = {
                'contacts': contacts
            }
        
        residents_with_contacts.append(resident_info)

    return jsonify({'residents_with_contacts': residents_with_contacts}), 200

# Get rooms
@app.route('/rooms', methods=['GET'])
def get_rooms_info():
    rooms_data = [
        {
            'id': room.id,
            'name': room.room_name,
            'price': room.price,
            'size': room.size
        } 
        for room in hotel.rooms
    ]

    return jsonify({'rooms': rooms_data}), 200

# Get rooms by id
@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    room_name = hotel.get_room_name_by_id(room_id)

    if room_name:
        return jsonify({'room_name': room_name}), 200
    else:
        return jsonify({'error': 'Room not found'}), 404
        
# Get residents by id
@app.route('/residents/<int:resident_id>', methods=['GET'])
def get_resident_by_id(resident_id):
    resident = hotel.get_resident_by_id(resident_id)

    if resident:
        response_data = {
            'name': resident[0],
            'surname': resident[1],
        }
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Resident not found'}), 404

@app.route('/residents', methods=['POST'])
def add_resident():
    data = request.json
    name = data.get('name')
    surname = data.get('surname')
    room_id = data.get('room_id')

    # Check if the room has enough space
    room = next((room for room in hotel.rooms if room.id == room_id), None)
    if room:
        if len(room.lives_here) >= room.size:
            return jsonify({'error': 'Room is already full.'}), 422

        # Call method to add resident
        try:
            resident_id = hotel.move_in_new_resident(name, surname, room_id)

            response_data = {
                'message': f'Resident {resident_id} added to room {room_id} successfully'
            }
            return jsonify(response_data), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 404

    else:
        return jsonify({'error': f'Room with ID {room_id} not found'}), 404

@app.route('/rooms', methods=['POST'])
def add_room():
    data = request.json
    room_name = data.get('room_name')
    price = data.get('price')
    size = data.get('size')
    
    # Create a new room
    new_room = hotel.create_new_room(room_name, price, size)
    
    # Check if the new room was successfully created

    room_id = new_room.id
    message = 'Room added successfully'
        
    response_data = {
        'room_id': new_room.id,
        'message': message
    }
    return jsonify(response_data), 201

# Change a room's info
@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.json
    new_name = data.get('new_name')
    new_price = data.get('new_price')
    new_size = data.get('new_size')
    
    # Check if a person is assigned to the room
    person_in_room = hotel.get_person_in_room(room_id)
    if person_in_room:
        return jsonify({'error': f'A person is assigned to room with ID {room_id}. Cannot update details.'}), 422
    
    success = hotel.update_room(room_id, new_name, new_price, new_size)
    if success:
        return jsonify({'message': f'Room with ID {room_id} updated successfully'}), 200
    else:
        return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# Move a resident into a new room
@app.route('/residents/<int:resident_id>', methods=['PUT'])
def move_resident(resident_id):
    data = request.json
    new_room_id = data.get('new_room_id')
    
    # Extract room_id from data
    room_id = data.get('room_id')

    residents_in_room = hotel.get_specific_resident_in_room(resident_id, new_room_id)
    
    new_room = next((room for room in hotel.rooms if room.id == new_room_id), None)
    if not new_room:
        return jsonify({'error': 'Room not found with provided ID.'}), 404

    if residents_in_room:
        return jsonify({'error': f'Resident is already in room with ID {new_room_id}.'}), 409

    # Check if the new room is full
    if len(new_room.lives_here) >= new_room.size:
        return jsonify({'error': 'Room {new_room_id} is already full. Cannot add resident.'}), 422
    
    # Move the resident to the new room
    success = hotel.move_resident_into_room(resident_id, new_room_id)

    if success:
        return jsonify({'message': f'Resident {resident_id} moved to room {new_room_id} successfully'}), 200
    else:
        return jsonify({'error': 'Resident or room not found.'}), 404

# Remove a resident
@app.route('/residents/<int:resident_id>', methods=['DELETE'])
def remove_resident(resident_id):

    removal_result = hotel.remove_resident_from_room(resident_id)

    if removal_result:
        return '', 204
    else:
        return (
            jsonify({'error': f'Resident with ID {resident_id} '
                        'not found'}), 404
        )

# Remove a room
@app.route('/rooms/<int:room_id>', methods=['DELETE'])
def remove_room(room_id):
    if hotel.remove_room(room_id):
        return '', 204
    else:
        return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# See the entire hotel
@app.route('/')
def index():
    hotel_data = []

    for room in hotel.rooms:
        room_info = {
            'room_name': room.room_name,
            'price': room.price,
            'size': room.size,
            'residents': []
        }
        for resident in room.lives_here:
            resident_info = {
                'id': resident.id,
                'name': resident.name,
                'surname': resident.surname,
                'contacts': get_contacts(resident.id)
            }
            if 'error' in resident_info['contacts']:
                resident_info['contacts'] = 'Contact not added'
            room_info['residents'].append(resident_info)
        hotel_data.append(room_info)

    return jsonify({'hotel': hotel_data}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

