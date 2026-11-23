# Seismic Wave Arrival Simulator

A Python program that reads real earthquake data from the USGS earthquake catalog and estimates when the first seismic wave (the P-wave) from each earthquake would reach a set of cities in western Canada.

For each earthquake, the stations are kept in a linked list sorted by arrival time, so the program shows the order in which each city would detect the earthquake.

## Example output

```
M4.2  off the coast of Oregon
  1. Vancouver      716 km   P-wave arrives after 1 min 29 s
  2. Calgary       1321 km   P-wave arrives after 2 min 45 s
  3. Edmonton      1517 km   P-wave arrives after 3 min 09 s
  4. Saskatoon     1831 km   P-wave arrives after 3 min 48 s
```

## How it works

1. Reads earthquakes (location, depth, magnitude) from a CSV file exported from the [USGS earthquake search](https://earthquake.usgs.gov/earthquakes/search/).
2. Calculates the distance from each earthquake to each station using the haversine (great-circle) formula.
3. Estimates travel time as distance ÷ average P-wave speed (8 km/s).
4. Inserts each station into a linked list sorted by arrival time.
5. Prints the largest earthquakes within 3,000 km of a station, with stations in order of arrival.

## Running it

Requires Python 3 and no extra packages.

1. Put `seismic_arrivals.py` and `query.csv` in the same folder.
2. Run `python seismic_arrivals.py`.

To use newer data, download a fresh CSV from the USGS earthquake search and save it as `query.csv`.

## Simplifications

This is a learning project, not a scientific tool:

- The P-wave is assumed to travel at one constant speed. Real seismic waves speed up with depth, so real arrival times differ.
- Distance is measured along the Earth's surface and ignores the earthquake's depth.
- Cities stand in for real seismograph stations.

## Background

The linked list and sorted-insert logic are adapted from my data structures coursework (CMPUT 175, University of Alberta). I built this project to practise working with real geophysical data in Python.

Earthquake data: U.S. Geological Survey (USGS) Earthquake Hazards Program.
