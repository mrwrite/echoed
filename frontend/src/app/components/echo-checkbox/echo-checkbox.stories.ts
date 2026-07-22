import { Meta, StoryObj } from '@storybook/angular';
import { EchoCheckboxComponent } from './echo-checkbox.component';

const meta: Meta<EchoCheckboxComponent> = {
  title: 'EchoEd/Components/Echo Checkbox',
  component: EchoCheckboxComponent,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<EchoCheckboxComponent>;

export const Default: Story = {
  args: {
    label: 'I agree to the terms',
    checked: false,
  },
};

export const ValidationError: Story = {
  args: { label: 'I agree to the community guidelines', required: true, error: 'Agreement is required.' },
};
