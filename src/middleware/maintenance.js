'use strict';

const util = require('util');
const nconf = require('nconf');
const meta = require('../meta');
const user = require('../user');
const groups = require('../groups');
const helpers = require('./helpers');

module.exports = function (middleware) {
        middleware.maintenanceMode = helpers.try(async (req, res, next) => {
                // If maintenance mode is disabled, proceed as normal
                if (!meta.config.maintenanceMode) {
                        return next();
                }

                const hooksAsync = util.promisify(middleware.pluginHooks);
                await hooksAsync(req, res);

                const url = req.url.replace(nconf.get('relative_path'), '');
                // Always allow access to login routes during maintenance
                if (url.startsWith('/login') || url.startsWith('/api/login')) {
                        return next();
                }

                // Administrators are always allowed through
                const isAdmin = await user.isAdministrator(req.uid);
                if (isAdmin) {
                        return next();
                }

                // Check if user belongs to any exempt groups (including guests if configured)
                let exemptGroups = meta.config.groupsExemptFromMaintenanceMode;
                const defaultExempt = ['administrators', 'Global Moderators'];
                if (!Array.isArray(exemptGroups) || exemptGroups.length === 0) {
                        exemptGroups = defaultExempt;
                }

                // If user is member of any exempt group, allow
                if (await groups.isMemberOfAny(req.uid, exemptGroups)) {
                        return next();
                }

                // Otherwise, render maintenance page / return JSON
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
};
