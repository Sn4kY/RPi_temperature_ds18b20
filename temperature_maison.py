#!/usr/bin/python
import time, sys, signal, json, yaml, os, requests

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from datetime import date, datetime

import subprocess

config = yaml.safe_load(open(os.path.dirname(sys.argv[0]) + "/config.yml"))

base_dir = '/sys/bus/w1/devices/'
sonde1 = base_dir + '28-0319a2790f6a/w1_slave'
sonde2 = base_dir + '28-0319a2792d11/w1_slave'

def read_temp_raw(sonde):
    f = open(sonde, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(sonde):
    lines = read_temp_raw(sonde)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.1)
        lines = read_temp_raw(sonde)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_round = round(temp_c,1)
        return temp_round
 

def loop():
  while True:
    date=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    t_sonde1 = read_temp(sonde1)
    t_sonde2 = read_temp(sonde2)
    print date
    print("Sonde 1 : %.1f" % t_sonde1)
    print("Sonde 2 : %.1f" % t_sonde2)
    json_body = [
    {
      "measurement": "temperature",
      "tags": {
        "host": "sonde1"
      },
      "time": date,
      "fields": { "value": t_sonde1
      }
    },
    {
      "measurement": "temperature",
      "tags": {
        "host": "sonde2"
      },
      "time": date,
      "fields": { "value": t_sonde2
      }
    }
    ]

    client = InfluxDBClient(config['influxdb']['host'], config['influxdb']['port'], config['influxdb']['user'], config['influxdb']['passwd'], config['influxdb']['db'], config['influxdb']['timeout'])
    try:
      client.write_points(json_body,time_precision='ms')
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout,
                  InfluxDBClientError, InfluxDBServerError) as err:
      print("Oops ! connextion error !")

    #result = client.query('select value from temperature;')
    #print("Result: {0}".format(result))

    time.sleep(5)

def signal_term_handler(signal, frame):
  sys.exit(0)

if __name__ == '__main__':
  signal.signal(signal.SIGTERM, signal_term_handler)
  loop()
