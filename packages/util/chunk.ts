/**
 * Splits an array into consecutive chunks of a fixed size while maintaining element order.
 * If the input length isn't a multiple of size, the final chunk contains the remaining elements.
 * The function is pure (does not mutate the input), returns new arrays, uses a default chunk size
 * of 1 when size is omitted, and returns [] when called without an input list.
 * 
 * @param list - array to split (defaults to [] if omitted)
 * @param size - chunk size (defaults to 1)
 * @returns a new array of sub-arrays, each up to size elements, preserving input order
 */
const chunk = <T>(list: T[] = [], size = 1): T[][] => {
    if (size <= 0) {
        return [];
    }
    
    return list.reduce<T[][]>((res, item, index) => {
        if (index % size === 0) {
            res.push([]);
        }
        res[res.length - 1].push(item);
        return res;
    }, []);
};

export default chunk;