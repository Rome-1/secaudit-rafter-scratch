#!/usr/bin/env node
// Final comprehensive verification of all PR requirements

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RESET = '\x1b[0m';

let passed = 0;
let failed = 0;

function check(condition, message) {
    if (condition) {
        console.log(`${GREEN}✓${RESET} ${message}`);
        passed++;
        return true;
    } else {
        console.log(`${RED}✗${RESET} ${message}`);
        failed++;
        return false;
    }
}

function section(title) {
    console.log(`\n${YELLOW}=== ${title} ===${RESET}\n`);
}

section('File Existence Checks');

const deepPartialPath = '/app/applications/drive/src/app/utils/type/DeepPartial.ts';
const extAttrPath = '/app/applications/drive/src/app/store/_links/extendedAttributes.ts';
const workerPath = '/app/applications/drive/src/app/store/_uploads/worker/worker.ts';

check(existsSync(deepPartialPath), 'DeepPartial.ts exists at correct location');
check(existsSync(extAttrPath), 'extendedAttributes.ts exists');
check(existsSync(workerPath), 'worker.ts exists');

section('DeepPartial Type Definition');

const deepPartialContent = readFileSync(deepPartialPath, 'utf8');
check(
    deepPartialContent.includes('export type DeepPartial<T>'),
    'DeepPartial is exported'
);
check(
    deepPartialContent.includes('T extends object'),
    'DeepPartial handles objects'
);
check(
    deepPartialContent.includes('DeepPartial<T[P]>'),
    'DeepPartial is recursive'
);

section('Extended Attributes Type Definitions');

const extAttrContent = readFileSync(extAttrPath, 'utf8');

check(
    extAttrContent.includes("import { DeepPartial } from '../../utils/type/DeepPartial'"),
    'DeepPartial is imported'
);

check(
    extAttrContent.includes('export type MaybeExtendedAttributes = DeepPartial<ExtendedAttributes>'),
    'MaybeExtendedAttributes is defined correctly'
);

check(
    extAttrContent.includes('export type XAttrCreateParams'),
    'XAttrCreateParams is exported'
);

check(
    extAttrContent.match(/file:\s*File/),
    'XAttrCreateParams has required file property'
);

check(
    extAttrContent.match(/digests\?:\s*\{\s*sha1:\s*string/),
    'XAttrCreateParams has optional digests property with sha1'
);

check(
    extAttrContent.match(/media\?:\s*\{\s*width:\s*number;\s*height:\s*number/),
    'XAttrCreateParams has optional media property with width and height'
);

section('Function Signatures');

check(
    extAttrContent.match(/export function createFileExtendedAttributes\(params: XAttrCreateParams\)/),
    'createFileExtendedAttributes accepts params: XAttrCreateParams'
);

check(
    extAttrContent.match(/export async function encryptFileExtendedAttributes\(\s*params: XAttrCreateParams,/),
    'encryptFileExtendedAttributes accepts params as first parameter'
);

check(
    extAttrContent.match(/encryptFileExtendedAttributes\(\s*params: XAttrCreateParams,\s*nodePrivateKey: PrivateKeyReference,\s*addressPrivateKey: PrivateKeyReference/),
    'encryptFileExtendedAttributes has correct parameter order'
);

section('Implementation Details');

check(
    extAttrContent.includes('const { file, media, digests } = params'),
    'createFileExtendedAttributes destructures params'
);

check(
    extAttrContent.match(/const fullBlocks = Math\.floor\(file\.size \/ FILE_CHUNK_SIZE\)/),
    'BlockSizes calculates full blocks correctly'
);

check(
    extAttrContent.match(/const remainder = file\.size % FILE_CHUNK_SIZE/),
    'BlockSizes calculates remainder'
);

check(
    extAttrContent.match(/if \(remainder > 0\)\s*{\s*blockSizes\.push\(remainder\)/),
    'BlockSizes only pushes remainder when > 0'
);

check(
    extAttrContent.match(/SHA1:\s*digests\.sha1/),
    'Digests normalizes sha1 to SHA1'
);

check(
    extAttrContent.match(/Width:\s*media\.width/),
    'Media normalizes width to Width'
);

check(
    extAttrContent.match(/Height:\s*media\.height/),
    'Media normalizes height to Height'
);

section('Parsing Helper Function Signatures');

const parsingFunctions = [
    'parseModificationTime',
    'parseSize',
    'parseBlockSizes',
    'parseMedia',
    'parseDigests'
];

for (const funcName of parsingFunctions) {
    check(
        extAttrContent.match(new RegExp(`function ${funcName}\\(xattr: MaybeExtendedAttributes\\)`)),
        `${funcName} accepts MaybeExtendedAttributes`
    );
}

section('Worker.ts Integration');

const workerContent = readFileSync(workerPath, 'utf8');

check(
    workerContent.includes("import { encryptFileExtendedAttributes } from '../../_links'"),
    'worker.ts imports encryptFileExtendedAttributes'
);

check(
    workerContent.match(/encryptFileExtendedAttributes\(\s*\{/),
    'worker.ts calls encryptFileExtendedAttributes with object parameter'
);

check(
    workerContent.match(/file,/),
    'worker.ts passes file in params object'
);

check(
    workerContent.match(/media:/),
    'worker.ts passes media in params object'
);

check(
    workerContent.match(/digests:/),
    'worker.ts passes digests in params object'
);

check(
    workerContent.match(/encryptFileExtendedAttributes\(\s*\{[\s\S]*?\},\s*privateKey,\s*addressPrivateKey/),
    'worker.ts passes privateKey and addressPrivateKey after params'
);

section('Summary');

console.log(`\nTotal Checks: ${passed + failed}`);
console.log(`${GREEN}Passed: ${passed}${RESET}`);
console.log(`${RED}Failed: ${failed}${RESET}`);

if (failed === 0) {
    console.log(`\n${GREEN}✅ All requirements met!${RESET}\n`);
    process.exit(0);
} else {
    console.log(`\n${RED}❌ Some requirements not met.${RESET}\n`);
    process.exit(1);
}
