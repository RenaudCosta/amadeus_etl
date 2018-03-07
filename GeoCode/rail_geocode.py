# -*- coding: utf-8 -*-

"""
@author: sraghunathan
05-Jun-2016
"""

import googlemaps
import logging
import codecs
from rail_country_codes import RailCountryCodes as rcc
from geocoder.distance import Distance
import datetime


class RailStationsReader:
    def __init__(self, file_name, mode, provider, encoding="utf-8"):
        self.data = []
        self.file_name = file_name
        if provider == "SWP":
            self.__readfileSWP(file_name, mode, encoding)

    def __readfileSWP(self, file_name, mode, encoding):
        self.data = (l.rstrip().split('\t') for l in codecs.open(file_name, mode, encoding))


class RailGeoCode(object):
    def __init__(self, file_name, identifier, append_country=True, append_station=True):

        logging.basicConfig(level=logging.DEBUG, filename='log/stations_' + identifier + '.log')
        logging.FileHandler('log/stations_' + identifier + '.log', encoding='utf-8')
        logging.info("file_name: {}".format(file_name))
        logging.info("append_country: {}".format(append_country))
        logging.info("append_station: {}".format(append_station))
        logging.info("identifier: {}".format(identifier))

        self.append_country = append_country
        self.append_station = append_station
        self.identifier = identifier

        self.stations_input = RailStationsReader(file_name, 'rU', 'SWP')

        self.stations_output_resolved = open('output/stations_resolved_' + self.identifier + '.csv', 'w+')
        self.stations_output_unresolved = open('output/stations_unresolved_' + self.identifier + '.csv',
                                               'w+')

        self.stations = self.stations_input.data
        self.maps = googlemaps.Client(key='AIzaSyA1KFYBmeoBS1oW8wCvHJVBrdYLu69q7xU')

        self.sign = {
            "S": -1,
            "W": -1,
            "N": 1,
            "E": 1
        }

        self.__enrich_geo_codes()

    def __del__(self):
        self.stations_output_resolved.close()
        self.stations_output_unresolved.close()

    def dms2dec(self, geocode):
        degrees, minutes, seconds = float(geocode[:-5]), float(geocode[-5:-3]), float(geocode[-3:-1])
        return self.sign[geocode[-1]] * (degrees + minutes / 60 + seconds / 3600)

    def dec2dms(self, deg, geo_type):
        d = int(deg)
        md = abs(deg - d) * 60
        m = int(md)
        sd = (md - m) * 60
        if geo_type == 'lat':
            hemisphere = "N" if deg > 0 else "S"
        else:
            hemisphere = "E" if deg > 0 else "W"
        return str(abs(d)).rjust(2, '0') + str(m).rjust(2, '0') + str(int(sd)).rjust(2, '0') + hemisphere

    def __get_confidence(self, geocode):
        """
            Units are measured in Kilometers
        """
        northeast_geo = (geocode['geometry']['bounds']['northeast']['lat'],
                         geocode['geometry']['bounds']['northeast']['lng'])

        southwest_geo = (geocode['geometry']['bounds']['southwest']['lat'],
                         geocode['geometry']['bounds']['southwest']['lng'])
        if northeast_geo and southwest_geo:
            distance = Distance(northeast_geo, southwest_geo, units='km')
            for score, maximum in [(10, 0.25),
                                   (9, 0.5),
                                   (8, 1),
                                   (7, 5),
                                   (6, 7.5),
                                   (5, 10),
                                   (4, 15),
                                   (3, 20),
                                   (2, 25)]:
                if distance < maximum:
                    logging.debug("Distance: {}".format(distance))
                    logging.debug("Confidence Level: {}".format(score))
                    return score
                if distance >= 25:
                    logging.debug("Distance: {}".format(distance))
                    logging.debug("Confidence Level: {}".format(1))
                    """Cannot determine score"""
                    return 1

        return 0

    def __write_to_resolved_stations(self, csv_line):
        self.stations_output_resolved.write(str(csv_line))

    def __write_to_unresolved_stations(self, station, geocode={}):
        record = []
        record.extend([station[0], station[1], str(geocode.get('lat', "")), str(geocode.get('lng', ""))])
        csv_line = '|'.join(record) + '\n'
        print ("Station Un resolved or not accurate")
        self.stations_output_unresolved.write(str(csv_line))

    def __enrich_geo_codes(self):
        count = 1
        for station in self.stations:
            print (station[0], " - ", station[1])
            self.__fetch_google_geo_codes(station)
            count += 1
            continue

    def __prepare_line_for_insert(self, result, station, geocode={}):
        logging.debug("Preparing the  line for insert")
        postal_code = None
        country_code = None
        for each in result.get('address_components'):
            if 'postal_code' in each.get('types'):
                postal_code = each.get('long_name')
            if 'country' in each.get('types'):
                country_code = each.get('short_name')

        if geocode.get('lat') and geocode.get('lng'):
            lat = self.dec2dms(geocode.get('lat'), 'lat')
            lng = self.dec2dms(geocode.get('lng'), 'lng')
            lat_dec = str(geocode.get('lat'))
            lng_dec = str(geocode.get('lng'))
            logging.debug("Geocodes from places API: Lat - {}, Lng - {}".format(lat_dec, lng_dec))
        else:
            lat = self.dec2dms(result.get('geometry').get('location').get('lat'), 'lat')
            lng = self.dec2dms(result.get('geometry').get('location').get('lng'), 'lng')
            lat_dec = str(result.get('geometry').get('location').get('lat'))
            lng_dec = str(result.get('geometry').get('location').get('lng'))
            logging.debug("Geocodes from geocoding API Decimal: Lat - {}, Lng - {}".format(lat_dec, lng_dec))

        confidence = 9
        record = []
        print ("Station Resolved Lat - {0}, Lng - {1}".format(lat, lng))
        record.extend([station[0],
                       station[1],
                       lat,
                       lng,
                       str(confidence),
                       postal_code,
                       country_code])
        record = ['None' if value is None else value for value in record]
        csv_line = '|'.join(record) + '\n'
        return csv_line

    def __check_nearby_train_stations(self, result, station):
        logging.debug("Checking nearby train stations")
        places_result = self.maps.places_nearby(result['geometry']['location'], type='train_station',
                                                radius=2000)
        logging.debug("Status: {}".format(places_result.get('status')))
        if places_result['status'] != 'OK':
            logging.debug("No nearby train stations found! Writing to unresolved")
            self.__write_to_unresolved_stations(station, result['geometry']['location'])
            return False
        else:
            logging.debug("Near by station found! Writing to resolved")
            logging.debug("Places result: {}".format(places_result))
            self.__write_to_resolved_stations(
                self.__prepare_line_for_insert(result, station,
                                               places_result['results'][0].get('geometry').get('location')))

    def __fetch_google_geo_codes(self, station):

        station_name_without_extn = station[1]
        if self.append_station:
            station_name_with_extn = station_name_without_extn + " station"

        country_name = rcc.country_names.get(str(station[0][0:2]))
        if not country_name:
            print ("ERROR: Country Name not found for station", station[0])
            exit(1)

        if len(station[0]) != 7:
            print ("ERROR: Station code should be 7 characters long", station[0])
            exit(1)

        geocode_result = self.maps.geocode(station_name_with_extn,
                                           components={"country": country_name})
        logging.info("=======================================================")
        logging.info("Station Name: {}".format(str(station_name_without_extn)))
        logging.info("Google Output: {}".format(geocode_result))

        bbox = True
        if len(geocode_result) > 0:
            logging.debug("Station resolved through geocoding API")
            bbox = geocode_result[0].get('geometry').get('bounds')
            if bbox:
                confidence = self.__get_confidence(geocode_result[0])
                if confidence >= 5:
                    self.__check_nearby_train_stations(geocode_result[0], station)
                else:
                    logging.debug("Confidence level below 5. Fetching without station extension")
                    geocode_result = self.maps.geocode(station_name_without_extn,
                                                       components={
                                                           "country": country_name})
                    logging.info("Google Output for station without extension: {}".format(geocode_result))
                    if len(geocode_result) > 0:
                        logging.debug("Station resolved through geocoding API. Station without extension")
                        bbox = geocode_result[0].get('geometry').get('bounds')
                        if bbox:
                            confidence = self.__get_confidence(geocode_result[0])
                            if confidence >= 5:
                                self.__check_nearby_train_stations(geocode_result[0], station)
                            else:
                                logging.info("Station Unresolvable after second search without extension")
                                self.__write_to_unresolved_stations(station, geocode_result[0]['geometry']['location'])
        else:
            logging.info("Station Unresolvable")
            self.__write_to_unresolved_stations(station)

        if not bbox:
            logging.debug("Accurate location found")
            logging.debug("Types of  locations: {}".format(geocode_result[0]['types']))
            station_found = False
            for types in geocode_result[0]['types']:
                if types in ['train_station', 'transit_station', 'bus_station']:
                    self.__write_to_resolved_stations(
                        self.__prepare_line_for_insert(geocode_result[0], station))
                    station_found = True
                    break
            if not station_found:
                logging.debug("Type is not train_station, transit_station or bus_station")
                self.__check_nearby_train_stations(geocode_result[0], station)


#############################################################################
# ENTER THE PATH OF THE INPUT FILE NAME BELOW
#############################################################################

file_name = 'input.csv'

#############################################################################
start_time = datetime.datetime.now()
print ("Start Time: ", start_time, "\n\n")
dt_time = str(datetime.datetime.now()).replace(':', "_").replace('-', '_').replace(' ', '_')

RailGeoCode(file_name, dt_time)

diff = datetime.datetime.now() - start_time
print ("\nTotal Execution Time: {}".format(diff))
