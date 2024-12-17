http POST http://localhost:8000/api/hardware/fsl,imx6q-sabrelite/commit-history \
Content-Type:application/json \
<<< '{
  "origin": "maestro",
  "startTimestampInSeconds": 1733846400,
  "endTimestampInSeconds": 1734105600,
    "commitHeads": [
        {
            "treeName": "stable-rc",
            "repositoryUrl": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git",
            "branch": "linux-5.10.y",
            "commitHash": "53504d530e5ecd4c32edd34ab074f6e745bb4e4d"
        },
        {
            "treeName": "stable-rc",
            "repositoryUrl": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git",
            "branch": "linux-5.15.y",
            "commitHash": "765608b24f2192193901d4b27e0d5a0a248e043c"
        }
    ]
}'

