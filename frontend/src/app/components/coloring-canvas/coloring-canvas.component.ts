import { Component, Input, ViewChild, ElementRef, AfterViewInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-coloring-canvas',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-2">
      <canvas #canvas class="border rounded w-full touch-none"></canvas>
      <div class="flex items-center gap-2">
        <button *ngFor="let c of colors"
          class="w-6 h-6 rounded-full border"
          [style.background]="c"
          (click)="currentColor = c"
        ></button>
        <button class="px-2 py-1 text-xs border rounded" (click)="clearCanvas()">Clear</button>
      </div>
    </div>
  `
})
export class ColoringCanvasComponent implements AfterViewInit, OnChanges {
  @Input() imageUrl: string = '';
  @ViewChild('canvas', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  colors = ['#ff0000', '#00a652', '#0057ff', '#ffc800', '#000000'];
  currentColor = this.colors[0];

  private ctx!: CanvasRenderingContext2D;
  private drawing = false;

  private resolveUrl(url: string): string {
    if (!url) {
      return '';
    }
    const hasProtocol = /^https?:\/\//i.test(url);
    if (hasProtocol) {
      return url;
    }
    const normalized = url.startsWith('/') ? url : `/${url}`;
    return `${environment.apiUrl}${normalized}`;
  }

  ngAfterViewInit() {
    this.initCanvas();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['imageUrl'] && changes['imageUrl'].currentValue) {
      this.loadImage();
    }
  }

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    this.ctx = ctx;

    canvas.addEventListener('pointerdown', this.startDrawing.bind(this));
    canvas.addEventListener('pointermove', this.draw.bind(this));
    window.addEventListener('pointerup', this.stopDrawing.bind(this));
    canvas.addEventListener('pointerleave', this.stopDrawing.bind(this));

    this.loadImage();
  }

  private loadImage() {
    const canvas = this.canvasRef.nativeElement;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = this.resolveUrl(this.imageUrl);
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      this.ctx.drawImage(img, 0, 0, img.width, img.height);
    };
    img.onerror = (err) => {
      console.error('Failed to load image', err);
    };
  }

  private startDrawing(event: PointerEvent) {
    this.drawing = true;
    this.ctx.strokeStyle = this.currentColor;
    this.ctx.lineWidth = 4;
    this.ctx.lineCap = 'round';
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.ctx.beginPath();
    this.ctx.moveTo(event.clientX - rect.left, event.clientY - rect.top);
  }

  private draw(event: PointerEvent) {
    if (!this.drawing) return;
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.ctx.lineTo(event.clientX - rect.left, event.clientY - rect.top);
    this.ctx.stroke();
  }

  private stopDrawing() {
    if (!this.drawing) return;
    this.drawing = false;
    this.ctx.closePath();
  }

  clearCanvas() {
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.loadImage();
  }
}
