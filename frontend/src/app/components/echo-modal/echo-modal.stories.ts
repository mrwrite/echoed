import { Meta, StoryObj } from '@storybook/angular';
import { EchoModalComponent } from './echo-modal.component';

const meta: Meta<EchoModalComponent> = {
  title: 'EchoEd/Components/Echo Modal',
  component: EchoModalComponent,
  args: {
    open: true,
    title: 'Delete Item',
    description: 'Are you sure you want to delete this item?',
  },
};

export default meta;
type Story = StoryObj<EchoModalComponent>;

export const Default: Story = {};

export const LongDescription: Story = {
  args: {
    description: 'This action will permanently delete the selected item. Please confirm if you wish to proceed.',
  },
};
