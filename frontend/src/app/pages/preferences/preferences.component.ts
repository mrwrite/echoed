import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PreferencesService } from '../../services/preferences.service';
import { UserPreferences } from '../../models/user-preferences';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-preferences',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './preferences.component.html',
  styleUrl: './preferences.component.scss'
})
export class PreferencesComponent implements OnInit {
  preferences: UserPreferences = {
    locale: 'en',
    timezone: '',
    theme: 'system',
    large_text: false,
    dyslexia_font: false,
    preferred_mode: 'student',
    reading_level_mode: 'standard'
  };

  constructor(private preferencesService: PreferencesService, private toastService: ToastService) {}

  ngOnInit(): void {
    this.preferencesService.loadPreferences().subscribe(prefs => {
      this.preferences = { ...prefs };
    });
  }

  save(): void {
    this.preferencesService.updatePreferences(this.preferences).subscribe(() => {
      localStorage.setItem('locale', this.preferences.locale);
      this.toastService.show('Preferences saved!', 'success');
    });
  }
}
