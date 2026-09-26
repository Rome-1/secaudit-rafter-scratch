// Chunk utility: splits an array into sub-arrays of a given size.
// Default size is 1. Returns a new array of new sub-arrays without mutating input.
export const chunk = <T>(list: T[] = [], size = 1): T[][] => {
    return list.reduce<T[][]>((result, item, index) => {
        if (index % size === 0) {
            result.push([]);
        }
        result[result.length - 1].push(item);
        return result;
    }, []);
};
export default chunk;
