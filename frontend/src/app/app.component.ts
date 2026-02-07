import { Component, Inject, OnInit, Renderer2 } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { EchoToastContainerComponent } from './components/echo-toast-container/echo-toast-container.component';
import { DemoTourOverlayComponent } from './components/demo-tour-overlay/demo-tour-overlay.component';
import { PreferencesService } from './services/preferences.service';
import { AuthService } from './services/auth.service';
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, EchoToastContainerComponent, DemoTourOverlayComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'echoed-frontend';

  constructor(
    private authService: AuthService,
    private preferencesService: PreferencesService,
    private renderer: Renderer2,
    @Inject(DOCUMENT) private document: Document
  ) {}

  ngOnInit(): void {
    if (this.authService.isLoggedIn()) {
      this.preferencesService.loadPreferences().subscribe(prefs => {
        localStorage.setItem('locale', prefs.locale);
        if (prefs.reading_level_mode === 'large-type' || prefs.large_text) {
          this.renderer.addClass(this.document.body, 'large-type');
        } else {
          this.renderer.removeClass(this.document.body, 'large-type');
        }
      });
    }
  }
}
