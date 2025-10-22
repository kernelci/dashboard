import http from "k6/http";
import { check } from "k6";

export const options = {
    iterations: 100,
};

export default function () {
    // endTimestamp is "now" or the closest date
    const endTimestampInSeconds = Math.floor(new Date('2025-10-21T19:30:00Z').getTime() / 1000);
    // startTimestamp is x days before endTimestamp
    const startTimestampInSeconds = Math.floor(new Date('2025-10-16T19:30:00Z').getTime() / 1000);

    const defaultRes = http.get("http://test-backend:8000/api/hardware?" +
        `startTimestampInSeconds=${startTimestampInSeconds}&` +
        `endTimestampInSeconds=${endTimestampInSeconds}&` +
        "origin=maestro");

    check(defaultRes, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
}
