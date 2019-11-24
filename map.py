import gmplot

from data import Data, StopWithTime

MAX_WAIT = 60 * 5

class Map:
    def __init__(self):
        self.gmap = gmplot.GoogleMapPlotter(
            54.69236,
            25.28048,
            14,
            apikey='AIzaSyC0rVfYKZRxc_50TJnxLO7tz_P0YEjOZWA'
        )

    def draw_leg(self, start, end, color='#00f'):
        self.gmap.plot(
            [start.lat, end.lat],
            [start.lng, end.lng],
            color
        )

    def save(self):
        self.gmap.draw("stops.html")


if __name__ == "__main__":
    map = Map()
    data = Data()

    data.load("schedules.json")
    for _, l in data.legs.iterrows():
        map.draw_leg(l)

    map.save()