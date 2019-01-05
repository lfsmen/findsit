# findsit
Findsit - Seat sensor

Small project where the purpose is to build a seat occupancy sensor using a raspberry PI and RF tags.

# difficulties / how to do it's
- Communication between IOT sensors and Raspberry Pi
How to I create a constant communication between the sensors and the raspberry pi? and how can my programming language interpret the results?

# guiding principles - gateway

- Real-time communication with a device that returns 0 or 1.
  - To do this, constantly look for signal
- Spatial location of all such devices in an area.
  - Previous mapping is needed - create an occupancy matrix with MxN, that represents an area in m2
  - Scan each device and tag it
- Heatmap production
  - When device is 1, the table is taken; when device is 0, the table is not taken
- Displaying the information
  - Display a matrix with blank spaces, 0's and 1's that represent a table, occupied or not.

# guiding principles - sensor pairing
- RF tags under seat, with a piezoelectric sensor.
- When pressure is effected on the seat, the RF tag triggers and communicates with the closest table.
- When a table receives a communication from a seat, it changes its state to 1.
- A table is in the '1' state for as long as a seat is under pressure.


# algorithm - heatmap

for each sensor in the area matrix
  read state
  if state = 1
    activated
  else if state = 0
    deactivated
  endif.
endfor.

read area matrix and display occupancy

# algorithm - read state

communicate with table sensors (wifi)
  read tag
  read state
end communication

# algorithm - event reader

read event
  if "activated"
    - analytics information regarding state activation
  if "deactivated"
    - analytics information regarding state deactivation
store event log
