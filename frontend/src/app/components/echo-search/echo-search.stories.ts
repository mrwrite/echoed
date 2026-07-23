import { Meta, StoryObj } from '@storybook/angular';
import { EchoSearchComponent } from './echo-search.component';

const meta: Meta<EchoSearchComponent> = {
  title: 'EchoEd/Components/Echo Search',
  component: EchoSearchComponent,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<EchoSearchComponent>;

export const WithResults: Story = {
  args: {
    label: 'Search learners',
    placeholder: 'Name or email',
    value: 'Ada',
    resultCount: 3,
  },
};

export const Loading: Story = {
  args: {
    label: 'Search courses',
    loading: true,
    hint: 'Updating available learning.',
  },
};
