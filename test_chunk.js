// Test script to verify chunk function works correctly
// This tests the current implementation before making changes

// Mock the chunk function from the current implementation
const chunk = (list = [], size = 1) => {
    return list.reduce((res, item, index) => {
        if (index % size === 0) {
            res.push([]);
        }
        res[res.length - 1].push(item);
        return res;
    }, []);
};

// Test cases
console.log('Testing chunk function:');
console.log('Empty array:', JSON.stringify(chunk()));
console.log('Default size (1):', JSON.stringify(chunk([1, 2, 3])));
console.log('Size 2:', JSON.stringify(chunk([1, 2, 3, 4, 5], 2)));
console.log('Size 3:', JSON.stringify(chunk([1, 2, 3, 4, 5], 3)));
console.log('Exact division:', JSON.stringify(chunk([1, 2, 3, 4], 2)));
console.log('Single element:', JSON.stringify(chunk([1], 3)));
console.log('Size larger than array:', JSON.stringify(chunk([1, 2], 5)));