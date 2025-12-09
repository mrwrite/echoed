import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

export interface TimelineEvent {
  date: string;
  title: string;
  description: string;
}

@Component({
  selector: 'app-timeline',
  standalone: true,
  imports: [CommonModule],
  template: `
    <ul class="space-y-4">
      <li *ngFor="let event of events" class="border-b pb-2">
        <div class="font-semibold">{{ event.date }} - {{ event.title }}</div>
        <div class="text-sm text-gray-600">{{ event.description }}</div>
      </li>
    </ul>
  `
})
export class TimelineComponent implements OnInit {
  events: TimelineEvent[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http
      .get<TimelineEvent[]>('assets/events.json')
      .subscribe(data => (this.events = data));
  }
}
