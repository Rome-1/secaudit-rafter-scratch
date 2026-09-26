#!/usr/bin/env node
// Test digest normalization (sha1 → SHA1)

import { readFileSync } from 'fs';

const extAttrPath = '/app/applications/drive/src/app/store/_links/extendedAttributes.ts';
const content = readFileSync(extAttrPath, 'utf8');

console.log('Testing Digest Normalization\n');
console.log('='.repeat(80) + '\n');

// Extract the createFileExtendedAttributes function
const funcMatch = content.match(
    /export function createFileExtendedAttributes\(params: XAttrCreateParams\):[\s\S]*?^}/m
);

if (!funcMatch) {
    console.error('❌ Could not find createFileExtendedAttributes function');
    process.exit(1);
}

const funcBody = funcMatch[0];

// Test 1: Check that input uses lowercase 'sha1'
console.log('Test 1: Input parameter uses lowercase "sha1"');
if (funcBody.includes('digests.sha1')) {
    console.log('  ✓ Input reads from digests.sha1');
} else {
    console.log('  ✗ Input does not read from digests.sha1');
    process.exit(1);
}

// Test 2: Check that output uses uppercase 'SHA1'
console.log('\nTest 2: Output uses uppercase "SHA1"');
if (funcBody.includes('SHA1: digests.sha1')) {
    console.log('  ✓ Output normalizes to SHA1');
} else {
    console.log('  ✗ Output does not normalize to SHA1');
    process.exit(1);
}

// Test 3: Check that the normalization happens in the Digests object
console.log('\nTest 3: Normalization happens in Common.Digests');
if (funcBody.match(/Digests: digests[\s\S]*?SHA1: digests\.sha1/)) {
    console.log('  ✓ Normalization is in the correct location');
} else {
    console.log('  ✗ Normalization is not in the correct location');
    process.exit(1);
}

// Test 4: Check that Digests is undefined when not provided
console.log('\nTest 4: Digests is undefined when not provided');
if (funcBody.match(/Digests: digests[\s\S]*?\?[\s\S]*?:[\s\S]*?undefined/s)) {
    console.log('  ✓ Digests is undefined when not provided');
} else {
    console.log('  ✗ Digests handling might be incorrect');
    process.exit(1);
}

console.log('\n' + '='.repeat(80));
console.log('\n✅ All digest normalization tests passed!');
console.log('\nSummary:');
console.log('  • Input accepts lowercase "sha1" in params.digests');
console.log('  • Output produces uppercase "SHA1" in Common.Digests');
console.log('  • Digests is undefined when not provided');
console.log('  • Normalization follows the canonical key format');
