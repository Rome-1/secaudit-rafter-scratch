/**
 * Utility type to create deeply partial versions of object types,
 * making all properties and nested properties optional recursively.
 */
export type DeepPartial<T> = T extends object
    ? {
          [P in keyof T]?: DeepPartial<T[P]>;
      }
    : T;