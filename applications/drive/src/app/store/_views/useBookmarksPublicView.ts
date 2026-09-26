import { useMemo, useState, useEffect } from 'react';

import useLoading from '@proton/hooks/useLoading';

import usePublicToken from '../../hooks/drive/usePublicToken';
import { useDriveShareURLBookmarkingFeatureFlag } from '../_bookmarks';
import { useBookmarks } from '../_bookmarks/useBookmarks';
import { usePublicShare } from '../_shares';

export const useBookmarksPublicView = (customPassword?: string) => {
    const { user, isUserLoading } = usePublicShare();
    const { addBookmark, listBookmarks } = useBookmarks();
    const [bookmarksTokens, setBookmarksTokens] = useState<Set<string>>(new Set());
    const [isLoading, withLoading, setIsLoading] = useLoading(true);
    const isDriveShareUrlBookmarkingEnabled = useDriveShareURLBookmarkingFeatureFlag();
    const { token, urlPassword } = usePublicToken();

    useEffect(() => {
        if (!user || !isDriveShareUrlBookmarkingEnabled) {
            if (!isUserLoading) {
                setIsLoading(false);
            }
            return;
        }
        const abortControler = new AbortController();
        void withLoading(async () => {
            const bookmarks = await listBookmarks(abortControler.signal);
            setBookmarksTokens(new Set(bookmarks.map((bookmark) => bookmark.token.Token)));
        });
        return () => {
            abortControler.abort();
        };
    }, [user, isUserLoading, isDriveShareUrlBookmarkingEnabled]);

    const isAlreadyBookmarked = useMemo(() => {
        return bookmarksTokens.has(token);
    }, [bookmarksTokens, token]);

    const handleAddBookmark = async () => {
        const abortSignal = new AbortController().signal;
        await addBookmark(abortSignal, { token, urlPassword: urlPassword + customPassword });
        setBookmarksTokens((prevState) => new Set([...prevState, token]));
    };

    return {
        urlPassword,
        isLoading,
        isLoggedIn: !!user,
        addBookmark: handleAddBookmark,
        isAlreadyBookmarked,
    };
};
