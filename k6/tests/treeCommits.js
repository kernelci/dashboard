import http from "k6/http";
import { check } from "k6";

/*
* Retrieves the latest commit for the next/master tree, then fetches
* the commits associated with that tree.
*/
export default function () {
    const nextLatestRes = http.get('http://test-backend:8000/api/tree/next/master');
    check(nextLatestRes, {
        'next latest status is 200': (r) => r.status === 200,
        'next latest has body': (r) => r.body && r.body.length > 0,
    });
    
    const nextLatestData = JSON.parse(nextLatestRes.body);
    if (!nextLatestData) {
        console.log("No next/master latest commit found, cannot proceed with commits test.");
        return;
    }

    const nextCommitsRes = http.get(
        `http://test-backend:8000/api/tree/next/master/\
        b5a4da2c459f79a2c87c867398f1c0c315779781/commits`
    );
    check(nextCommitsRes, {
        'next details status is 200': (r) => r.status === 200,
        'next details response time < 500ms': (r) => r.timings.duration < 500,
    });
}
