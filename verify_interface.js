// This script verifies that the new interface is correctly implemented
const fs = require('fs');

const extendedAttributesContent = fs.readFileSync(
    '/app/applications/drive/src/app/store/_links/extendedAttributes.ts',
    'utf8'
);

console.log('Checking implementation details...\n');

// Check 1: XAttrCreateParams type exists and has correct shape
if (!extendedAttributesContent.includes('export type XAttrCreateParams')) {
    console.error('❌ XAttrCreateParams not exported');
    process.exit(1);
}
console.log('✓ XAttrCreateParams is exported');

if (!extendedAttributesContent.match(/file:\s*File/)) {
    console.error('❌ XAttrCreateParams does not have file: File property');
    process.exit(1);
}
console.log('✓ XAttrCreateParams has file property');

if (!extendedAttributesContent.match(/digests\?:/)) {
    console.error('❌ XAttrCreateParams does not have optional digests property');
    process.exit(1);
}
console.log('✓ XAttrCreateParams has optional digests property');

if (!extendedAttributesContent.match(/media\?:/)) {
    console.error('❌ XAttrCreateParams does not have optional media property');
    process.exit(1);
}
console.log('✓ XAttrCreateParams has optional media property');

// Check 2: createFileExtendedAttributes accepts params object
if (!extendedAttributesContent.match(/createFileExtendedAttributes\(params: XAttrCreateParams\)/)) {
    console.error('❌ createFileExtendedAttributes does not accept params: XAttrCreateParams');
    process.exit(1);
}
console.log('✓ createFileExtendedAttributes accepts params: XAttrCreateParams');

// Check 3: encryptFileExtendedAttributes accepts params as first parameter
if (!extendedAttributesContent.match(/encryptFileExtendedAttributes\(\s*params: XAttrCreateParams,/)) {
    console.error('❌ encryptFileExtendedAttributes does not accept params as first parameter');
    process.exit(1);
}
console.log('✓ encryptFileExtendedAttributes accepts params as first parameter');

// Check 4: BlockSizes logic - remainder should only be added if > 0
const blockSizesLogicRegex = /if \(remainder > 0\)\s*{\s*blockSizes\.push\(remainder\)/s;
if (!blockSizesLogicRegex.test(extendedAttributesContent)) {
    console.error('❌ BlockSizes does not conditionally add remainder when > 0');
    process.exit(1);
}
console.log('✓ BlockSizes only adds remainder when > 0');

// Check 5: Parsing functions accept MaybeExtendedAttributes
const parsingFunctions = [
    'parseModificationTime',
    'parseSize',
    'parseBlockSizes',
    'parseMedia',
    'parseDigests'
];

for (const funcName of parsingFunctions) {
    const regex = new RegExp(`function ${funcName}\\(xattr: MaybeExtendedAttributes\\)`);
    if (!regex.test(extendedAttributesContent)) {
        console.error(`❌ ${funcName} does not accept MaybeExtendedAttributes`);
        process.exit(1);
    }
    console.log(`✓ ${funcName} accepts MaybeExtendedAttributes`);
}

// Check 6: DeepPartial import
if (!extendedAttributesContent.includes("import { DeepPartial } from '../../utils/type/DeepPartial'")) {
    console.error('❌ DeepPartial is not imported correctly');
    process.exit(1);
}
console.log('✓ DeepPartial is imported');

// Check 7: MaybeExtendedAttributes type alias
if (!extendedAttributesContent.includes('export type MaybeExtendedAttributes = DeepPartial<ExtendedAttributes>')) {
    console.error('❌ MaybeExtendedAttributes is not defined correctly');
    process.exit(1);
}
console.log('✓ MaybeExtendedAttributes is defined');

console.log('\n✅ All interface checks passed!');
