import json
import pandas as pd
from types import SimpleNamespace
from typing import Tuple, List


class Stop(SimpleNamespace):
    id: str
    nr: int
    name: str
    lat: float
    lng: float


class StopWithTime(Stop):
    time: int
    bus: str


class Leg(SimpleNamespace):
    start: Stop
    end: Stop
    start_time: int
    end_time: int


class Data:
    stops_id: Tuple[str, Stop]
    stops_nr: List[Stop]
    legs: pd.DataFrame

    def load(self, filename: str):
        with open(filename, 'rb') as json_file:
            j = json.load(json_file)

        self.stops_id = {}
        self.stops_nr = []
        for s in j['stops']:
            stop = Stop(
                id = s['id'],
                nr = len(self.stops_nr),
                name = s['name'],
                lat = s['location']['lat'],
                lng = s['location']['lng']
            )
            self.stops_id[s['id']] = stop
            self.stops_nr.append(stop)

        legs = []
        for s in j['schedules']:
            for t in s['tracks']:
                for departure in t['departures']:
                    start: Stop = None
                    prev_ride_time = None
                    for ss in t['stops']:
                        end: Stop = self.stops_id[ss['id']]
                        ride_time: int = ss['rideTime']

                        if start is not None:
                            end_time = departure + ride_time
                            duration = ride_time - prev_ride_time
                            start_time = end_time - duration

                            leg = [
                                s['name'],
                                start_time, start.nr, start.lat, start.lng,
                                end_time, end.nr, end.lat, end.lng
                            ]
                            legs.append(leg)

                        start = end
                        prev_ride_time = ride_time

        df = pd.DataFrame(legs, columns=[
            'bus',
            'start_time', 'start_nr', 'start_lat', 'start_lng',
            'end_time', 'end_nr', 'end_lat', 'end_lng'
        ])
        # df.drop_duplicates(inplace=True)
        self.legs = df

    def get_stop_with_time(self, time: int, nr: int, bus: str = None):
        stop = self.stops_nr[nr]
        return StopWithTime(
            time = time,
            bus = bus,
            id = stop.id,
            nr = stop.nr,
            name = stop.name,
            lat = stop.lat,
            lng = stop.lng,
        )

if __name__ == "__main__":
    data = Data()
    data.load("schedules.json")
    print(data.legs.query(f'''
        start_nr==110 and 
        start_time >= 35940
    '''.replace('\n', '')).sort_values(
        by=['start_time']
    ))

