/*
Copyright 2024 New Vector Ltd.

SPDX-License-Identifier: AGPL-3.0-only OR GPL-3.0-only
Please see LICENSE files in the repository root for full details.
*/

import { ReactNode } from "react";
import { Root, createRoot } from "react-dom/client";
import { flushSync } from "react-dom";

/**
 * A utility class to manage multiple independent React roots, providing a consistent
 * interface for rendering and unmounting dynamic subtrees.
 */
export class ReactRootManager {
    private roots = new Map<Element, Root>();

    /**
     * Renders the given children into the specified DOM element using createRoot
     * and tracks it for later unmounting.
     *
     * @param children - The React components to render
     * @param element - The DOM element to render into
     */
    public render(children: ReactNode, element: Element): void {
        let root = this.roots.get(element);
        if (!root) {
            root = createRoot(element);
            this.roots.set(element, root);
        }
        // Use flushSync to ensure synchronous rendering for backward compatibility
        flushSync(() => {
            root!.render(children);
        });
    }

    /**
     * Unmounts all managed React roots and clears their associated container elements
     * to ensure proper cleanup.
     */
    public unmount(): void {
        this.roots.forEach((root, element) => {
            root.unmount();
        });
        this.roots.clear();
    }

    /**
     * Returns the list of DOM elements currently used as containers for mounted roots,
     * useful for deduplication or external reference.
     *
     * @returns Array of DOM elements that have React roots mounted
     */
    public get elements(): Element[] {
        return Array.from(this.roots.keys());
    }
}
