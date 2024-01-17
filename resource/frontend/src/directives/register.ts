import type { App } from 'vue';
import Markdown from './markdown';

export function registerDirectives(app: App): void {
    app.directive('md', Markdown);
}