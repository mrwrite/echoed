import { Meta, StoryObj } from '@storybook/angular';
import { EchoTooltipComponent } from './echo-tooltip.component';

const meta: Meta<EchoTooltipComponent> = {
  title: 'EchoEd/Components/Echo Tooltip',
  component: EchoTooltipComponent,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<EchoTooltipComponent>;

export const Top: Story = {
  args: {
    text: 'Tooltip on top',
    position: 'top',
  },
  render: (args) => ({
    component: EchoTooltipComponent,
    props: args,
    template: `
      <app-echo-tooltip [text]="text" [position]="position">
        <button class="bg-primary text-white px-4 py-2 rounded">Hover me</button>
      </app-echo-tooltip>
    `
  }),
};

export const Right: Story = {
  args: {
    text: 'Tooltip on right',
    position: 'right',
  },
  render: Top.render,
};

export const Left: Story = {
    args: {
        text: 'Tooltip on left',
        position: 'left',
    },
    render: Top.render,
}

export const Bottom: Story = {
    args: {
        text: 'Tooltip on bottom',
        position: 'bottom',
    },
    render: Top.render, 
}