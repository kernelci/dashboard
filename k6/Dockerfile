FROM grafana/k6:1.3.0

WORKDIR /

# Copy the entrypoint script and set permissions in one step
COPY --chmod=755 entrypoint.sh /entrypoint.sh

COPY tests/ /k6/tests/

# Create results directory with proper permissions
USER root
RUN mkdir -p /results && chmod 777 /results
USER k6

WORKDIR /k6

ENTRYPOINT ["/entrypoint.sh"]
