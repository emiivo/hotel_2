# hotel_2
A simple hotel service built using Python and Docker.
This project expands the functionality of the first web service by adding contact management for residents, utilizing another student's assignment for contact handling.
# Usage:

Launch:

```git clone --recurse https://github.com/emiivo/hotel_2.git```

```cd hotel_service```

```docker-compose up```


# NEW FUNCTIONS WITH CONTACTS:

# Get residents and their contacts:

```curl http://localhost:80/residents```

# Add contacts to a resident:

```curl -X POST -H "Content-Type: application/json" -d '{"number": "123456789", "email": "john@example.com"}' http://localhost:80/contacts/residents/1```

# Get a specific contact by resident's id:

```curl -X GET http://localhost:80/contacts/residents/1```

# See the entire hotel - with contacts:

```curl http://localhost:80/```

# CREATE:

Add a resident. Only works when the room capacity is not at the limit.

```curl -X POST -H "Content-Type: application/json" -d '{"name": "New", "surname": "Resident", "room_id": 3}' http://localhost:80/residents```

Create a new room.

```curl -X POST -H "Content-Type: application/json" -d '{"room_name": "New room", "price": 100, "size": 2}' http://localhost:80/rooms```


# READ:

Rooms:

```curl http://localhost:80/rooms```

Residents - now with contacts:

```curl http://localhost:80/residents```

Room name by id:

```curl http://localhost:80/rooms/3```

Resident name and surname by id:

```curl http://localhost:80/residents/3```

# UPDATE:

Update room info - name, price, size:

```curl -X PUT -H "Content-Type: application/json" -d '{"new_name": "Changed room", "new_price": 1000, "new_size": 5}' http://localhost:80/rooms/3```

Update resident info - move to another room:

```curl -X PUT -H "Content-Type: application/json" -d '{"new_room_id": 3}' http://localhost:80/residents/1```


# DELETE:

Remove a room and its residents (number at the end is room id):

```curl -X DELETE http://localhost:80/rooms/1```

Remove a resident from a room (number at the end is resident id):

```curl -X DELETE http://localhost:80/residents/1```





