import { Component, Input, ViewChild, ElementRef, AfterViewInit, OnChanges, SimpleChanges, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-coloring-canvas',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-2 flex flex-col items-center">
      <canvas
        #canvas
        class="border rounded touch-none max-h-[60vh]"
        style="max-width: 100%;"
      ></canvas>
      <div class="flex items-center gap-2 flex-wrap justify-center">
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
export class ColoringCanvasComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() imageUrl: string = '';
  @ViewChild('canvas', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  // Palette tailored for common safari animals
  colors = [
    '#ffe8a3', // light yellow for giraffe body
    '#b5651d', // brown for giraffe spots
    '#c68642', // tan for lion fur
    '#8b4513', // dark brown for lion mane
    '#808080', // grey for elephant skin
    '#f4f4f4', // light grey/white for tusks
    '#000000'  // black for details and outlines
  ];
  currentColor = this.colors[0];

  private ctx!: CanvasRenderingContext2D;
  private drawing = false;
  private baseImg: HTMLImageElement | null = null;
  private baseImgCanvas?: HTMLCanvasElement;
  private baseImgCtx?: CanvasRenderingContext2D;
  private resizeHandler = () => this.loadImage();

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
    window.addEventListener('resize', this.resizeHandler);
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['imageUrl'] && changes['imageUrl'].currentValue) {
      this.loadImage();
    }
  }

  ngOnDestroy() {
    window.removeEventListener('resize', this.resizeHandler);
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
      const containerWidth = canvas.parentElement?.clientWidth || img.width;
      const containerHeight = window.innerHeight * 0.8; // fit within viewport

      const widthScale = containerWidth / img.width;
      const heightScale = containerHeight / img.height;
      const scale = Math.min(1, widthScale, heightScale);

      canvas.width = img.width * scale;
      canvas.height = img.height * scale;
      canvas.style.width = `${canvas.width}px`;
      canvas.style.height = `${canvas.height}px`;

      this.ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      this.baseImg = img;

      this.baseImgCanvas = document.createElement('canvas');
      this.baseImgCanvas.width = canvas.width;
      this.baseImgCanvas.height = canvas.height;
      this.baseImgCtx = this.baseImgCanvas.getContext('2d') ?? undefined;
      this.baseImgCtx?.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.onerror = (err) => {
      console.error('Failed to load image', err);
    };
  }

  private startDrawing(event: PointerEvent) {
    this.ctx.strokeStyle = this.currentColor;
    this.ctx.lineWidth = 4;
    this.ctx.lineCap = 'round';
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    const scaleX = this.canvasRef.nativeElement.width / rect.width;
    const scaleY = this.canvasRef.nativeElement.height / rect.height;
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;
    if (!this.isWhitePixel(x, y)) {
      this.drawing = false;
      return;
    }
    this.drawing = true;
    this.ctx.beginPath();
    this.ctx.moveTo(x, y);
  }

  private draw(event: PointerEvent) {
    if (!this.drawing) return;
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    const scaleX = this.canvasRef.nativeElement.width / rect.width;
    const scaleY = this.canvasRef.nativeElement.height / rect.height;
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;
    if (!this.isWhitePixel(x, y)) {
      this.ctx.moveTo(x, y);
      return;
    }
    this.ctx.lineTo(x, y);
    this.ctx.stroke();
    if (this.baseImg) {
      const canvas = this.canvasRef.nativeElement;
      this.ctx.save();
      this.ctx.globalCompositeOperation = 'destination-over';
      this.ctx.drawImage(this.baseImg, 0, 0, canvas.width, canvas.height);
      this.ctx.restore();
    }
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

  private isWhitePixel(x: number, y: number): boolean {
    if (!this.baseImgCtx) {
      return true;
    }
    const data = this.baseImgCtx.getImageData(x, y, 1, 1).data;
    return data[0] > 240 && data[1] > 240 && data[2] > 240 && data[3] > 0;
  }
}
