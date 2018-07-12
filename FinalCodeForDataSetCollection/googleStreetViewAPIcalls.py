import streetview

def getPointsOfInterest(pos):

    usedIDs = []
    pointOfInterest = []

    for i in range(len(pos)):
        lat = pos[i, 0]
        lon = pos[i, 1]
        panoids = streetview.panoids(lat, lon)

        for panoid in panoids:
            if 'year' in panoid:
                id = panoid['panoid']
                if id not in usedIDs:
                    usedIDs.append(id)
                    pointOfInterest.append(panoid)

    return pointOfInterest
