
from garmin_fit_sdk import Decoder, Stream
import argparse
import gzip
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4

ACTIVITY_KEYS = ['id', 'sport', 'datetime']
RECORDS_KEYS = ['activity_id', 'datetime', 'altitude_meters',
                'heart_rate_bpm', 'cadence', 'latitude_degrees', 'longitude_degrees', 'power']
SPORTS = {'Running': 'running', 'Biking': 'cycling', 'Other': 'other'}

DEGREE_CONVERSION = 180 / 2 ** 31


def import_tcx(file_path):
    ns = {'garmin': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}

    tcx_file = gzip.open(file_path, 'rb')
    tcx_contents = tcx_file.read().strip()
    root = ET.fromstring(tcx_contents)
    activity_records = []

    activities_nodes = root.findall('garmin:Activities', ns)
    for activities_node in activities_nodes:
        # TODO: Multisport session
        activity_node = activities_node.find('garmin:Activity', ns)
        activity_id = str(uuid4())
        activity = {
            'id': activity_id,
            'sport': SPORTS.get(activity_node.get('Sport')),
            'datetime': activity_node.find('garmin:Id', ns).text
        }

        laps = activity_node.findall('garmin:Lap', ns)
        for lap in laps:
            for track in lap.findall('garmin:Track', ns):
                for track_point in track.findall('garmin:Trackpoint', ns):
                    position = track_point.find('garmin:Position', ns)
                    heart_rate = track_point.find('garmin:HeartRateBpm', ns)

                    activity_records.append({
                        'activity_id': activity_id,
                        'datetime': get_text(track_point, 'garmin:Time', ns),
                        'altitude_meters': get_text(track_point, 'garmin:AltitudeMeters', ns),
                        'heart_rate_bpm': get_text(heart_rate, 'garmin:Value', ns),
                        'cadence': get_text(track_point, 'garmin:Cadence', ns),
                        'latitude_degrees': get_text(position, 'garmin:LatitudeDegrees', ns),
                        'longitude_degrees': get_text(position, 'garmin:LongitudeDegrees', ns),
                        'power': get_text(track_point, 'garmin:Power', ns),
                    })
        save_activity(activity, activity_records)


def init_csv(name, keys):
    with open(name, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()


def save_activity(activity, activity_records):
    with open('activities.csv', 'a') as output_file:
        dict_writer = csv.DictWriter(output_file, ACTIVITY_KEYS)
        dict_writer.writerow(activity)

    with open('activity_records.csv', 'a') as output_file:
        dict_writer = csv.DictWriter(output_file, RECORDS_KEYS)
        dict_writer.writerows(activity_records)


def get_text(node, child, ns):
    if node is None:
        return None

    child_node = node.find(child, ns)
    return child_node.text if child_node is not None else None


def import_fit(file_path):
    fit_file = gzip.open(file_path, 'rb')
    stream = Stream.from_buffered_reader(fit_file)
    decoder = Decoder(stream)
    messages, errors = decoder.read()

    activity_id = str(uuid4())
    activity = {
        'id': activity_id,
        'sport': messages['session_mesgs'][0]['sport'],
        'datetime': messages['activity_mesgs'][0]['timestamp']
    }

    activity_records = []
    for record in messages['record_mesgs']:
        activity_records.append({
            'activity_id': activity_id,
            'datetime': record['timestamp'],
            'altitude_meters': record.get('enhanced_altitude') or record.get('altitude'),
            'heart_rate_bpm': record.get('heart_rate'),
            'cadence': record.get('cadence'),
            'latitude_degrees': semicircles_to_degrees(record.get('position_lat')),
            'longitude_degrees': semicircles_to_degrees(record.get('position_long')),
            'power': record.get('power'),
        })
    save_activity(activity, activity_records)


def semicircles_to_degrees(cemicircles):
    if cemicircles is None:
        return None

    return float(cemicircles) * DEGREE_CONVERSION


def run(directory: str):
    init_csv('activities.csv', ACTIVITY_KEYS)
    init_csv('activity_records.csv', RECORDS_KEYS)

    pathlist = Path(directory).rglob('*.tcx.gz')
    for path in pathlist:
        print(f'converting {path}')
        import_tcx(path)

    pathlist = Path(directory).rglob('*.fit.gz')
    for path in pathlist:
        print(f'converting {path}')
        import_fit(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--directory', type=str,
                        help='folder with fit files', default='./data')

args = parser.parse_args()
run(args.directory)
