import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { EchoButtonComponent } from './echo-button.component';
import { CommonModule } from '@angular/common';


const meta: Meta<EchoButtonComponent> = {
  title: 'EchoEd/Components/Echo Button',
  component: EchoButtonComponent,
  decorators: [
    moduleMetadata({
      imports: [CommonModule, EchoButtonComponent],
    }),
  ],
  tags: ['autodocs'],
  argTypes: {
    color: {
      control: 'select',
      options: ['primary', 'accent', 'warn'],
    },
    disabled: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<EchoButtonComponent>;

export const Primary: Story = {
  args: {
    label: 'Primary Button',
    color: 'primary',
  },
};

export const Accent: Story = {
  args: {
    label: 'Accent Button',
    color: 'accent',
  },
};

export const Warn: Story = {
  args: {
    label: 'Warning Button',
    color: 'warn',
  },
};

export const Disabled: Story = {
  args: {
    label: 'Disabled Button',
    color: 'primary',
    disabled: true,
  },
};