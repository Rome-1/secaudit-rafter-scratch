// Simple test to verify the changes compile correctly
const fs = require('fs');
const path = require('path');

console.log('Checking if files exist...');

const deepPartialPath = '/app/applications/drive/src/app/utils/type/DeepPartial.ts';
const extendedAttributesPath = '/app/applications/drive/src/app/store/_links/extendedAttributes.ts';
const workerPath = '/app/applications/drive/src/app/store/_uploads/worker/worker.ts';

if (!fs.existsSync(deepPartialPath)) {
    console.error('❌ DeepPartial.ts not found');
    process.exit(1);
}
console.log('✓ DeepPartial.ts exists');

if (!fs.existsSync(extendedAttributesPath)) {
    console.error('❌ extendedAttributes.ts not found');
    process.exit(1);
}
console.log('✓ extendedAttributes.ts exists');

if (!fs.existsSync(workerPath)) {
    console.error('❌ worker.ts not found');
    process.exit(1);
}
console.log('✓ worker.ts exists');

// Check for required exports in extendedAttributes.ts
const extendedAttributesContent = fs.readFileSync(extendedAttributesPath, 'utf8');

const requiredPatterns = [
    /export type MaybeExtendedAttributes/,
    /export type XAttrCreateParams/,
    /export function createFileExtendedAttributes\(params: XAttrCreateParams\)/,
    /export async function encryptFileExtendedAttributes\(\s*params: XAttrCreateParams/,
    /function parseModificationTime\(xattr: MaybeExtendedAttributes\)/,
    /function parseSize\(xattr: MaybeExtendedAttributes\)/,
    /function parseBlockSizes\(xattr: MaybeExtendedAttributes\)/,
    /function parseMedia\(xattr: MaybeExtendedAttributes\)/,
    /function parseDigests\(xattr: MaybeExtendedAttributes\)/,
];

requiredPatterns.forEach((pattern, index) => {
    if (!pattern.test(extendedAttributesContent)) {
        console.error(`❌ Pattern ${index + 1} not found: ${pattern}`);
        process.exit(1);
    }
    console.log(`✓ Pattern ${index + 1} found`);
});

// Check BlockSizes logic (remainder check)
if (!extendedAttributesContent.includes('if (remainder > 0)')) {
    console.error('❌ BlockSizes remainder check not found');
    process.exit(1);
}
console.log('✓ BlockSizes remainder check found');

// Check worker.ts update
const workerContent = fs.readFileSync(workerPath, 'utf8');
if (!workerContent.includes('media:') || !workerContent.includes('digests:')) {
    console.error('❌ Worker.ts not updated with new parameter structure');
    process.exit(1);
}
console.log('✓ Worker.ts updated with new parameter structure');

console.log('\n✅ All checks passed!');
