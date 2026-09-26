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

                // Check if user is administrator
                const isAdmin = await privileges.users.isAdministrator(socket.uid);
                
                if (!isAdmin) {
                        // Get category IDs associated with the post IDs
                        const cids = await posts.getCidsByPids(pids);
                        const uniqueCids = [...new Set(cids.filter(Boolean))];
                        
                        if (uniqueCids.length > 0) {
                                // Check if user has 'topics:read' privilege for all categories
                                const canReadAll = await Promise.all(
                                        uniqueCids.map(cid => privileges.categories.can('topics:read', cid, socket.uid))
                                );
                                
                                // If any category is not readable, deny access
                                if (canReadAll.some(canRead => !canRead)) {
                                        throw new Error('[[error:no-privileges]]');
                                }
                        }
                }

                const data = await posts.getUpvotedUidsByPids(pids);
                if (!data.length) {
                        return [];
                }

                const cutoff = 6;
                const result = await Promise.all(data.map(async (uids) => {
                        // Deduplicate user IDs
                        const uniqueUids = [...new Set(uids)];
                        
                        let otherCount = 0;
                        let usernamesToResolve = uniqueUids;
                        
                        if (uniqueUids.length > cutoff) {
                                otherCount = uniqueUids.length - (cutoff - 1);
                                usernamesToResolve = uniqueUids.slice(0, cutoff - 1);
                        }
                        
                        const usernames = await user.getUsernamesByUids(usernamesToResolve);
                        return {
                                otherCount: otherCount,
                                usernames: usernames,
                                cutoff: cutoff,
                        };
                }));
                return result;
        };
};
