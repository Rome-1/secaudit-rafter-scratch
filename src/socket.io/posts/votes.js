'use strict';

const db = require('../../database');
const user = require('../../user');
const posts = require('../../posts');
const privileges = require('../../privileges');
const meta = require('../../meta');

module.exports = function (SocketPosts) {
        SocketPosts.getVoters = async function (socket, data) {
                if (!data || !data.pid || !data.cid) {
                        throw new Error('[[error:invalid-data]]');
                }
                const showDownvotes = !meta.config['downvote:disabled'];
                const canSeeVotes = meta.config.votesArePublic || await privileges.categories.isAdminOrMod(data.cid, socket.uid);
                if (!canSeeVotes) {
                        throw new Error('[[error:no-privileges]]');
                }
                const [upvoteUids, downvoteUids] = await Promise.all([
                        db.getSetMembers(`pid:${data.pid}:upvote`),
                        showDownvotes ? db.getSetMembers(`pid:${data.pid}:downvote`) : [],
                ]);

                const [upvoters, downvoters] = await Promise.all([
                        user.getUsersFields(upvoteUids, ['username', 'userslug', 'picture']),
                        user.getUsersFields(downvoteUids, ['username', 'userslug', 'picture']),
                ]);

                return {
                        upvoteCount: upvoters.length,
                        downvoteCount: downvoters.length,
                        showDownvotes: showDownvotes,
                        upvoters: upvoters,
                        downvoters: downvoters,
                };
        };

        SocketPosts.getUpvoters = async function (socket, pids) {
                if (!Array.isArray(pids)) {
                        throw new Error('[[error:invalid-data]]');
                }

                // Enforce access control for non-admins across all categories derived from pids
                const isAdmin = await user.isAdministrator(socket.uid);
                if (!isAdmin) {
                        const cids = await posts.getCidsByPids(pids);
                        const uniqueCids = Array.from(new Set(cids.filter(Boolean)));
                        if (uniqueCids.length) {
                                const allowed = await privileges.categories.isUserAllowedTo('topics:read', uniqueCids, socket.uid);
                                const allAllowed = Array.isArray(allowed) ? allowed.every(Boolean) : !!allowed;
                                if (!allAllowed) {
                                        throw new Error('[[error:no-privileges]]');
                                }
                        }
                }

                const upvoteUidLists = await posts.getUpvotedUidsByPids(pids);
                if (!upvoteUidLists.length) {
                        return [];
                }

                const cutoff = 6; // server-enforced cutoff

                // Prepare per-post truncated uid lists, with per-post ordering preserved
                const perPost = upvoteUidLists.map((uids) => {
                        uids = Array.isArray(uids) ? uids : [];
                        // dedupe within this post while preserving order
                        const seen = new Set();
                        const deduped = [];
                        for (const uid of uids) {
                                const key = String(uid);
                                if (!seen.has(key)) {
                                        seen.add(key);
                                        deduped.push(uid);
                                }
                        }
                        let otherCount = 0;
                        let visibleUids = deduped;
                        if (deduped.length > cutoff) {
                                otherCount = deduped.length - (cutoff - 1);
                                visibleUids = deduped.slice(0, cutoff - 1);
                        }
                        return { visibleUids, otherCount };
                });

                // Deduplicate all user ids across all posts before resolving usernames
                const allVisibleUids = [];
                const seenAll = new Set();
                perPost.forEach(({ visibleUids }) => {
                        visibleUids.forEach((uid) => {
                                const key = String(uid);
                                if (!seenAll.has(key)) {
                                        seenAll.add(key);
                                        allVisibleUids.push(uid);
                                }
                        });
                });

                const usernamesAll = await user.getUsernamesByUids(allVisibleUids);
                const uidToUsername = {};
                allVisibleUids.forEach((uid, idx) => { uidToUsername[uid] = usernamesAll[idx]; });

                // Assemble result preserving per-post order
                const result = perPost.map(({ visibleUids, otherCount }) => ({
                        cutoff,
                        otherCount,
                        usernames: visibleUids.map(uid => uidToUsername[uid]),
                }));

                return result;
        };
};
