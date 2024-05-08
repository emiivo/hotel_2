from flask import Flask, request, jsonify, Response
from hotel import Hotel
from contacts import create_contact_for_resident, get_contacts, get_all_contacts

app = Flask(__name__)
hotel = Hotel()

# Get all contacts
@app.route('/contacts', methods=['GET'])
def get_all_contacts_route():
    all_contacts = get_all_contacts()
    
    return jsonify({'contacts': all_contacts})

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
                
        return jsonify({'id': resident_id, 'contacts': resident_contacts})
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
            return jsonify({'message': 'Contact added successfully'}), 201
            
    else:
        return jsonify({'error': 'Resident not found'}), 404

# Get residents and their contacts
@app.route('/contacts/residents', methods=['GET'])
def get_residents_with_contacts():
    residents_with_contacts = []

    for resident in hotel.residents:
        resident_info = {
            'id': resident.id,
            'name': resident.name,
            'surname': resident.surname,
            'contacts': []
        }
        contacts = get_contacts(resident.id)
        if 'error' in contacts:
            resident_info['contacts'] = {'error': 'No contacts specified'}
        else:
            resident_info['contacts'] = contacts
        residents_with_contacts.append(resident_info)

    return jsonify({'residents_with_contacts': residents_with_contacts})

# Get residents
@app.route('/residents', methods=['GET'])
def get_residents_info():
    residents_data = [
        {
            'id': resident.id,
            'name': resident.name,
            'surname': resident.surname
        } 
        for resident in hotel.residents
    ]

    return jsonify({'residents': residents_data})
    


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

    return jsonify({'rooms': rooms_data})

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
			return jsonify({'error': 'Room is already full.'}), 400

		# Call method to add resident
		try:
			success = hotel.move_in_new_resident(name, surname, room_id)
			# Construct response with added resident information
			response_data = {
				'resident': {
					'name': name,
					'surname': surname,
					'room_id': room_id
				},
				'message': 'Resident added to room successfully'
			}
			return jsonify(response_data), 200
		except ValueError as e:
			return jsonify({'error': str(e)}), 404
    
	else:
		return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# Add a room
@app.route('/rooms', methods=['POST'])
def add_room():
    data = request.json
    room_name = data.get('room_name')
    price = data.get('price')
    size = data.get('size')

    hotel.create_new_room(room_name, price, size)

    return jsonify({'message': 'New room added'})

# Change a room's info
@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.json
    new_name = data.get('new_name')
    new_price = data.get('new_price')
    new_size = data.get('new_size')
    
    person_in_room = hotel.get_resident_by_id(room_id)
    
    # Check if a person is assigned to the room
    if person_in_room:
        return jsonify({'error': f'A person is assigned to room with ID {room_id}. Cannot update details.'}), 400
    
    success = hotel.update_room(room_id, new_name, new_price, new_size)
    if success:
        return jsonify({'message': 'Room updated successfully'}), 200
    else:
        return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# Change a resident's info
@app.route('/residents/<int:resident_id>', methods=['PUT'])
def move_resident(resident_id):
    data = request.json
    new_room_id = data.get('new_room_id')

    new_room = next((room for room in hotel.rooms if room.id == new_room_id), None)
    if not new_room:
        return jsonify({'error': 'Room not found with provided ID.'}), 404

    if len(new_room.lives_here) >= new_room.size:  
        return jsonify({'error': 'Room is already full. Cannot add resident.'}), 400
        
    for room in hotel.rooms:
        if resident_id in room.lives_here:  
            return jsonify({'error': 'Resident is already in the new room.'}), 400

    success = hotel.move_resident_into_room(resident_id, new_room_id)

    if success:
        return jsonify({'message': 'Resident moved to new room successfully'}), 200
    else:
        return jsonify({'error': 'Resident or room not found.'}), 404

# Remove a resident
@app.route('/residents/<int:resident_id>', methods=['DELETE'])
def remove_resident(resident_id):

    removal_result = hotel.remove_resident_from_room(resident_id)

    if removal_result:
        return jsonify({'message': 'Resident removed from room successfully'}), 200
    else:
        return (
            jsonify({'error': f'Resident with ID {resident_id} '
                        'not found'}), 404
        )

# Remove a room
@app.route('/rooms/<int:room_id>', methods=['DELETE'])
def remove_room(room_id):
    if hotel.remove_room(room_id):
        return jsonify({'message': f'Room with ID {room_id} '
                            'and its residents removed successfully'}), 200
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

    return jsonify({'hotel': hotel_data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

