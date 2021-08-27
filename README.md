# cassandra-elk
This repo contains a Docker compose ELK stack to analyse Cassandra and DataStax Enterprise logs as organized in a diagnostic bundle.
You can use OpsCenter or these scripts from DataStax to collect the diagnostic bundle from a cluster:
[Diagnostic Collection Scripts](https://github.com/DataStax-Toolkit/diagnostic-collection)


## Prerequisites

* Linux machine (You can use OSX but make sure docker RAM is increased to at least 8GB)
* [Docker Compose](https://docs.docker.com/compose/install/#install-compose)

## Usage

Clone the repo and change directories into it.
```bash
git clone https://github.com/riptano/cassandra-elk.git
cd cassadra-elk
```

Run the `start-elk-stack.sh` script passing in the path to your diagnostic bundle.
```bash
./start-elk-stack.sh /path/to/your/diag/CLUSTERNAME-diagnostics-2019_02_14_15_37_50_UTC/
```

The script will download all needed containers, launch them, and setup Kibana. Once it returns you can bring up the Kibana UI at `http://<ip address>:5601/`

If something doesn't come up properly the script can be run multiple times without issue.

It can take a while to index all the logs especially with larger diags. You can see the index grow on the *Discover* tab in Kibana.

To stop the stack run `docker-compose down`.

#### Multiple Diagnostics

All of the ELK stack related files are stored within the diagnostic directory. This means you can switch between diagnostics without issues.
Just stop the stack then relaunch pointing to a different diagnostic path to switch.

#### Logs Not In a Diagnostic

If you have logs not in the typical diagnostic structure. You can edit the `logstash/pipeline/logstash.conf` file and change
the log file paths.

The `/client_data/` path refers to the path passed to the `start-elk-stack.sh` script. 
So if you have log files in `/home/me/cluster1/logs/`. Change this line:
```
path => ["/client_data/nodes/*/logs/cassandra/system.log", "/client_data/nodes/*/logs/cassandra/debug.log"]
```

To this:

```
path => ["/client_data/logs/*.log"]
```
And you would launch the stack with `start-elk-stack.sh /home/me/cluster1`


## Contributing

Index patterns and Kibana dashboards are the two main ways to contribute.

## Index Patterns

A list of built in logstash grok patterns can be found here: https://github.com/elastic/logstash/blob/v1.4.2/patterns/grok-patterns

A useful tool for building grok patterns is here: https://grokdebug.herokuapp.com/

Grok patterns can be found in `logstash/config/patterns/`.
The `cassandra-default` file contains patterns that match all possible log lines. Anything that doesn't match is 
considered a stack trace and indexed as part of the preceding matched line.

You can add more indexes for building visualizations in the `logstash/pipeline/logstash.conf` file. 
There's a section to define additional matching based on Java filename.
Add an if statement targeting the Java file and apply your patterns against the `message` of the log line as below.
You can add a `tag_on_failure` to help troubleshoot if needed.
```
  if [file] == "GCInspector.java" {
    grok {
      patterns_dir => "/usr/share/logstash/config/patterns"
      match => {"message" => "G1\s?%{GCINSPECTOR_GC_TYPE:gc_type} GC in %{GCINSPECTOR_GC_DURATION_MS:gc_duration_ms:int}ms%{GREEDYDATA}"}
      tag_on_failure => ["tags", "gcinspector_grok_parse_failure"]
    }
  }
```

This will index the GC type and the GC duration so you can filter and aggregate based on those values.

## Kibana Dashboards

Use the Kibana UI to create visualizations and dashboards you find useful. You can find the getting started guide here: [Dashboards Getting Started](https://www.elastic.co/guide/en/kibana/6.2/dashboard-getting-started.html)

Make sure you add all your visualizations to at least one dashboard so that they can be exported with the `export-dashboards.py` script.

Once you have the dashboards ready. Run the `export-dashboards.py` script to save them to json files.
The saved json files are used to automatically import the dashboards when launching the ELK stack.

NOTE: The export script requires the `requests` and `elasticsearch6` python modules to run.

If you're running the ELK stack locally. No arguments are needed with the script as it connects to localhost by default.
If you're running the ELK stack on another server. Use the -e and -k options to pass in the connection points.

Example script usage:
```bash
export-dashboards.py -e 10.101.32.111 -k 10.101.32.111
```

Full script usage:
```bash
usage: export-dashboards.py [-h] [-e ELASTICSEARCH] [-k KIBANA] [-i INDEX]
                            [-d DESTINATION] [-v]

This script exports all dashboards and objects for Kibana and saves them as
json files.

optional arguments:
  -h, --help            show this help message and exit
  -e ELASTICSEARCH, --elasticsearch ELASTICSEARCH
                        ElasticSearch host to get Kibana data from.
  -k KIBANA, --kibana KIBANA
                        Kibana host to export dashboards from.
  -i INDEX, --index INDEX
                        The ElasticSearch index name with Kibana data.
  -d DESTINATION, --destination DESTINATION
                        Directory to save dashboard json files to.
  -v, --verbose         Enable verbose logging output.

```

Once the dashboards are exported. Issue a PR so they can be used by others.
