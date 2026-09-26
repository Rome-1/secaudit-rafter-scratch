#!/usr/bin/env node
// Test edge cases for BlockSizes logic

const FILE_CHUNK_SIZE = 4194304; // 4MB standard chunk size

function calculateBlockSizes(fileSize) {
    const fullBlocks = Math.floor(fileSize / FILE_CHUNK_SIZE);
    const remainder = fileSize % FILE_CHUNK_SIZE;
    
    const blockSizes = new Array(fullBlocks).fill(FILE_CHUNK_SIZE);
    if (remainder > 0) {
        blockSizes.push(remainder);
    }
    return blockSizes;
}

const testCases = [
    {
        name: 'Empty file (0 bytes)',
        size: 0,
        expected: []
    },
    {
        name: 'Small file (123 bytes)',
        size: 123,
        expected: [123]
    },
    {
        name: 'Exactly 1 chunk',
        size: FILE_CHUNK_SIZE,
        expected: [FILE_CHUNK_SIZE]
    },
    {
        name: '1 chunk + 1 byte',
        size: FILE_CHUNK_SIZE + 1,
        expected: [FILE_CHUNK_SIZE, 1]
    },
    {
        name: 'Exactly 2 chunks',
        size: FILE_CHUNK_SIZE * 2,
        expected: [FILE_CHUNK_SIZE, FILE_CHUNK_SIZE]
    },
    {
        name: '2 chunks + 123 bytes',
        size: FILE_CHUNK_SIZE * 2 + 123,
        expected: [FILE_CHUNK_SIZE, FILE_CHUNK_SIZE, 123]
    },
    {
        name: 'Almost 3 chunks (3 chunks - 1 byte)',
        size: FILE_CHUNK_SIZE * 3 - 1,
        expected: [FILE_CHUNK_SIZE, FILE_CHUNK_SIZE, FILE_CHUNK_SIZE - 1]
    },
    {
        name: 'Exactly 10 chunks',
        size: FILE_CHUNK_SIZE * 10,
        expected: new Array(10).fill(FILE_CHUNK_SIZE)
    },
    {
        name: '10 chunks + half chunk',
        size: FILE_CHUNK_SIZE * 10 + FILE_CHUNK_SIZE / 2,
        expected: [...new Array(10).fill(FILE_CHUNK_SIZE), FILE_CHUNK_SIZE / 2]
    },
];

console.log('Testing BlockSizes Edge Cases\n');
console.log('='.repeat(80) + '\n');

let passed = 0;
let failed = 0;

for (const testCase of testCases) {
    const result = calculateBlockSizes(testCase.size);
    const success = JSON.stringify(result) === JSON.stringify(testCase.expected);
    
    if (success) {
        console.log(`✓ ${testCase.name}`);
        console.log(`  Size: ${testCase.size.toLocaleString()} bytes`);
        console.log(`  Result: ${result.length} block(s)`);
        passed++;
    } else {
        console.log(`✗ ${testCase.name}`);
        console.log(`  Size: ${testCase.size.toLocaleString()} bytes`);
        console.log(`  Expected: [${testCase.expected.join(', ')}]`);
        console.log(`  Got: [${result.join(', ')}]`);
        failed++;
    }
    console.log('');
}

console.log('='.repeat(80));
console.log(`\nTotal: ${testCases.length} tests`);
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);

if (failed === 0) {
    console.log('\n✅ All edge cases pass!');
    process.exit(0);
} else {
    console.log('\n❌ Some edge cases failed!');
    process.exit(1);
}
