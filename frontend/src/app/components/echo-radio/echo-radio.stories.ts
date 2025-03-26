import { Meta, StoryObj } from '@storybook/angular';
import { EchoRadioComponent } from './echo-radio.component';

const meta: Meta<EchoRadioComponent> = {
  title: 'EchoEd/Components/Echo Radio',
  component: EchoRadioComponent,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<EchoRadioComponent>;

export const Selected: Story = {
  args: {
    label: 'Option A',
    value: 'a',
    name: 'demo',
    checked: true,
  },
};

export const Unselected: Story = {
  args: {
    label: 'Option B',
    value: 'b',
    name: 'demo',
    checked: false,
  },
};
