import http from "k6/http";
import { check } from "k6";

/*
* This test simulates user behavior for the Tree Details page.
* It fetches the most recent commit from both mainline and next branches,
* then retrieves their details.
*
* This assures that the TreeDetails pages exist, and we also cover
* the TreeLatest endpoint with it.
*/
export default function () {
    // Get the most recent commit from mainline so that we can fetch its details
    const mainlineLatestRes = http.get('http://test-backend:8000/api/tree/mainline/master');
    check(mainlineLatestRes, {
        'mainline latest status is 200': (r) => r.status === 200,
        'mainline latest response time < 500ms': (r) => r.timings.duration < 500,
        'mainline latest has body': (r) => r.body && r.body.length > 0,
    });
    
    const mainlineLatestData = JSON.parse(mainlineLatestRes.body);
    if (mainlineLatestData) {
        const mainlineDetailsRes = http.get(`http://test-backend:8000${mainlineLatestData.api_url}`);
        check(mainlineDetailsRes, {
            'mainline details status is 200': (r) => r.status === 200,
            'mainline details response time < 500ms': (r) => r.timings.duration < 500,
            'mainline details has body': (r) => r.body && r.body.length > 0,
        });
    }

    // Get the most recent commit from next so that we can fetch its details
    const nextLatestRes = http.get('http://test-backend:8000/api/tree/next/master');
    check(nextLatestRes, {
        'next latest status is 200': (r) => r.status === 200,
        'next latest response time < 500ms': (r) => r.timings.duration < 500,
        'next latest has body': (r) => r.body && r.body.length > 0,
    });

    const nextLatestData = JSON.parse(nextLatestRes.body);
    if (nextLatestData) {
        const treeDetailsRes = http.get(`http://test-backend:8000${nextLatestData.api_url}`);
        check(treeDetailsRes, {
            'next details status is 200': (r) => r.status === 200,
            'next details response time < 500ms': (r) => r.timings.duration < 500,
            'next details has body': (r) => r.body && r.body.length > 0,
        });
    }

}
