"""
Seismic Wave Arrival Simulator
Author: Nsikan-Abasi Mfon Akpan

This program reads real earthquake data whicbh I got from the from the USGS earthquake catalog (CSV export) and
estimates when the first seismic wave (P-wave) from each earthquake would reach
a set of Canadian cities used as stand-in seismograph stations.

For each earthquake, the stations are stored in a linked list kept sorted according to
arrival time, so walking the list gives the order in which the stations would
detect the earthquake.

I built this program with the concepts I learned in my CMPUT 175 class at the University of Alberta.
It mostly focuses on the linked list topic.

Simplifications (this is a teaching model, not a real seismic tool):
  - Distance is the straight great-circle distance along the Earth's surface.
  - The P-wave travels at one constant average speed (8 km/s). Real waves
    speed up as they travel deeper into the Earth, so real arrival times would differ.
  - Only earthquakes within MAX_DISTANCE_KM of the nearest station are used,
    because the larger the distance the less accurate the constant-speed model.
"""

import csv
import math

DATA_FILE = "query.csv"
P_WAVE_SPEED_KM_S = 8.0      # average P-wave speed used for the whole path
EARTH_RADIUS_KM = 6371.0
MAX_DISTANCE_KM = 3000.0     # ignore earthquakes farther than this from every station
NUM_TO_SHOW = 5              # how many of the largest nearby earthquakes to print

# Cities used as stand-in seismograph stations: (name, latitude, longitude)
STATIONS = [
    ("Whitehorse", 60.72, -135.06),
    ("Vancouver", 49.28, -123.12),
    ("Calgary", 51.05, -114.07),
    ("Edmonton", 53.55, -113.49),
    ("Saskatoon", 52.13, -106.67),
    ("Regina", 50.45, -104.61),
    ("Winnipeg", 49.90, -97.14),
]



# Linked list (from my CMPUT 175 coursework, with the sorted insert adapted)

class Node:
    def __init__(self, init_data, init_next=None):
        self.data = init_data
        self.next = init_next

    def getData(self):
        return self.data

    def getNext(self):
        return self.next

    def setNext(self, new_next):
        self.next = new_next


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def isEmpty(self):
        return self.head is None

    def length(self):
        return self.size

    def __iter__(self):
        cur = self.head
        while cur is not None:
            yield cur.getData()
            cur = cur.getNext()

    def insert_sorted_by_arrival(self, arrival):
        # keep list sorted by arrival time (earliest first)
        new_node = Node(arrival)

        # empty list
        if self.head is None:
            self.head = new_node
            self.size = 1
            return

        # goes before head
        if arrival.travel_time_s < self.head.getData().travel_time_s:
            new_node.setNext(self.head)
            self.head = new_node
            self.size += 1
            return

        # otherwise walk to the right spot
        prev = None
        cur = self.head
        while cur is not None and cur.getData().travel_time_s <= arrival.travel_time_s:
            prev = cur
            cur = cur.getNext()

        prev.setNext(new_node)
        new_node.setNext(cur)
        self.size += 1


# ---------------------------------------------------------------------------
# Earthquake data
# ---------------------------------------------------------------------------

class Earthquake:
    def __init__(self, time, latitude, longitude, depth_km, magnitude, place):
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.depth_km = depth_km
        self.magnitude = magnitude
        self.place = place


class Arrival:
    # one station's arrival for one earthquake
    def __init__(self, station_name, distance_km, travel_time_s):
        self.station_name = station_name
        self.distance_km = distance_km
        self.travel_time_s = travel_time_s


def distance_km(lat1, lon1, lat2, lon2):
    # great-circle distance between two points (haversine formula)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def load_earthquakes(filename):
    # read the USGS CSV export into a list of Earthquake objects
    quakes = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] != "earthquake" or row["mag"] == "":
                continue
            quakes.append(Earthquake(
                time=row["time"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                depth_km=float(row["depth"]) if row["depth"] else 0.0,
                magnitude=float(row["mag"]),
                place=row["place"],
            ))
    return quakes


def compute_arrivals(quake):
    # build a linked list of station arrivals, sorted earliest first
    arrivals = LinkedList()
    for name, lat, lon in STATIONS:
        d = distance_km(quake.latitude, quake.longitude, lat, lon)
        t = d / P_WAVE_SPEED_KM_S
        arrivals.insert_sorted_by_arrival(Arrival(name, d, t))
    return arrivals


def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes} min {secs:02d} s"


def main():
    quakes = load_earthquakes(DATA_FILE)
    print(f"Loaded {len(quakes)} earthquakes from {DATA_FILE}")

    # keep only earthquakes close enough for the simple model
    nearby = []
    for q in quakes:
        arrivals = compute_arrivals(q)
        nearest = arrivals.head.getData()     # list is sorted, so head is nearest
        if nearest.distance_km <= MAX_DISTANCE_KM:
            nearby.append((q, arrivals))

    print(f"{len(nearby)} are within {MAX_DISTANCE_KM:.0f} km of a station\n")

    # show the largest nearby earthquakes
    nearby.sort(key=lambda pair: pair[0].magnitude, reverse=True)
    for q, arrivals in nearby[:NUM_TO_SHOW]:
        print("=" * 60)
        print(f"M{q.magnitude}  {q.place}")
        print(f"Time (UTC): {q.time[:19].replace('T', ' ')}   Depth: {q.depth_km:.0f} km")
        print("-" * 60)
        order = 1
        for a in arrivals:
            print(f"  {order}. {a.station_name:<11} {a.distance_km:6.0f} km   "
                  f"P-wave arrives after {format_time(a.travel_time_s)}")
            order += 1
        print()


if __name__ == "__main__":
    main()