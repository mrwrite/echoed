import { Meta, StoryObj } from '@storybook/angular';
import { EchoToggleComponent } from './echo-toggle.component';

const meta: Meta<EchoToggleComponent> = {
  title: 'EchoEd/Components/Echo Toggle',
  component: EchoToggleComponent,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<EchoToggleComponent>;

export const Default: Story = {
  args: {
    label: 'Enable Notifications',
    checked: true,
  },
};

export const Disabled: Story = {
  args: { label: 'Email notifications', checked: false, disabled: true, hint: 'Managed by your organization.' },
};
