import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Artifact } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({ selector: 'app-studio-draft-detail', standalone: true, imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent], templateUrl: './studio-draft-detail.component.html', styleUrl: './studio-draft-detail.component.scss' })
export class StudioDraftDetailComponent implements OnInit, OnDestroy {
  draft?: Artifact; loading = true; failed = false; private draftId = ''; private readonly subscriptions = new Subscription();
  constructor(private readonly route: ActivatedRoute, private readonly platform: V2PlatformService) {}
  ngOnInit(): void { this.draftId = this.route.snapshot.paramMap.get('artifactId') || ''; this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }
  load(): void { if (!this.draftId) { this.failed = true; this.loading = false; return; } this.loading = true; this.failed = false; this.subscriptions.add(this.platform.getArtifact(this.draftId).subscribe({ next: draft => { this.draft = draft; this.loading = false; }, error: () => { this.failed = true; this.loading = false; } })); }
  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase()); }
}
