import { Meta, StoryObj } from '@storybook/angular';
import { EchoRadioGroupComponent } from './echo-radio-group.component';

const meta: Meta<EchoRadioGroupComponent> = {
  title: 'EchoEd/Components/Echo Radio Group',
  component: EchoRadioGroupComponent,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<EchoRadioGroupComponent>;

export const Default: Story = {
  args: {
    options: [
      { label: 'Option 1', value: 'option1' },
      { label: 'Option 2', value: 'option2' },
      { label: 'Option 3', value: 'option3' },
    ],
    selectedValue: 'option2',
    name: 'demo-group',
  },
};
