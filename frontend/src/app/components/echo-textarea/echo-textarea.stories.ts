import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { EchoTextareaComponent } from './echo-textarea.component';
import { FormsModule } from '@angular/forms';

const meta: Meta<EchoTextareaComponent> = {
  title: 'EchoEd/Components/Echo Textarea',
  component: EchoTextareaComponent,
  tags: ['autodocs'],
  decorators: [
    moduleMetadata({
      imports: [FormsModule],
    }),
  ],
};

export default meta;
type Story = StoryObj<EchoTextareaComponent>;

export const Default: Story = {
  args: {
    label: 'Message: ',
    placeholder: 'Enter your message...',
    value: '',
  },
};

export const WithValue: Story = {
  args: {
    label: 'Notes: ',
    value: 'This is a pre-filled textarea.',
  },
};

export const Disabled: Story = {
  args: {
    label: 'Disabled: ',
    placeholder: 'You can’t type here',
    disabled: true,
  },
};
