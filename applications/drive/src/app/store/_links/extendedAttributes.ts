import { CryptoProxy, PrivateKeyReference, PublicKeyReference, VERIFICATION_STATUS } from '@proton/crypto';
import { FILE_CHUNK_SIZE } from '@proton/shared/lib/drive/constants';
import { decryptSigned } from '@proton/shared/lib/keys/driveKeys';
import { DeepPartial } from '../../utils/type/DeepPartial';

interface ExtendedAttributes {
    Common: {
        ModificationTime?: string;
        Size?: number;
        BlockSizes?: number[];
        Digests?: {
            [key: string]: string;
        };
    };
    Media?: {
        Width: number;
        Height: number;
    };
}

interface ParsedExtendedAttributes {
    Common: {
        ModificationTime?: number;
        Size?: number;
        BlockSizes?: number[];
        Digests?: {
            [key: string]: string;
        };
    };
    Media?: {
        Width: number;
        Height: number;
    };
}

export type MaybeExtendedAttributes = DeepPartial<ExtendedAttributes>;

export interface XAttrCreateParams {
    file: File;
    digests?: {
        sha1: string;
    };
    media?: {
        width: number;
        height: number;
    };
}

export async function encryptFolderExtendedAttributes(
    modificationTime: Date,
    nodePrivateKey: PrivateKeyReference,
    addressPrivateKey: PrivateKeyReference
) {
    const xattr = createFolderExtendedAttributes(modificationTime);
    return encryptExtendedAttributes(xattr, nodePrivateKey, addressPrivateKey);
}

export function createFolderExtendedAttributes(modificationTime: Date): ExtendedAttributes {
    return {
        Common: {
            ModificationTime: dateToIsoString(modificationTime),
        },
    };
}

// New signature using parameter object
export async function encryptFileExtendedAttributes(
    params: XAttrCreateParams,
    nodePrivateKey: PrivateKeyReference,
    addressPrivateKey: PrivateKeyReference
): Promise<string>;

// Legacy signature for backward compatibility
export async function encryptFileExtendedAttributes(
    file: File,
    nodePrivateKey: PrivateKeyReference,
    addressPrivateKey: PrivateKeyReference,
    media?: {
        width: number;
        height: number;
    },
    digests?: {
        sha1: string;
    }
): Promise<string>;

export async function encryptFileExtendedAttributes(
    paramsOrFile: XAttrCreateParams | File,
    nodePrivateKey: PrivateKeyReference,
    addressPrivateKey: PrivateKeyReference,
    media?: {
        width: number;
        height: number;
    },
    digests?: {
        sha1: string;
    }
): Promise<string> {
    let xattr: ExtendedAttributes;
    
    if ('file' in paramsOrFile) {
        // New parameter object signature
        xattr = createFileExtendedAttributes(paramsOrFile as XAttrCreateParams);
    } else {
        // Legacy signature
        xattr = createFileExtendedAttributes(paramsOrFile as File, media, digests);
    }
    
    return encryptExtendedAttributes(xattr, nodePrivateKey, addressPrivateKey);
}

// New signature using parameter object
export function createFileExtendedAttributes(params: XAttrCreateParams): ExtendedAttributes;

// Legacy signature for backward compatibility
export function createFileExtendedAttributes(
    file: File,
    media?: {
        width: number;
        height: number;
    },
    digests?: {
        sha1: string;
    }
): ExtendedAttributes;

export function createFileExtendedAttributes(
    paramsOrFile: XAttrCreateParams | File,
    media?: {
        width: number;
        height: number;
    },
    digests?: {
        sha1: string;
    }
): ExtendedAttributes {
    // Handle both new parameter object and legacy signature
    let file: File;
    let mediaParams: { width: number; height: number } | undefined;
    let digestParams: { sha1: string } | undefined;

    if ('file' in paramsOrFile) {
        // New parameter object signature
        const params = paramsOrFile as XAttrCreateParams;
        file = params.file;
        mediaParams = params.media;
        digestParams = params.digests;
    } else {
        // Legacy signature
        file = paramsOrFile as File;
        mediaParams = media;
        digestParams = digests;
    }
    
    // Calculate block sizes: partition file size into consecutive FILE_CHUNK_SIZE blocks
    // plus a final remainder entry when non-zero; omit remainder when zero
    const blockSizes = new Array(Math.floor(file.size / FILE_CHUNK_SIZE));
    blockSizes.fill(FILE_CHUNK_SIZE);
    
    const remainder = file.size % FILE_CHUNK_SIZE;
    if (remainder > 0) {
        blockSizes.push(remainder);
    }

    // Normalize digest names to canonical keys (e.g., sha1 → SHA1)
    const normalizedDigests = digestParams ? normalizeDigests(digestParams) : undefined;

    return {
        Common: {
            ModificationTime: dateToIsoString(new Date(file.lastModified)),
            Size: file.size,
            BlockSizes: blockSizes,
            Digests: normalizedDigests,
        },
        Media: mediaParams
            ? {
                  Width: mediaParams.width,
                  Height: mediaParams.height,
              }
            : undefined,
    };
}

async function encryptExtendedAttributes(
    xattr: ExtendedAttributes,
    nodePrivateKey: PrivateKeyReference,
    addressPrivateKey: PrivateKeyReference
) {
    const xattrString = JSON.stringify(xattr);
    const { message } = await CryptoProxy.encryptMessage({
        textData: xattrString,
        encryptionKeys: nodePrivateKey,
        signingKeys: addressPrivateKey,
        compress: true,
    });
    return message;
}

export async function decryptExtendedAttributes(
    encryptedXAttr: string,
    nodePrivateKey: PrivateKeyReference,
    addressPublicKey: PublicKeyReference | PublicKeyReference[]
): Promise<{ xattrs: ParsedExtendedAttributes; verified: VERIFICATION_STATUS }> {
    const { data: xattrString, verified } = await decryptSigned({
        armoredMessage: encryptedXAttr,
        privateKey: nodePrivateKey,
        publicKey: addressPublicKey,
    });
    return {
        xattrs: parseExtendedAttributes(xattrString),
        verified,
    };
}

function normalizeDigests(digests: { sha1: string }): { [key: string]: string } {
    const normalized: { [key: string]: string } = {};
    if (digests.sha1) {
        normalized.SHA1 = digests.sha1;
    }
    return normalized;
}

export function parseExtendedAttributes(xattrString: string): ParsedExtendedAttributes {
    let xattr: MaybeExtendedAttributes = {};
    try {
        xattr = JSON.parse(xattrString);
    } catch (err) {
        console.warn(`XAttr "${xattrString}" is not valid JSON`);
    }
    return {
        Common: {
            ModificationTime: parseModificationTime(xattr),
            Size: parseSize(xattr),
            BlockSizes: parseBlockSizes(xattr),
            Digests: parseDigests(xattr),
        },
        Media: parseMedia(xattr),
    };
}

export function parseModificationTime(xattr: MaybeExtendedAttributes): number | undefined {
    const modificationTime = xattr?.Common?.ModificationTime;
    if (modificationTime === undefined) {
        return undefined;
    }
    const modificationDate = new Date(modificationTime);
    // This is the best way to check if date is "Invalid Date". :shrug:
    if (JSON.stringify(modificationDate) === 'null') {
        console.warn(`XAttr modification time "${modificationTime}" is not valid`);
        return undefined;
    }
    const modificationTimestamp = Math.trunc(modificationDate.getTime() / 1000);
    if (Number.isNaN(modificationTimestamp)) {
        console.warn(`XAttr modification time "${modificationTime}" is not valid`);
        return undefined;
    }
    return modificationTimestamp;
}

export function parseSize(xattr: MaybeExtendedAttributes): number | undefined {
    const size = xattr?.Common?.Size;
    if (size === undefined) {
        return undefined;
    }
    if (typeof size !== 'number') {
        console.warn(`XAttr file size "${size}" is not valid`);
        return undefined;
    }
    return size;
}

export function parseBlockSizes(xattr: MaybeExtendedAttributes): number[] | undefined {
    const blockSizes = xattr?.Common?.BlockSizes;
    if (blockSizes === undefined) {
        return undefined;
    }
    if (!Array.isArray(blockSizes)) {
        console.warn(`XAttr block sizes "${blockSizes}" is not valid`);
        return undefined;
    }
    if (!blockSizes.every((item) => typeof item === 'number')) {
        console.warn(`XAttr block sizes "${blockSizes}" is not valid`);
        return undefined;
    }
    return blockSizes;
}

export function parseMedia(xattr: MaybeExtendedAttributes): { Width: number; Height: number } | undefined {
    const media = xattr?.Media;
    if (media === undefined || media.Width === undefined || media.Height === undefined) {
        return undefined;
    }
    const width = media.Width;
    if (typeof width !== 'number') {
        console.warn(`XAttr media width "${width}" is not valid`);
        return undefined;
    }
    const height = media.Height;
    if (typeof height !== 'number') {
        console.warn(`XAttr media height "${height}" is not valid`);
        return undefined;
    }
    return {
        Width: width,
        Height: height,
    };
}

export function parseDigests(xattr: MaybeExtendedAttributes): { [key: string]: string } | undefined {
    const digests = xattr?.Common?.Digests;
    if (!digests || Object.keys(digests).length === 0) {
        return undefined;
    }

    const normalized: { [key: string]: string } = {};
    
    // Normalize known digest names to canonical keys and filter out invalid ones
    for (const [key, value] of Object.entries(digests)) {
        if (typeof value === 'string') {
            // Normalize digest names (e.g., sha1 → SHA1)
            const canonicalKey = key.toUpperCase();
            normalized[canonicalKey] = value;
        } else {
            console.warn(`XAttr digest ${key} "${value}" is not valid`);
        }
    }

    return Object.keys(normalized).length > 0 ? normalized : undefined;
}

function dateToIsoString(date: Date) {
    const isDateValid = !Number.isNaN(date.getTime());
    return isDateValid ? date.toISOString() : undefined;
}
