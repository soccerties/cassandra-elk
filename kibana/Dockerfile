ARG ELK_VERSION

# https://github.com/elastic/kibana-docker
FROM docker.elastic.co/kibana/kibana-oss:${ELK_VERSION}

# Add your kibana plugins setup here
# Example: RUN kibana-plugin install <name|url>
#ADD dashboard.json /usr/share/kibana/dashboard.json
#RUN curl -X POST "http://127.0.0.1:5601/api/kibana/dashboards/import" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' -d @/usr/share/kibana/dashboard.json
