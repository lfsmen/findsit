# findsit
Findsit - Seat sensor

Small project where the purpose is to build a seat occupancy sensor using a raspberry PI and RF tags.

# guiding principles - gateway

- Real-time Communication with a device that returns 0 or 1.
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
