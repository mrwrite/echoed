import { Meta, StoryObj } from '@storybook/angular';
import { EchoDataListComponent } from './echo-data-list.component';

const meta: Meta<EchoDataListComponent> = {
  title: 'EchoEd/Components/Echo Data List',
  component: EchoDataListComponent,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<EchoDataListComponent>;

export const Roster: Story = {
  args: {
    title: 'Class roster',
    itemLabel: 'learner',
    itemLabelPlural: 'learners',
    columns: [
      { key: 'name', label: 'Learner', primary: true },
      { key: 'email', label: 'Email' },
      { key: 'status', label: 'Status' },
    ],
    items: [
      { id: 1, values: { name: 'Ada Lovelace', email: 'ada@example.org', status: 'Active' } },
      { id: 2, values: { name: 'Mary Jackson', email: 'mary@example.org', status: 'Invited' } },
    ],
    actions: [{ id: 'open', label: 'Open' }],
  },
};
