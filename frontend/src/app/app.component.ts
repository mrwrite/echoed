import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { EchoToastContainerComponent } from './components/echo-toast-container/echo-toast-container.component';
import { DemoTourOverlayComponent } from './components/demo-tour-overlay/demo-tour-overlay.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, EchoToastContainerComponent, DemoTourOverlayComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'echoed-frontend';
}
