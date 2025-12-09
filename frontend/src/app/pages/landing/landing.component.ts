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
      icon: '📚'
    },
    {
      title: 'Student progress intelligence',
      description: 'Live visibility into mastery, pacing, and engagement for every learner.',
      icon: '✨'
    },
    {
      title: 'Built for any learning model',
      description: 'Perfect for private schools, microschools, homeschool families, and community learning pods.',
      icon: '🏫'
    },
  ];

  tourSteps = [
    'Immersive landing page',
    'Login & family onboarding',
    'Student dashboard',
    'Lesson experience',
    'Teacher & admin controls'
  ];

  testimonials = [
    {
      quote: 'EchoEd brings cultural relevance into every lesson. Our students feel seen and inspired.',
      name: 'Principal Amina O.',
      role: 'Independent School Leader'
    },
    {
      quote: 'As a homeschooling parent, I needed a trusted partner. EchoEd delivers depth and joy.',
      name: 'Danielle W.',
      role: 'Homeschool Collective Organizer'
    },
    {
      quote: 'It is the rare platform that respects history and gives me the data I need as an educator.',
      name: 'Mr. Carter',
      role: 'Middle School Humanities Teacher'
    }
  ];

  comingSoon = [
    { title: 'Middle School Suites', detail: 'Expanding into grades 6–8 with civics-rich projects and debates.' },
    { title: 'High School Pathways', detail: 'College-ready modules with primary-source analysis and AP-aligned rigor.' },
    { title: 'Community Archives', detail: 'District and family uploads curated into living history collections.' },
  ];
}
