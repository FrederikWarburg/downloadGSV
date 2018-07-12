from googleplaces import GooglePlaces
import gmplot
import numpy as np
import matplotlib.pyplot as plt
from pathEstimation import getGeoCoord
import googlemaps

from helpers import measure

def generateRoutes(chains,lat,lon, apiKey):
    #chains = ["mcdonalds", "burger king","cinemas"]

    pos =[]

    for i, chain in enumerate(chains):

        google_places = GooglePlaces(apiKey)

        query_result = google_places.nearby_search(
                lat_lng={'lat': lat, 'lng': lon},
                radius=5000,
                keyword= chain)

        places = query_result.places

        for place in places:
            place = str(place)
            latPos = place.find("lat=")
            lonPos = place.find("lng=")
            lat = np.float64(place[latPos+4:latPos+12])
            lon = np.float64(place[lonPos+4:lonPos+12])
            #gmap.scatter([lat], [lon], color=colors2[i], edge_width=10)
            pos.append([lat,lon])

    return pos

"""
for i, pos1 in enumerate(pos):

    for j, pos2 in enumerate(pos):
        if i != j:

            # Open Google Maps with API Key
            gmaps = googlemaps.Client(key=apiKey)

            # Request directions via car
            directions_result = gmaps.directions(pos1, pos2, mode="walking")  # mode = driving

            # Get geo coordinates from directions
            lats, lons, distance = getGeoCoord(directions_result)
            totalDistance += distance
            if distance > 1000: # addresses has to be minimum 1km from each other.

                plt.plot(lats,lons,'.')
                for i in range(len(lats)):

                    lat = lats[i]
                    lon = lons[i]

                    routes.append(np.array([lat,lon]))

    print(i,len(pos1))

routes = np.array(routes)

"""