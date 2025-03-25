import type { StorybookConfig } from '@storybook/angular';

const config: StorybookConfig = {
  "stories": ['../src/app/components/**/*.stories.ts'],
  "addons": [
    "@storybook/addon-essentials",
    "@storybook/addon-onboarding",
    "@chromatic-com/storybook",
    "@storybook/addon-interactions",
    "@storybook/addon-mdx-gfm"
  ],  
  framework: {
    name: '@storybook/angular',
    options: {},
  },
};

export default config;