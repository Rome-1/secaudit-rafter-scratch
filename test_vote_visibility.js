const db = require('./src/database');
const meta = require('./src/meta');
const user = require('./src/user');
const topics = require('./src/topics');
const posts = require('./src/posts');
const categories = require('./src/categories');
const privileges = require('./src/privileges');

async function test() {
    console.log('Starting test for vote visibility...\n');
    
    // Check current voteVisibility config
    const voteVisibility = meta.config.voteVisibility;
    console.log('Current voteVisibility config:', voteVisibility);
    
    // Create test users
    const adminUid = await user.create({ username: 'testadmin', email: 'admin@test.com', password: 'password123' });
    const normalUid = await user.create({ username: 'testuser', email: 'user@test.com', password: 'password123' });
    
    console.log('Created test users:', { adminUid, normalUid });
    
    // Make admin an administrator
    await user.setUserField(adminUid, 'status', 'online');
    await db.sortedSetAdd('administrators', Date.now(), adminUid);
    
    // Create a test category
    const categoryData = await categories.create({
        name: 'Test Category',
        description: 'Test category for vote visibility',
        uid: adminUid,
    });
    console.log('Created test category:', categoryData.cid);
    
    // Create a test topic
    const topicData = await topics.post({
        uid: adminUid,
        cid: categoryData.cid,
        title: 'Test Topic',
        content: 'This is a test topic for vote visibility',
    });
    console.log('Created test topic:', topicData.topicData.tid);
    
    // Add a vote to the main post
    const pid = topicData.postData.pid;
    await posts.upvote(pid, adminUid);
    console.log('Added upvote to post:', pid);
    
    // Check privileges for normal user
    const userPrivileges = await privileges.topics.get(topicData.topicData.tid, normalUid);
    console.log('Normal user privileges:', {
        read: userPrivileges['topics:read'],
        isAdmin: userPrivileges.isAdministrator,
        isMod: userPrivileges.isModerator,
    });
    
    // Try to get upvoters as normal user
    try {
        const canSeeVotes = await posts.canSeeVotes(pid, normalUid);
        console.log('Can normal user see votes?', canSeeVotes);
        
        if (!canSeeVotes) {
            console.log('Normal user cannot see votes - this would trigger error in frontend');
        }
    } catch (err) {
        console.log('Error checking vote visibility:', err.message);
    }
    
    // Check what data is sent to topic controller
    const topicController = require('./src/controllers/topics');
    console.log('\nChecking topic controller data structure...');
    const req = {
        params: { topic_id: topicData.topicData.tid },
        uid: normalUid,
        query: {},
        loggedIn: true,
    };
    const res = {
        locals: { isAPI: false, linkTags: [] },
        render: (template, data) => {
            console.log('Topic data includes voteVisibility?', 'voteVisibility' in data);
            console.log('Current meta.config.voteVisibility:', meta.config.voteVisibility);
        },
        set: () => {},
    };
    
    try {
        // Note: This won't actually work without a full express setup, but shows the structure
        console.log('Topic controller would need to add voteVisibility to topicData');
    } catch (err) {
        console.log('Expected error in test environment:', err.message);
    }
    
    console.log('\n=== Test Summary ===');
    console.log('1. Vote visibility is controlled by meta.config.voteVisibility');
    console.log('2. Current value:', meta.config.voteVisibility || 'not set');
    console.log('3. Need to add voteVisibility to topicData in topics controller');
    console.log('4. Need to modify frontend votes.js to check permissions before showing tooltips');
    console.log('5. Need to optimize database calls in accounts/helpers.js');
    
    process.exit(0);
}

// Initialize database and run test
db.init(async (err) => {
    if (err) {
        console.error('Database init error:', err);
        process.exit(1);
    }
    
    await meta.configs.init();
    await test();
});