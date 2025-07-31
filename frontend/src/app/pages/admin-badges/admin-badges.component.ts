import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BadgesService } from '../../services/badges.service';
import { Badge } from '../../models/badge';

@Component({
  selector: 'admin-badges-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-badges.component.html',
  styleUrl: './admin-badges.component.scss'
})
export class AdminBadgesComponent implements OnInit {
  badges: Badge[] = [];
  badgeForm: FormGroup;

  constructor(private badgesService: BadgesService, private fb: FormBuilder) {
    this.badgeForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      image_url: ['']
    });
  }

  ngOnInit(): void {
    this.loadBadges();
  }

  loadBadges() {
    this.badgesService.getBadges().subscribe(badges => (this.badges = badges));
  }

  onSubmit() {
    if (this.badgeForm.invalid) return;
    this.badgesService.createBadge(this.badgeForm.value).subscribe(badge => {
      this.badges.push(badge);
      this.badgeForm.reset();
    });
  }
}
