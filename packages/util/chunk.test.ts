import { chunk } from './chunk';

describe('chunk', () => {
    it('should return empty array when given empty array', () => {
        expect(chunk()).toEqual([]);
        expect(chunk([])).toEqual([]);
    });

    it('should use default size of 1 when no size is provided', () => {
        expect(chunk([1, 2, 3])).toEqual([[1], [2], [3]]);
    });

    it('should chunk array into groups of specified size', () => {
        expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]]);
        expect(chunk([1, 2, 3, 4, 5], 3)).toEqual([[1, 2, 3], [4, 5]]);
    });

    it('should handle array length exactly divisible by chunk size', () => {
        expect(chunk([1, 2, 3, 4], 2)).toEqual([[1, 2], [3, 4]]);
        expect(chunk([1, 2, 3, 4, 5, 6], 3)).toEqual([[1, 2, 3], [4, 5, 6]]);
    });

    it('should handle case where chunk size is larger than array length', () => {
        expect(chunk([1, 2], 5)).toEqual([[1, 2]]);
        expect(chunk([1], 3)).toEqual([[1]]);
    });

    it('should handle chunk size of 1', () => {
        expect(chunk([1, 2, 3], 1)).toEqual([[1], [2], [3]]);
    });

    it('should preserve order of original array elements', () => {
        const array = ['a', 'b', 'c', 'd', 'e', 'f'];
        expect(chunk(array, 2)).toEqual([['a', 'b'], ['c', 'd'], ['e', 'f']]);
    });

    it('should work with different data types', () => {
        const objects = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];
        expect(chunk(objects, 2)).toEqual([[{ id: 1 }, { id: 2 }], [{ id: 3 }, { id: 4 }]]);
    });
});