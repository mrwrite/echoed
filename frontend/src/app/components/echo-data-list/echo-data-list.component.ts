import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface EchoDataListColumn {
  key: string;
  label: string;
  primary?: boolean;
  mobile?: boolean;
}

export interface EchoDataListItem {
  id: string | number;
  values: Record<string, string | number | null | undefined>;
}

export interface EchoDataListAction {
  id: string;
  label: string;
  danger?: boolean;
  disabled?: (item: EchoDataListItem) => boolean;
  accessibleLabel?: (item: EchoDataListItem) => string;
}

export interface EchoDataListActionEvent {
  actionId: string;
  item: EchoDataListItem;
}

@Component({
  selector: 'app-echo-data-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="ee-data-list" [attr.aria-labelledby]="headingId">
      <div class="ee-data-list__summary">
        <h2 [id]="headingId">{{ title }}</h2>
        <p role="status" aria-live="polite">{{ items.length }} {{ items.length === 1 ? itemLabel : itemLabelPlural }}</p>
      </div>

      <div *ngIf="items.length; else emptyTemplate">
        <div class="ee-data-list__table-wrap">
          <table class="ee-data-list__table">
            <caption>{{ caption || title }}</caption>
            <thead><tr><th *ngFor="let column of columns" scope="col">{{ column.label }}</th><th *ngIf="actions.length" scope="col">Actions</th></tr></thead>
            <tbody>
              <tr *ngFor="let item of items; trackBy: trackItem">
                <td *ngFor="let column of columns" [attr.data-label]="column.label">{{ displayValue(item, column) }}</td>
                <td *ngIf="actions.length"><div class="ee-data-list__actions"> <ng-container *ngFor="let action of actions"><button
                  type="button" class="ee-data-list__action" [class.ee-data-list__action--danger]="action.danger"
                  [disabled]="isDisabled(action, item)" [attr.aria-label]="actionLabel(action, item)"
                  (click)="selectAction(action, item)">{{ action.label }}</button></ng-container></div></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="ee-data-list__cards" role="list" [attr.aria-label]="caption || title">
          <article *ngFor="let item of items; trackBy: trackItem" class="ee-data-list__card" role="listitem">
            <h3>{{ displayValue(item, primaryColumn) }}</h3>
            <dl>
              <ng-container *ngFor="let column of mobileColumns">
                <div><dt>{{ column.label }}</dt><dd>{{ displayValue(item, column) }}</dd></div>
              </ng-container>
            </dl>
            <div *ngIf="actions.length" class="ee-data-list__actions"><button *ngFor="let action of actions" type="button"
              class="ee-data-list__action" [class.ee-data-list__action--danger]="action.danger" [disabled]="isDisabled(action, item)"
              [attr.aria-label]="actionLabel(action, item)" (click)="selectAction(action, item)">{{ action.label }}</button></div>
          </article>
        </div>
      </div>

      <ng-template #emptyTemplate><div class="ee-data-list__empty" role="status"><strong>{{ emptyTitle }}</strong><p>{{ emptyMessage }}</p></div></ng-template>
    </section>
  `,
})
export class EchoDataListComponent {
  private static nextId = 0;
  readonly headingId = `echo-data-list-${++EchoDataListComponent.nextId}-heading`;
  @Input() title = 'Records';
  @Input() caption = '';
  @Input() columns: EchoDataListColumn[] = [];
  @Input() items: EchoDataListItem[] = [];
  @Input() actions: EchoDataListAction[] = [];
  @Input() itemLabel = 'record';
  @Input() itemLabelPlural = 'records';
  @Input() emptyTitle = 'No records yet';
  @Input() emptyMessage = 'Records will appear here when they are available.';
  @Output() actionSelected = new EventEmitter<EchoDataListActionEvent>();

  get primaryColumn(): EchoDataListColumn {
    return this.columns.find(column => column.primary) || this.columns[0] || { key: 'id', label: 'Record' };
  }

  get mobileColumns(): EchoDataListColumn[] {
    return this.columns.filter(column => column !== this.primaryColumn && column.mobile !== false);
  }

  displayValue(item: EchoDataListItem, column: EchoDataListColumn): string {
    const value = item.values[column.key];
    return value === null || value === undefined || value === '' ? 'Not available' : String(value);
  }

  actionLabel(action: EchoDataListAction, item: EchoDataListItem): string {
    return action.accessibleLabel?.(item) || `${action.label} ${this.displayValue(item, this.primaryColumn)}`;
  }

  isDisabled(action: EchoDataListAction, item: EchoDataListItem): boolean {
    return action.disabled?.(item) ?? false;
  }

  selectAction(action: EchoDataListAction, item: EchoDataListItem): void {
    if (!this.isDisabled(action, item)) this.actionSelected.emit({ actionId: action.id, item });
  }

  trackItem(_index: number, item: EchoDataListItem): string | number { return item.id; }
}
