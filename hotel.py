import room as room
import resident as resident

class Hotel:
	def __init__(self):
		# Initial Data
		room1 = room.Room("Standard room", 50, 2)
		room2 = room.Room("Better room", 80, 2)
		room3 = room.Room("Largest room", 120, 4)


		# Fields
		self.rooms = [room1, room2, room3]
		self.residents = []
		
		# Add residents to rooms
		self.move_in_new_resident(name="Mike", surname="Smith", room_id=1)
		self.move_in_new_resident(name="Ana", surname="Smith", room_id=1)
		self.move_in_new_resident(name="Karen", surname="Jones", room_id=2)
		self.move_in_new_resident(name="Don", surname="Jones", room_id=2)

	def move_in_new_resident(self, name, surname, room_id):
		# Create a new resident
		new_resident = resident.Resident(name, surname)

		# Find the room by ID
		room = next(
			(room for room in self.rooms if room.id == room_id),
			None
		)

		# If the room exists, add the new resident to it
		if room:
			room.lives_here.append(new_resident)
			new_resident.occupied_room = room
			self.residents.append(new_resident)
			return True
		else:
			raise ValueError(f'Room with ID {room_id} not found.')


	def create_new_room(self, room_name, price, size):
		new_room = room.Room(room_name, price, size)
		self.rooms.append(new_room)

	def get_room_name_by_id(self, id):
		room = next(
			(room for room in self.rooms if room.id == id),
			None
		)
		if room:
			return room.room_name
		else:
			return False

	def get_resident_by_id(self, id):
		resident = next(
			(resident for resident in self.residents if resident.id == id),
			None
		)
		if resident:
			return resident.name, resident.surname
		else:
			return False

	def update_room(self, room_id, new_name=None, new_price=None, new_size=None):
		room = next(
			(room for room in self.rooms if room.id == room_id),
			None
		)
		if room:
			if new_name is not None:
				room.room_name = new_name
			if new_price is not None:
				room.price = new_price
			if new_size is not None:
				room.size = new_size
			return True
		else:
			return False

	def move_resident_into_room(self, resident_id, new_room_id):
		# Find the resident and both the old and new rooms by ID
		resident = next(
			(resident for resident in self.residents if resident.id == resident_id),
			None
		)
		old_room = next(
			(room for room in self.rooms if resident in room.lives_here),
			None
		)
		new_room = next(
		(room for room in self.rooms if room.id == new_room_id),
		None
		)

		if resident and old_room and new_room and new_room != old_room:
			old_room.lives_here.remove(resident) 
			new_room.lives_here.append(resident)
			resident.occupied_room = new_room
			return True
		else:
			return False

		
	def remove_room(self, room_id):
		# Find the room by ID
		room = next(
			(room for room in self.rooms if room.id == room_id),
			None
		)

		# If the room exists, remove it and its residents
		if room:
			self.rooms.remove(room)
			self.residents = [
				resident
				for resident in self.residents
				if resident.occupied_room != room
			]
			return True
		else:
			return False

	def remove_resident_from_room(self, resident_id):
		# Find the resident by ID
		resident = next(
			(resident for resident in self.residents if resident.id == resident_id),
			None
		)

		# If the resident exists, remove them from their room 
		# from the list of residents in the hotel
		if resident:
			if resident.occupied_room:
				resident.occupied_room.lives_here.remove(resident)
				resident.occupied_room = None
				self.residents.remove(resident)
			return True
		else:
			return False
