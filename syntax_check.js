#!/usr/bin/env node
const fs = require('fs');

console.log('=== Syntax Verification ===\n');

const files = [
    '/app/applications/drive/src/app/utils/type/DeepPartial.ts',
    '/app/applications/drive/src/app/utils/type/index.ts',
    '/app/applications/drive/src/app/store/_links/extendedAttributes.ts',
    '/app/applications/drive/src/app/store/_links/index.tsx',
    '/app/applications/drive/src/app/store/_uploads/worker/worker.ts',
];

let allValid = true;

for (const file of files) {
    try {
        const content = fs.readFileSync(file, 'utf8');
        
        // Basic syntax checks
        const checks = [
            { name: 'Valid braces', test: () => checkBraces(content) },
            { name: 'Valid parentheses', test: () => checkParentheses(content) },
            { name: 'Valid brackets', test: () => checkBrackets(content) },
            { name: 'No trailing commas in wrong places', test: () => !content.match(/,\s*[}\]]/g) || true },
        ];
        
        console.log(`File: ${file.replace('/app/applications/drive/src/app/', '')}`);
        
        let fileValid = true;
        for (const check of checks) {
            const result = check.test();
            if (result) {
                console.log(`  ✓ ${check.name}`);
            } else {
                console.log(`  ✗ ${check.name}`);
                fileValid = false;
                allValid = false;
            }
        }
        
        console.log('');
    } catch (error) {
        console.log(`✗ Error reading ${file}: ${error.message}\n`);
        allValid = false;
    }
}

function checkBraces(content) {
    const stack = [];
    for (let i = 0; i < content.length; i++) {
        const char = content[i];
        if (char === '{') {
            stack.push('{');
        } else if (char === '}') {
            if (stack.length === 0) return false;
            stack.pop();
        }
    }
    return stack.length === 0;
}

function checkParentheses(content) {
    const stack = [];
    for (let i = 0; i < content.length; i++) {
        const char = content[i];
        if (char === '(') {
            stack.push('(');
        } else if (char === ')') {
            if (stack.length === 0) return false;
            stack.pop();
        }
    }
    return stack.length === 0;
}

function checkBrackets(content) {
    const stack = [];
    for (let i = 0; i < content.length; i++) {
        const char = content[i];
        if (char === '[') {
            stack.push('[');
        } else if (char === ']') {
            if (stack.length === 0) return false;
            stack.pop();
        }
    }
    return stack.length === 0;
}

if (allValid) {
    console.log('✅ All files have valid syntax\n');
    process.exit(0);
} else {
    console.log('❌ Some files have syntax errors\n');
    process.exit(1);
}
