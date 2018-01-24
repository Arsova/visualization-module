import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='')

with open('coordinates-codes.csv', 'w') as outfile:
    with open('postcodes.txt', 'r') as infile:
        for line in infile:
            line = line.strip('\n')
            geocode_result = gmaps.geocode(line)
            location = geocode_result[0]['geometry']['location']
            new_line = str(line) + ',' + str(location['lat']) + ',' + str(location['lng']) + '\n'
            outfile.write(new_line)
