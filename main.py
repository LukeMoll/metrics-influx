import configparser, argparse
import platform
import subprocess
import os
from pprint import pp

def main():
    pp(get_data())
    config = get_config('config.ini')
    args = do_args()
    influx_write(get_data(), config)

def do_args():
    parser = argparse.ArgumentParser()

    return parser.parse_args()

def get_config(fn):
    if not os.path.exists(fn):
        raise FileNotFoundError("Could not find {}".format(fn))
    config = configparser.ConfigParser()
    config.read(fn)

    return config

def get_data():
    return {
        'tags': {
            'hostname': platform.node()
        },
        'fields': {
            **run_uptime(),
            **run_df()
        }
    }

def run_uptime():
    a = os.getloadavg()
    return {
        "loadavg_1": a[0],
        "loadavg_5": a[1],
        "loadavg_15": a[2]
    }

def run_df():
    p = subprocess.run(['df', '.', '/'], capture_output=True)
    results = {}
    for line in p.stdout.decode('UTF-8').splitlines()[1:]:
        fields = line.split()
        results[fields[0]] = fields[3]
    return dict(map(lambda t: ('df'+t[0].replace('/','_'), t[1]), results.items()))


def influx_write(data, config):
    try:
        client = influxdb.InfluxDBClient(
            config['host'], 
            config.get('port', 8086), 
            config['username'], 
            config['password'], 
            config['database'], 
            ssl=True
        )
    except KeyError as e:
        print("Missing {} section/value in {}".format(e, config_fn))
        exit(1)
    for datum in data: datum['measurement'] = measurement
    client.write_points(data)

if __name__ == "__main__":
    main()