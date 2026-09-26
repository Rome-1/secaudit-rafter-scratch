#!/usr/bin/env python3

"""
Script to demonstrate the vote visibility issue and database performance problem
"""

import sys
import os
import subprocess
import json

def main():
    print("=== NodeBB Vote Visibility and Database Performance Issue Demo ===")
    
    # Check if we can find the required files
    files_to_check = [
        '/app/public/src/client/topic/votes.js',
        '/app/src/controllers/topics.js',
        '/app/src/controllers/accounts/helpers.js',
        '/app/src/database/mongo/sorted.js',
        '/app/src/database/redis/sorted.js',
        '/app/src/database/postgres/sorted.js'
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"ERROR: Missing required files: {missing_files}")
        return 1
    
    print("\n1. CURRENT ISSUES:")
    print("   a) Vote tooltips show error alerts for users without permissions")
    print("   b) Profile pages make inefficient database queries for post counts")
    
    print("\n2. CURRENT IMPLEMENTATION ANALYSIS:")
    
    # Check vote.js for conditional handling
    print("\n   Analyzing client-side vote handling...")
    with open('/app/public/src/client/topic/votes.js', 'r') as f:
        votes_content = f.read()
        if 'canSeeVotes' not in votes_content:
            print("   ❌ No canSeeVotes function found")
        else:
            print("   ✅ canSeeVotes function already exists")
        
        if 'voteVisibility' not in votes_content:
            print("   ❌ No voteVisibility checking in client code")
        else:
            print("   ✅ voteVisibility checking exists")
    
    # Check topics controller for voteVisibility
    print("\n   Analyzing topics controller...")
    with open('/app/src/controllers/topics.js', 'r') as f:
        topics_content = f.read()
        if 'voteVisibility' not in topics_content:
            print("   ❌ voteVisibility not included in topicData")
        else:
            print("   ✅ voteVisibility field included in topicData")
    
    # Check accounts helpers for inefficient queries
    print("\n   Analyzing accounts helpers...")
    with open('/app/src/controllers/accounts/helpers.js', 'r') as f:
        helpers_content = f.read()
        # Look for multiple sortedSetCount calls
        best_count = helpers_content.count('sortedSetCount')
        if 'Promise.all(cids.map(async c => db.sortedSetCount(' in helpers_content:
            print(f"   ❌ Found inefficient database calls using multiple sortedSetCount: {best_count} occurrences")
        else:
            print("   ✅ No inefficient sortedSetCount patterns found")
    
    # Check database implementations for min/max parameters
    for db_type in ['mongo', 'redis', 'postgres']:
        db_file = f'/app/src/database/{db_type}/sorted.js'
        print(f"\n   Analyzing {db_type} sortedSetsCardSum implementation...")
        with open(db_file, 'r') as f:
            db_content = f.read()
            # Find the sortedSetsCardSum function
            if 'sortedSetsCardSum = async function (keys)' in db_content:
                print(f"   ❌ {db_type}: sortedSetsCardSum doesn't accept min/max parameters")
            elif 'sortedSetsCardSum = async function (keys, min, max)' in db_content:
                print(f"   ✅ {db_type}: sortedSetsCardSum accepts min/max parameters")
            else:
                print(f"   ❓ {db_type}: Could not determine sortedSetsCardSum signature")
    
    print("\n3. NEXT STEPS:")
    print("   - Implement canSeeVotes function in client-side code")
    print("   - Add voteVisibility field to topicData") 
    print("   - Update sortedSetsCardSum functions to accept min/max parameters")
    print("   - Optimize profile page queries to use single sortedSetsCardSum call")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())