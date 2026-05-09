import { Meta, StoryObj } from '@storybook/angular';

import { EchoLoadingStateComponent } from './echo-loading-state.component';

const meta: Meta<EchoLoadingStateComponent> = {
  title: 'EchoEd/States/Loading State',
  component: EchoLoadingStateComponent,
  tags: ['autodocs'],
  argTypes: {
    density: {
      control: 'select',
      options: ['page', 'section', 'compact'],
    },
  },
};

export default meta;
type Story = StoryObj<EchoLoadingStateComponent>;

export const PageLoading: Story = {
  args: {
    density: 'page',
    centered: true,
    ariaLabel: 'page-loading',
    title: 'Preparing your workspace',
    body: 'We are resolving the latest authenticated and governed state for this screen.',
  },
};

export const SectionLoading: Story = {
  args: {
    density: 'section',
    ariaLabel: 'section-loading',
    title: 'Loading section content',
    body: 'This section is waiting for its latest data.',
  },
};

export const CompactLoading: Story = {
  args: {
    density: 'compact',
    ariaLabel: 'compact-loading',
    title: 'Loading navigation',
    body: 'Visible options will appear as soon as access is resolved.',
  },
};
