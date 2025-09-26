import http from "k6/http";
import { check } from "k6";


/*
* This test simulates user behavior for the Build and Test Details pages.
* It fetches the latest commit for the mainline/master tree, then retrieves
* details for a random build and boot associated with that tree.
*
* Along with the BuildDetails and TestDetails pages, this test also
* covers the TreeDetailsBuilds and TreeDetailsBoots endpoints.
*/
export default function () {
    const treeName = 'mainline';
    const gitBranch = 'master';
    
    const treeLatestRes = http.get(`http://test-backend:8000/api/tree/${treeName}/${gitBranch}/`);
    check(treeLatestRes, {
        'tree status is 200': (r) => r.status === 200,
        'has body': (r) => r.body && r.body.length > 0,
    });

    const mainlineData = JSON.parse(treeLatestRes.body);
    if (!mainlineData || mainlineData.length === 0) {
        console.log("No data found for mainline/master, cannot proceed with details page test.");
        return;
    }

    const commitHash = mainlineData["git_commit_hash"];

    // Build Details
    const buildsRes = http.get(`http://test-backend:8000/api/tree/${treeName}/${gitBranch}/${commitHash}/builds/`);
    check(buildsRes, {
        'builds status is 200': (r) => r.status === 200,
        'builds response time < 500ms': (r) => r.timings.duration < 500,
        'builds has body': (r) => r.body && r.body.length > 0,
    });

    const buildsData = JSON.parse(buildsRes.body);
    let buildId;
    if (buildsData.length > 0 && buildsData["builds"].length > 0) {
        const randomIndex = Math.floor(Math.random() * buildsData["builds"].length);
        const selectedBuild = buildsData["builds"][randomIndex];
        buildId = selectedBuild.id;
    }

    const buildDetailsRes = http.get(`http://test-backend:8000/api/build/${buildId}/`);
    check(buildDetailsRes, {
        'build details status is 200': (r) => r.status === 200,
        'build details response time < 500ms': (r) => r.timings.duration < 500
    });

    // Boot Details
    const bootsRes = http.get(`http://test-backend:8000/api/tree/${treeName}/${gitBranch}/${commitHash}/boots/`);
    check(bootsRes, {
        'boots status is 200': (r) => r.status === 200,
        'boots response time < 500ms': (r) => r.timings.duration < 500,
        'boots has body': (r) => r.body && r.body.length > 0,
    });

    const bootsData = JSON.parse(bootsRes.body);
    let bootId;
    if (bootsData.length > 0 && bootsData["boots"].length > 0) {
        const randomIndex = Math.floor(Math.random() * bootsData["boots"].length);
        const selectedBoot = bootsData["boots"][randomIndex];
        bootId = selectedBoot.id;
    }

    const bootDetailsRes = http.get(`http://test-backend:8000/api/boot/${bootId}/`);
    check(bootDetailsRes, {
        'boot details status is 200': (r) => r.status === 200,
        'boot details response time < 500ms': (r) => r.timings.duration < 500
    });
}
