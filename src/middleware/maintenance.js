'use strict';

const util = require('util');
const nconf = require('nconf');
const meta = require('../meta');
const user = require('../user');
const groups = require('../groups');
const helpers = require('./helpers');

module.exports = function (middleware) {
        middleware.maintenanceMode = helpers.try(async (req, res, next) => {
                if (!meta.config.maintenanceMode) {
                        return next();
                }

                const hooksAsync = util.promisify(middleware.pluginHooks);
                await hooksAsync(req, res);

                const url = req.url.replace(nconf.get('relative_path'), '');
                if (url.startsWith('/login') || url.startsWith('/api/login')) {
                        return next();
                }

                const isAdmin = await user.isAdministrator(req.uid);
                if (isAdmin) {
                        return next();
                }

                // Check if user belongs to exempt groups
                const exemptGroups = getGroupsExemptFromMaintenanceMode();
                const isExempt = await checkUserExemptFromMaintenance(req.uid, exemptGroups);
                if (isExempt) {
                        return next();
                }

                res.status(meta.config.maintenanceModeStatus);

                const data = {
                        site_title: meta.config.title || 'NodeBB',
                        message: meta.config.maintenanceModeMessage,
                };

                if (res.locals.isAPI) {
                        return res.json(data);
                }
                await middleware.buildHeaderAsync(req, res);
                res.render('503', data);
        });

        function getGroupsExemptFromMaintenanceMode() {
                let exemptGroups = meta.config.groupsExemptFromMaintenanceMode;
                
                // Handle the case where config is a JSON string
                if (typeof exemptGroups === 'string') {
                        try {
                                exemptGroups = JSON.parse(exemptGroups);
                        } catch (err) {
                                exemptGroups = [];
                        }
                }
                
                // Ensure we always have the default exempt groups (administrators and Global Moderators)
                if (!Array.isArray(exemptGroups)) {
                        exemptGroups = [];
                }
                
                // Add default exempt groups if not already present
                if (!exemptGroups.includes('administrators')) {
                        exemptGroups.push('administrators');
                }
                if (!exemptGroups.includes('Global Moderators')) {
                        exemptGroups.push('Global Moderators');
                }
                
                return exemptGroups;
        }

        async function checkUserExemptFromMaintenance(uid, exemptGroups) {
                // For unauthenticated users (uid = 0), check if 'guests' is in exempt groups
                if (parseInt(uid, 10) <= 0) {
                        return exemptGroups.includes('guests');
                }
                
                // Check if user is a member of any exempt groups
                const isMemberOfGroups = await groups.isMemberOfGroups(uid, exemptGroups);
                return isMemberOfGroups.some(Boolean);
        }
};
