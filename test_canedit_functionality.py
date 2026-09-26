#!/usr/bin/env python3

"""
Script to test the canEdit functionality specifically.

This script creates a focused test for the new canEdit prop functionality
to ensure it works correctly in both enabled and disabled states.
"""

import os
import subprocess

def create_test_file():
    test_content = """import { render, screen } from '@testing-library/react';
import { mocked } from 'jest-mock';

import { useApi, useNotifications } from '@proton/components/hooks';
import {
    CalendarMember,
    CalendarMemberInvitation,
    MEMBER_INVITATION_STATUS,
} from '@proton/shared/lib/interfaces/calendar';
import { mockApi, mockNotifications } from '@proton/testing';

import CalendarMemberAndInvitationList from './CalendarMemberAndInvitationList';

jest.mock('@proton/components/hooks/useGetEncryptionPreferences');
jest.mock('@proton/components/hooks/useNotifications');
jest.mock('@proton/components/hooks/useApi');
jest.mock('@proton/components/hooks/useAddresses');

jest.mock('../../contacts/ContactEmailsProvider', () => ({
    useContactEmailsCache: () => ({
        contactEmails: [],
        contactGroups: [],
        contactEmailsMap: {
            'member1@pm.gg': {
                Name: 'Test User',
                Email: 'member1@pm.gg',
            },
        },
        groupsWithContactsMap: {},
    }),
}));

const mockedUseApi = mocked(useApi);
const mockedUseNotifications = mocked(useNotifications);

describe('CalendarMemberAndInvitationList canEdit functionality', () => {
    beforeEach(() => {
        mockedUseApi.mockImplementation(() => mockApi);
        mockedUseNotifications.mockImplementation(() => mockNotifications);
    });

    const members = [
        {
            ID: 'member1',
            Email: 'member1@pm.gg',
            Permissions: 96,
        },
    ] as CalendarMember[];
    
    const invitations = [
        {
            CalendarInvitationID: 'invitation1',
            Email: 'invitation1@pm.gg',
            Permissions: 96,
            Status: MEMBER_INVITATION_STATUS.PENDING,
        },
    ] as CalendarMemberInvitation[];

    it('should enable permission controls when canEdit is true (default)', () => {
        render(
            <CalendarMemberAndInvitationList
                members={members}
                invitations={invitations}
                onDeleteInvitation={() => Promise.resolve()}
                onDeleteMember={() => Promise.resolve()}
                calendarID="1"
                canEdit={true}
            />
        );

        // Check that permission dropdowns are enabled (not disabled)
        const permissionSelects = screen.getAllByRole('button', { name: /See all event details/ });
        permissionSelects.forEach(select => {
            expect(select).not.toBeDisabled();
        });

        // Check that delete buttons are present and enabled
        expect(screen.getByTitle('Remove this member')).not.toBeDisabled();
        expect(screen.getByTitle('Revoke this invitation')).not.toBeDisabled();
    });

    it('should disable permission controls when canEdit is false', () => {
        render(
            <CalendarMemberAndInvitationList
                members={members}
                invitations={invitations}
                onDeleteInvitation={() => Promise.resolve()}
                onDeleteMember={() => Promise.resolve()}
                calendarID="1"
                canEdit={false}
            />
        );

        // Check that permission dropdowns are disabled
        const permissionSelects = screen.getAllByRole('button', { name: /See all event details/ });
        permissionSelects.forEach(select => {
            expect(select).toBeDisabled();
        });

        // Check that delete buttons are still enabled
        expect(screen.getByTitle('Remove this member')).not.toBeDisabled();
        expect(screen.getByTitle('Revoke this invitation')).not.toBeDisabled();
    });

    it('should default canEdit to true when not provided', () => {
        render(
            <CalendarMemberAndInvitationList
                members={members}
                invitations={invitations}
                onDeleteInvitation={() => Promise.resolve()}
                onDeleteMember={() => Promise.resolve()}
                calendarID="1"
                // canEdit prop not provided, should default to true
            />
        );

        // Check that permission dropdowns are enabled by default
        const permissionSelects = screen.getAllByRole('button', { name: /See all event details/ });
        permissionSelects.forEach(select => {
            expect(select).not.toBeDisabled();
        });

        // Check that delete buttons are present and enabled
        expect(screen.getByTitle('Remove this member')).not.toBeDisabled();
        expect(screen.getByTitle('Revoke this invitation')).not.toBeDisabled();
    });
});
"""
    
    test_file_path = "/app/packages/components/containers/calendar/settings/CalendarMemberAndInvitationList.canEdit.test.tsx"
    
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    return test_file_path

def main():
    print("=== Testing canEdit Functionality ===")
    print()
    
    # Create the test file
    test_file = create_test_file()
    print(f"Created test file: {test_file}")
    
    # Run the test
    print("Running canEdit functionality tests...")
    try:
        result = subprocess.run([
            'npx', 'jest', 
            'containers/calendar/settings/CalendarMemberAndInvitationList.canEdit.test.tsx',
            '--passWithNoTests', '--no-coverage'
        ], 
        cwd='/app/packages/components',
        capture_output=True,
        text=True,
        timeout=120
        )
        
        print(f"Exit code: {result.returncode}")
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        # Clean up the test file
        os.remove(test_file)
        print(f"Cleaned up test file: {test_file}")
        
        if result.returncode == 0:
            print("✅ canEdit functionality tests PASSED!")
            return 0
        else:
            print("❌ canEdit functionality tests FAILED!")
            return 1
            
    except subprocess.TimeoutExpired:
        print("❌ Test execution timed out")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit(main())