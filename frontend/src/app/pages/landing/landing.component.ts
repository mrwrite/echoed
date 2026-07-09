import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.scss'
})
export class LandingComponent {
  readonly githubUrl = 'https://github.com/mrwrite/echoed';
  readonly contactEmail = 'support@echoed.com';

  readonly educatorMailto =
    'mailto:support@echoed.com?subject=EchoEd%20educator%20feedback&body=Hi%20EchoEd%20team%2C%0A%0AI%27m%20an%20educator%20and%20I%27d%20like%20to%20help%20review%20or%20shape%20the%20learning%20experience.%0A%0ARole%2Fcontext%3A%0AWhat%20I%27d%20like%20to%20review%3A%0AAvailability%20for%20a%20walkthrough%3A%0A';

  readonly interestMailto =
    'mailto:support@echoed.com?subject=I%20want%20to%20help%20with%20EchoEd&body=Hi%20EchoEd%20team%2C%0A%0AI%27d%20like%20to%20help%20with%20EchoEd.%0A%0AName%3A%0ARole%20%28educator%2C%20developer%2C%20student%2C%20organizer%2C%20other%29%3A%0AHow%20I%20want%20to%20help%3A%0AGitHub%2FLinkedIn%20%28optional%29%3A%0A';

  readonly featureHighlights = [
    {
      title: 'African and African-American history at the center',
      description: 'Lessons, activities, and source-aware learning flows designed around Black historical knowledge instead of treating it as an add-on.',
      kicker: '01'
    },
    {
      title: 'A real product educators can test',
      description: 'The live K-5 demo includes student, teacher, and admin experiences with progress, badges, courses, and guided learning paths.',
      kicker: '02'
    },
    {
      title: 'Open-source infrastructure for community ownership',
      description: 'Developers can inspect the code, improve the platform, strengthen accessibility, and help build tools educators actually need.',
      kicker: '03'
    },
  ];

  readonly platformSignals = [
    { label: 'Curriculum', value: 'Story-led K-5 lessons and activities', kicker: 'A' },
    { label: 'Dashboards', value: 'Student, teacher, and admin views', kicker: 'B' },
    { label: 'Progress', value: 'Badges, completion, and mastery signals', kicker: 'C' },
    { label: 'Roadmap', value: 'Middle and high school pathways in motion', kicker: 'D' },
  ];

  readonly educatorNeeds = [
    'Review lesson flow, tone, age fit, and classroom usefulness',
    'Suggest culturally responsive activities and discussion prompts',
    'Identify what teachers need before using this with learners',
    'Help form an advisory circle for Black-centered curriculum review',
  ];

  readonly developerNeeds = [
    'Improve Angular frontend workflows, responsive polish, and accessibility',
    'Contribute FastAPI backend features, tests, and data model hardening',
    'Add documentation, setup help, seed data, and good first issues',
    'Build curriculum tooling, review workflows, and demo reliability',
  ];

  readonly contributionPaths = [
    {
      title: 'Curriculum review',
      detail: 'Read a lesson, flag weak spots, suggest sources, and help the learning experience respect both rigor and culture.'
    },
    {
      title: 'Accessibility pass',
      detail: 'Test keyboard flow, contrast, labels, mobile layout, and learner-friendly states across the public demo.'
    },
    {
      title: 'Good first issues',
      detail: 'Help split small frontend, backend, documentation, and testing tasks so new contributors can start quickly.'
    },
    {
      title: 'Community outreach',
      detail: 'Introduce EchoEd to Black educator networks, HBCU programs, developer groups, and local learning communities.'
    },
  ];
}
