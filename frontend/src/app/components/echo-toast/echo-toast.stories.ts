import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { EchoToastComponent } from './echo-toast.component';

const meta: Meta<EchoToastComponent> = {
  title: 'EchoEd/Components/Toast',
  component: EchoToastComponent,
  decorators: [
    moduleMetadata({
      imports: [],
    }),
  ],
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['info', 'warn', 'error', 'success'],
    },
    duration: {
      control: { type: 'number' },
    }
  }
};

export default meta;
type Story = StoryObj<EchoToastComponent>;

export const Info: Story = {
  args: {
    message: 'This is an info toast.',
    type: 'info',
    duration: 3000,
  }
};

export const Warn: Story = {
  args: {
    message: 'This is a warning toast.',
    type: 'warn',
    duration: 3000,
  }
};

export const Error: Story = {
  args: {
    message: 'This is an error toast.',
    type: 'error',
    duration: 3000,
  }
};

export const Success: Story = {
  args: {
    message: 'This is a success toast!',
    type: 'success',
    duration: 3000,
  }
};

export const Persistent: Story = {
  args: {
    message: 'This toast will not auto-dismiss.',
    type: 'info',
    duration: 0, // 0 disables auto-dismiss
  }
};
