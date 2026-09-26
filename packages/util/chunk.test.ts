import chunk from './chunk';

describe('chunk', () => {
    it('should divide an array into chunks of specified size', () => {
        const input = [1, 2, 3, 4, 5];
        const result = chunk(input, 2);
        expect(result).toEqual([[1, 2], [3, 4], [5]]);
    });

    it('should handle arrays that divide evenly', () => {
        const input = [1, 2, 3, 4];
        const result = chunk(input, 2);
        expect(result).toEqual([[1, 2], [3, 4]]);
    });

    it('should handle chunk size of 1 (default)', () => {
        const input = [1, 2, 3];
        const result = chunk(input);
        expect(result).toEqual([[1], [2], [3]]);
    });

    it('should handle explicit chunk size of 1', () => {
        const input = [1, 2, 3];
        const result = chunk(input, 1);
        expect(result).toEqual([[1], [2], [3]]);
    });

    it('should handle chunk size larger than array length', () => {
        const input = [1, 2, 3];
        const result = chunk(input, 5);
        expect(result).toEqual([[1, 2, 3]]);
    });

    it('should handle empty array', () => {
        const result = chunk([], 2);
        expect(result).toEqual([]);
    });

    it('should handle empty array with default parameters', () => {
        const result = chunk();
        expect(result).toEqual([]);
    });

    it('should handle undefined list parameter', () => {
        const result = chunk(undefined as any);
        expect(result).toEqual([]);
    });

    it('should handle chunk size of 0', () => {
        const input = [1, 2, 3];
        const result = chunk(input, 0);
        expect(result).toEqual([]);
    });

    it('should handle negative chunk size', () => {
        const input = [1, 2, 3];
        const result = chunk(input, -1);
        expect(result).toEqual([]);
    });

    it('should not mutate the original array', () => {
        const input = [1, 2, 3, 4, 5];
        const originalInput = [...input];
        chunk(input, 2);
        expect(input).toEqual(originalInput);
    });

    it('should return new arrays (not references)', () => {
        const input = [{ id: 1 }, { id: 2 }, { id: 3 }];
        const result = chunk(input, 2);
        
        // Check that result arrays are new
        expect(result).not.toBe(input);
        expect(result[0]).not.toBe(input);
        
        // But the objects inside are the same references (shallow copy expected)
        expect(result[0][0]).toBe(input[0]);
        expect(result[0][1]).toBe(input[1]);
        expect(result[1][0]).toBe(input[2]);
    });

    it('should work with different data types', () => {
        const stringResult = chunk(['a', 'b', 'c', 'd'], 2);
        expect(stringResult).toEqual([['a', 'b'], ['c', 'd']]);

        const objectResult = chunk([{ x: 1 }, { x: 2 }, { x: 3 }], 2);
        expect(objectResult).toEqual([[{ x: 1 }, { x: 2 }], [{ x: 3 }]]);
    });

    it('should maintain element order', () => {
        const input = [1, 2, 3, 4, 5, 6, 7, 8, 9];
        const result = chunk(input, 3);
        expect(result).toEqual([[1, 2, 3], [4, 5, 6], [7, 8, 9]]);
    });

    it('should handle undefined chunk size (should use default)', () => {
        const input = [1, 2, 3];
        const result = chunk(input, undefined as any);
        expect(result).toEqual([[1], [2], [3]]);
    });
});