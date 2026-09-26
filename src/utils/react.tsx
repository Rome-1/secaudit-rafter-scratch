/*
Copyright 2024 New Vector Ltd.

SPDX-License-Identifier: AGPL-3.0-only OR GPL-3.0-only
Please see LICENSE files in the repository root for full details.
*/

import { ReactNode } from "react";
import { createRoot, Root } from "react-dom/client";

/**
 * A utility class to manage multiple independent React roots, providing a consistent interface 
 * for rendering and unmounting dynamic subtrees.
 * 
 * This allows full adoption of React 18's createRoot API while maintaining centralized
 * lifecycle management for dynamic components.
 */
export class ReactRootManager {
    private roots: Map<Element, Root> = new Map();

    /**
     * Renders the given children into the specified DOM element using createRoot 
     * and tracks it for later unmounting.
     * 
     * @param children - The React component(s) to render
     * @param element - The DOM element to render into
     */
    public render(children: ReactNode, element: Element): void {
        // Check if we already have a root for this element
        let root = this.roots.get(element);
        
        if (!root) {
            // Create a new root and track it
            root = createRoot(element);
            this.roots.set(element, root);
        }
        
        // Render the children into the root
        root.render(children);
    }

    /**
     * Unmounts all managed React roots and clears their associated container elements 
     * to ensure proper cleanup.
     */
    public unmount(): void {
        // Unmount all tracked roots
        this.roots.forEach((root) => {
            root.unmount();
        });
        
        // Clear the tracking map
        this.roots.clear();
    }

    /**
     * Returns the list of DOM elements currently used as containers for mounted roots,
     * useful for deduplication or external reference.
     */
    public get elements(): Element[] {
        return Array.from(this.roots.keys());
    }
}