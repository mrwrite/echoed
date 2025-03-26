import { Meta, StoryObj } from '@storybook/angular';
import { EchoBadgeComponent } from './echo-badge.component';

const meta: Meta<EchoBadgeComponent> = {
  title: 'EchoEd/Components/Echo Badge',
  component: EchoBadgeComponent,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'accent', 'warn', 'neutral'],
    },
  },
};

export default meta;
type Story = StoryObj<EchoBadgeComponent>;

export const Primary: Story = {
  args: {
    label: 'Primary',
    variant: 'primary',
  },
};

export const Accent: Story = {
  args: {
    label: 'Accent',
    variant: 'accent',
  },
};

export const Warn: Story = {
  args: {
    label: 'Warning',
    variant: 'warn',
  },
};

export const Neutral: Story = {
  args: {
    label: 'Neutral',
    variant: 'neutral',
  },
};
