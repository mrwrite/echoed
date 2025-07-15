import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { EchoToastContainerComponent } from './components/echo-toast-container/echo-toast-container.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, EchoToastContainerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'echoed-frontend';
}
