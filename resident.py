class Resident:
	static_person_id = 1

	def __init__(self, name, surname):
		# Automatic ID assignment to Resident
		self.id = Resident.static_person_id
		Resident.static_person_id += 1
        
		self.name = name
		self.surname = surname
		self.occupied_room = None

	def __dict__(self):
		return {
		'Person ID': self.id, 
		'Person name': self.name,
		'Person surname': self.surname,
		'Occupied room': self.occupied_room.room_name if self.occupied_room else None
	}
