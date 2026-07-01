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
      title: 'Culturally grounded curriculum',
      description: 'Stories, primary sources, and activities that celebrate African and African-American history with respect and rigor.',
      kicker: '01'
    },
    {
      title: 'Student progress intelligence',
      description: 'Live visibility into mastery, pacing, and engagement for every learner.',
      kicker: '02'
    },
    {
      title: 'Built for any learning model',
      description: 'Perfect for private schools, microschools, homeschool families, and community learning pods.',
      kicker: '03'
    },
  ];

  animatedCards = [
    { label: 'Educator-first', value: 'Admin & teacher control centers', detail: 'Curriculum tools, cohorts, and progress views' },
    { label: 'Learner delight', value: 'Immersive lessons & achievements', detail: 'Story-led lessons, badges, and momentum' },
    { label: 'Families', value: 'Simple onboarding', detail: 'Parent-friendly account creation and access' },
    { label: 'Middle + HS', value: 'Coming soon', detail: 'Upper grade pathways are already in motion' },
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
    { title: 'Future Grades', detail: 'Middle School Suites expanding into grades 6-8 with civics-rich projects and debates.' },
    { title: 'High School Pathways', detail: 'College-ready modules with primary-source analysis and AP-aligned rigor.' },
  ];

  audienceCards = [
    'K-5 content live today',
    'Middle & High School in motion',
  ];
}
