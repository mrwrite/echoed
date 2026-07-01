import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.scss'
})
export class LandingComponent {
  featureHighlights = [
    {
      title: 'AI-native knowledge studio',
      description: 'Turn institutional expertise, source material, and instructional goals into governed products without losing human review.',
      kicker: 'Knowledge in'
    },
    {
      title: 'Governed learner delivery',
      description: 'Package learning experiences for schools, enterprises, parents, and teachers while existing lesson readiness stays authoritative.',
      kicker: 'Trust built in'
    },
    {
      title: 'Product health analytics',
      description: 'See product readiness, learner engagement, access, review, and knowledge pipeline signal from one premium workspace.',
      kicker: 'Operator clarity'
    },
  ];

  animatedCards = [
    { label: 'Workspace', value: 'Command center', detail: 'Projects, products, review, learners, analytics' },
    { label: 'Review', value: 'Human governed', detail: 'Artifact and product decisions stay separate from runtime publishing' },
    { label: 'Learner Portal', value: 'Product first', detail: 'Existing lessons continue through governed runtime paths' },
  ];

  walkthroughSteps = [
    'Open the workspace dashboard and frame the knowledge-to-product model.',
    'Show Product Studio as the flagship creation workflow.',
    'Open Review Center to explain trust, readiness, and governance.',
    'Switch to Learner Portal to show product delivery without changing runtime rules.',
    'Close with Analytics for product, access, review, and pipeline health.'
  ];

  testimonials = [
    {
      quote: 'EchoEd gives our leadership team a way to turn internal expertise into governed learning products without adding operational chaos.',
      name: 'Maya R.',
      role: 'Enterprise Enablement Leader'
    },
    {
      quote: 'The review model matters. We can see what is ready, what is blocked, and what learners can safely access.',
      name: 'Dr. Jonah P.',
      role: 'Independent School Director'
    },
    {
      quote: 'It feels less like an LMS and more like a product studio for trusted education experiences.',
      name: 'Elena W.',
      role: 'Parent and Learning Pod Organizer'
    }
  ];

  roadmap = [
    { title: 'Commercial packaging', detail: 'Public product pages, pricing placeholders, and branded product presentation.' },
    { title: 'Access expansion', detail: 'Manual grants today, with future memberships, teams, invitations, and enterprise seats.' },
    { title: 'AI generation execution', detail: 'Future controlled generation runs after review and governance foundations are stable.' },
  ];

  audienceCards = [
    'Investors evaluating a premium SaaS platform',
    'Schools modernizing curriculum operations',
    'Enterprises packaging internal knowledge',
    'Parents and teachers seeking trusted learner delivery',
  ];
}
