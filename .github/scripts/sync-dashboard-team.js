#!/usr/bin/env node

const fs = require("fs");
const { Octokit } = require("@octokit/rest");
const path = require("path");

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

const ORG = process.env.ORG;
const TEAM_SLUG = process.env.TEAM_SLUG;
const DRY_RUN = process.env.DRY_RUN === "true";

const TEAM_FILE = path.join(
  __dirname,
  "..",
  "dashboard-team",
);

const PROTECTED_USERS = ["nuclearcat", "bhcopeland", "victor-accarini"];

const USER_RE = /^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$/i;

function validateEnv() {
  const required = ["ORG", "TEAM_SLUG", "GITHUB_TOKEN"];

  const missing = required.filter((v) => !process.env[v]);

  if (missing.length > 0) {
    throw new Error(`Missing required env vars: ${missing.join(", ")}`);
  }
}

function readDesiredUsers() {
  if (!fs.existsSync(TEAM_FILE)) {
    throw new Error(`Team file not found: ${TEAM_FILE}`);
  }

  const content = fs.readFileSync(TEAM_FILE, "utf8");

  const users = [
    ...new Set(
      content
        .split("\n")
        .map((line) => line.trim().toLowerCase())
        .filter((line) => line && !line.startsWith("#")),
    ),
  ];

  const invalidUsers = users.filter((u) => !USER_RE.test(u));
  if (invalidUsers.length > 0) {
    throw new Error(
      `Found invalid GitHub usernames: ${invalidUsers.join(", ")}`,
    );
  }

  return users;
}

async function getCurrentTeamMembers() {
  const members = await octokit.paginate(octokit.teams.listMembersInOrg, {
    org: ORG,
    team_slug: TEAM_SLUG,
    per_page: 100,
  });

  return members.map((m) => m.login.toLowerCase());
}

async function ensureOrgMembership(username) {
  try {
    const membership = await octokit.orgs.getMembershipForUser({
      org: ORG,
      username,
    });

    const state = membership.data.state;

    if (state === "active") {
      console.log(`${username} is already an active org member`);
      return "active";
    }

    if (state === "pending") {
      console.log(`${username} already has a pending org invitation`);
      return "pending";
    }

    throw new Error(`Unexpected membership state for ${username}: ${state}`);
  } catch (err) {
    if (err.status === 404) {
      if (DRY_RUN) {
        console.log(`[DRY RUN] Would invite ${username} to org`);
        return "invited";
      }

      console.log(`Inviting ${username} to org`);

      await octokit.orgs.setMembershipForUser({
        org: ORG,
        username,
        role: "direct_member",
      });

      return "invited";
    }

    throw err;
  }
}

async function addToTeam(username) {
  if (DRY_RUN) {
    console.log(`[DRY RUN] Would add ${username} to ${TEAM_SLUG}`);
    return;
  }

  console.log(`Adding ${username} to ${TEAM_SLUG}`);

  await octokit.teams.addOrUpdateMembershipForUserInOrg({
    org: ORG,
    team_slug: TEAM_SLUG,
    username,
    role: "member",
  });
}

async function removeFromTeam(username) {
  if (PROTECTED_USERS.includes(username)) {
    console.log(`Skipping protected user removal: ${username}`);
    return;
  }

  if (DRY_RUN) {
    console.log(`[DRY RUN] Would remove ${username} from ${TEAM_SLUG}`);
    return;
  }

  console.log(`Removing ${username} from ${TEAM_SLUG}`);

  await octokit.teams.removeMembershipForUserInOrg({
    org: ORG,
    team_slug: TEAM_SLUG,
    username,
  });
}

async function main() {
  validateEnv();

  const desiredUsers = readDesiredUsers();
  const currentUsers = await getCurrentTeamMembers();

  const usersToAdd = desiredUsers.filter((u) => !currentUsers.includes(u));
  const usersToRemove = currentUsers.filter((u) => !desiredUsers.includes(u));

  console.log("");
  console.log("=== Dashboard Team Sync ===");
  console.log("");

  console.log(`Desired users (${desiredUsers.length}):`);
  desiredUsers.forEach((u) => console.log(`  - ${u}`));

  console.log("");

  console.log(`Current users (${currentUsers.length}):`);
  currentUsers.forEach((u) => console.log(`  - ${u}`));

  console.log("");

  for (const username of usersToAdd) {
    const membershipState = await ensureOrgMembership(username);

    if (membershipState !== "active") {
      console.log(`${username} is not yet an active org member`);

      continue;
    }

    await addToTeam(username);
  }

  for (const username of usersToRemove) {
    await removeFromTeam(username);
  }

  console.log("");
  console.log("Sync complete");
}

main().catch((err) => {
  console.error("");
  console.error("Sync failed");
  console.error(err);

  process.exit(1);
});
