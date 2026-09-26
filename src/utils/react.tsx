/*
Copyright 2024 New Vector Ltd.

SPDX-License-Identifier: AGPL-3.0-only OR GPL-3.0-only
Please see LICENSE files in the repository root for full details.
*/

import React, { ReactNode } from "react";
import { createRoot, Root } from "react-dom/client";

/**
 * ReactRootManager
 * A small utility to manage multiple independent React roots mounted into arbitrary DOM elements.
 * It provides a consistent interface for rendering and unmounting dynamic subtrees.
 */
export class ReactRootManager {
    private roots: Array<{ root: Root; element: Element }> = [];

    /**
     * Renders the given `children` into the provided `element` using React 18 `createRoot`.
     * The created root is tracked for later unmounting.
     */
    public render(children: ReactNode, element: Element): void {
        // If we already manage a root for this element, just re-render.
        const existing = this.roots.find((r) => r.element === element);
        if (existing) {
            existing.root.render(children);
            return;
        }
        const root = createRoot(element);
        root.render(children);
        this.roots.push({ root, element });
    }

    /**
     * Unmounts all managed React roots and clears their associated elements.
     */
    public unmount(): void {
        for (const { root } of this.roots) {
            try {
                root.unmount();
            } catch {
                // noop - best-effort cleanup
            }
        }
        this.roots = [];
    }

    /**
     * Provides external access to the container elements used by managed roots.
     */
    public get elements(): Element[] {
        return this.roots.map((r) => r.element);
    }
}

export default ReactRootManager;
