import { Meta, StoryObj } from '@storybook/angular';
import { EchoInputComponent } from './echo-input.component';

const meta: Meta<EchoInputComponent> = {
  title: 'EchoEd/Components/Echo Input',
  component: EchoInputComponent,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<EchoInputComponent>;

export const Default: Story = {
  args: {
    label: 'Name',
    placeholder: 'Your name...',
    value: '',
  },
};

export const Password: Story = {
  args: {
    type: 'password',
    placeholder: 'Enter password',
  },
};

export const Disabled: Story = {
  args: {
    placeholder: 'Disabled input',
    disabled: true,
  },
};

export const ValidationError: Story = {
  args: { label: 'Email address', required: true, value: 'invalid', error: 'Enter a valid email address.' },
};
