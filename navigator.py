from datetime import timedelta
from typing import List, Optional
import pandas as pd
import pickle

from data import Data, StopWithTime
from map import Map

MAX_WAIT = 60 * 20

class Navigator:
    data: Data
    legs: pd.DataFrame

    def __init__(self):
        self.data = Data()
        self.data.load("schedules.json")
        self.legs = self.data.legs
        self.cache = {}
        self.map = Map()

    def find(self, time: int, start_nr: int, end_nr: int, max_time: int, depth=0) -> Optional[List[StopWithTime]]:
        key = '|'.join([str(int(time / 60)), str(start_nr), str(end_nr)])
        if key in self.cache:
            return self.cache[key]

        print('find', time, start_nr, end_nr, len(self.cache))

        if start_nr == end_nr or depth > 18:
            return []

        legs = self.legs.query(f'''
            start_nr=={start_nr} and 
            start_time >= {time} and 
            start_time <= {time + MAX_WAIT} and
            end_time <= {max_time}
        '''.replace('\n', ''))

        dest = self.data.stops_nr[end_nr]
        legs['distance'] = (legs.end_lat - dest.lat) * (legs.end_lat - dest.lat) + (legs.end_lng - dest.lng) * (legs.end_lng - dest.lng)
        legs.sort_values(by=['distance'])

        # print(legs)

        best_route = []
        best_time = max_time

        for _, l in legs.iterrows():
            start = self.data.get_stop_with_time(l.start_time, l.start_nr, l.bus)
            end = self.data.get_stop_with_time(l.end_time, l.end_nr, l.bus)

            # self.map.draw_leg(start, end)

            route = [start, end]
            if end.nr == end_nr:
                self.cache[key] = route
                finish_time = route[-1].time
                if finish_time < best_time:
                    best_route = route
                    best_time = finish_time
                continue

            rest = self.find(l.end_time, l.end_nr, end_nr, best_time, depth+1)
            if len(rest) > 0:
                route.extend(rest)
                finish_time = route[-1].time
                if finish_time < best_time:
                    best_route = route
                    best_time = finish_time

        self.cache[key] = best_route
        return best_route

    def print_route(self, stops: List[StopWithTime], start_time: int):
        print()
        prev_stop = None
        prev_time = None
        for stop in stops:
            if stop.time != prev_time:
                print(stop.bus, timedelta(seconds=int(stop.time)), stop.name, " \t\t\t", stop.id, stop.nr, stop.time)

            if prev_stop:
                self.map.draw_leg(prev_stop, stop, '#f00')

            prev_stop = stop
            prev_time = stop.time

        duration = timedelta(seconds=stops[-1].time - start_time)
        print(duration)


if __name__ == "__main__":
    navigator = Navigator()
    with open('cache.pkl', 'rb') as handle:
        navigator.cache = pickle.load(handle)

    start = navigator.data.stops_id['vln_0711']
    end = navigator.data.stops_id['vln_0216']

    timestr = '13:30:00'
    start_time = sum([a * b for a, b in zip([3600, 60, 1], map(int, timestr.split(':')))])

    max_time = start_time + 60 * 60 * 2 # 2 hours
    route = navigator.find(start_time, start.nr, end.nr, max_time)

    if route:
        navigator.print_route(route, start_time)

    navigator.map.save()

    with open('cache.pkl', 'wb') as handle:
        pickle.dump(navigator.cache, handle)

