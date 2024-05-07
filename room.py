class Room:
	static_room_id = 1

	def __init__(self, room_name, price, size, lives_here=None):
		if lives_here is None:
			lives_here = []
            
		# Automatic ID assignment to room
		self.id = Room.static_room_id
		Room.static_room_id += 1
        
		self.room_name = room_name
		self.price = price
		self.size = size
		self.lives_here = lives_here

	def __dict__(self):
		return {
			'Room ID': self.id, 
			'Room name': self.room_name,
			'Price': self.price,
			'Size': self.size,
			'Residents': self.lives_here
		}

