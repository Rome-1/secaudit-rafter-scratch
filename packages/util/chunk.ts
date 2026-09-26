/**
 * Divide an array into sub-arrays of a fixed chunk size
 *
 * Expected behavior:
 * - When called without an input list (undefined), return []
 * - When size is omitted or undefined, default to 1
 * - Preserve input order, do not mutate input
 */
const chunk = <T>(list: T[] = [], size = 1): T[][] => {
    return list.reduce<T[][]>((res, item, index) => {
        if (index % size === 0) {
            res.push([]);
        }
        res[res.length - 1].push(item);
        return res;
    }, []);
};

export default chunk;
