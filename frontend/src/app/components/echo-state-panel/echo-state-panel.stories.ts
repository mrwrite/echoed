import { Meta, StoryObj } from '@storybook/angular';

import { EchoStatePanelComponent } from './echo-state-panel.component';

const meta: Meta<EchoStatePanelComponent> = {
  title: 'EchoEd/States/State Panel',
  component: EchoStatePanelComponent,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['empty', 'error', 'unavailable', 'blocked', 'permission', 'success'],
    },
    align: {
      control: 'select',
      options: ['left', 'center'],
    },
  },
};

export default meta;
type Story = StoryObj<EchoStatePanelComponent>;

export const Empty: Story = {
  args: {
    variant: 'empty',
    eyebrow: 'No content yet',
    title: 'Nothing to show yet',
    body: 'This area will populate when content is available for the current context.',
  },
};

export const Error: Story = {
  args: {
    variant: 'error',
    eyebrow: 'Request failed',
    title: 'We could not load this view',
    body: 'Try again after the connection stabilizes or return to a known screen.',
    actionLabel: 'Retry',
  },
};

export const Unavailable: Story = {
  args: {
    variant: 'unavailable',
    eyebrow: 'Unavailable',
    title: 'This content is not currently available',
    body: 'The current context resolved successfully, but the requested content cannot be entered right now.',
  },
};

export const GovernedBlocked: Story = {
  args: {
    variant: 'blocked',
    eyebrow: 'Governed blocked state',
    title: 'This learning path is currently blocked',
    body: 'Learner delivery is waiting on a governed state change before it can continue.',
    actionLabel: 'Return to dashboard',
  },
};

export const PermissionDenied: Story = {
  args: {
    variant: 'permission',
    eyebrow: 'Access needed',
    title: 'This area is not available for your current role',
    body: 'Ask an organization owner if you need access.',
    context: 'Teacher · Freedom Learning Center',
    impact: 'No data was changed.',
    actionLabel: 'Return to classes',
    secondaryActionLabel: 'View profile',
  },
};

export const Success: Story = {
  args: { variant: 'success', title: 'Changes saved', body: 'Your organization name is up to date.', compact: true },
};
