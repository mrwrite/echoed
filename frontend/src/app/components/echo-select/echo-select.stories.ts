import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { EchoSelectComponent } from './echo-select.component';
import { FormsModule } from '@angular/forms';

const meta: Meta<EchoSelectComponent> = {
  title: 'EchoEd/Components/Echo Select',
  component: EchoSelectComponent,
  tags: ['autodocs'],
  decorators: [
    moduleMetadata({
      imports: [FormsModule], // Needed for ngModel binding
    }),
  ],
};

export default meta;
type Story = StoryObj<EchoSelectComponent>;

export const Default: Story = {
  args: {
    label: 'Choose a fruit: ',
    options: ['Apple', 'Banana', 'Cherry'],
    value: 'Banana',
  },
};

export const WithObjects: Story = {
  args: {
    label: 'Choose a plan: ',
    options: [
      { label: 'Basic', value: 'basic' },
      { label: 'Pro', value: 'pro' },
      { label: 'Enterprise', value: 'enterprise' },
    ],
    value: 'pro',
  },
};

export const Disabled: Story = {
  args: {
    label: 'Disabled select: ',
    options: ['Option 1', 'Option 2'],
    disabled: true,
  },
};

export const ValidationError: Story = {
  args: { label: 'Organization role', options: ['Teacher', 'Student'], required: true, error: 'Choose a role.' },
};
