import { ChangeDetectionStrategy, Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { DependencyStatus, VideoAnalysis, VideoFormat } from './models/models';
import { BrowserDownloadService } from './services/browser-download.service';
import { VideoApiService } from './services/video-api.service';

type DownloadState = 'idle' | 'starting' | 'running' | 'completed' | 'failed' | 'cancelled';

const DEFAULT_QUALITIES = ['1080p', '720p', '480p', '360p', '240p'];
const DEFAULT_FORMATS = ['mp4', 'webm', 'mkv'];

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AppComponent {

  private readonly fb = inject(NonNullableFormBuilder);
  private readonly api = inject(VideoApiService);
  private readonly browserDownload = inject(BrowserDownloadService);
  private readonly destroyRef = inject(DestroyRef);
  private downloadAbortController?: AbortController;

  readonly dependencies = signal<DependencyStatus | null>(null);
  readonly analysis = signal<VideoAnalysis | null>(null);
  readonly progress = signal(0);
  readonly downloadState = signal<DownloadState>('idle');
  readonly downloadMessage = signal('Paste a video link.');
  readonly thumbnailLoaded = signal(false);
  readonly thumbnailError = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly isAnalyzing = signal(false);
  readonly isDownloading = signal(false);
  readonly statusLabel = signal('Checking system...');
  readonly statusIsReady = signal(false);
  readonly statusIsLoading = signal(true);
  readonly qualityOptions = signal<string[]>([...DEFAULT_QUALITIES]);
  readonly currentFormatOptions = signal<string[]>([...DEFAULT_FORMATS]);
  readonly canStartDownload = signal(false);
  readonly downloadStateLabel = computed(() => {
    const value = this.downloadState();
    return value.charAt(0).toUpperCase() + value.slice(1);
  });

  readonly defaultQualities = DEFAULT_QUALITIES;
  readonly defaultFormats = DEFAULT_FORMATS;

  readonly videoForm = this.fb.group({
    url: ['', [Validators.required]],
    quality: ['720p'],
    format: ['mp4']
  });

  constructor() {
    this.videoForm.controls.quality.disable({ emitEvent: false });
    this.videoForm.controls.format.disable({ emitEvent: false });
    this.loadDependencies();

    this.videoForm.controls.url.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      if (this.isDownloading()) {
        return;
      }

      if (this.analysis()) {
        this.resetAnalysisState();
      }

      this.refreshSelectionState();
    });

    this.videoForm.controls.quality.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.refreshSelectionState();
    });

    this.videoForm.controls.format.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.refreshSelectionState();
    });

    this.refreshSelectionState();

    this.destroyRef.onDestroy(() => {
      this.downloadAbortController?.abort();
    });
  }

  analyzeVideo(): void {
    if (this.isAnalyzing() || this.isDownloading()) {
      return;
    }

    const url = this.videoForm.controls.url.value.trim();
    if (!url) {
      this.errorMessage.set('Enter a video URL.');
      return;
    }

    this.isAnalyzing.set(true);
    this.analysis.set(null);
    this.downloadState.set('idle');
    this.thumbnailLoaded.set(false);
    this.thumbnailError.set(false);
    this.progress.set(0);
    this.downloadMessage.set('Analyzing...');
    this.errorMessage.set(null);
    this.videoForm.controls.quality.setValue('720p', { emitEvent: false });
    this.videoForm.controls.format.setValue('mp4', { emitEvent: false });
    this.refreshSelectionState();

    this.api.analyze(url).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: response => {
        this.analysis.set(response);
        this.isAnalyzing.set(false);
        this.refreshSelectionState(true);
      },
      error: error => {
        this.isAnalyzing.set(false);
        const message = this.extractErrorMessage(error);
        this.downloadMessage.set('Analysis failed.');
        this.errorMessage.set(message);
      }
    });
  }

  downloadVideoInBrowser(): void {
    if (this.isAnalyzing() || this.isDownloading()) {
      return;
    }

    const format = this.resolveSelectedFormat();
    if (!format?.url) {
      this.errorMessage.set('Choose a direct browser-downloadable format.');
      return;
    }

    this.downloadAbortController?.abort();
    this.downloadAbortController = new AbortController();
    this.isDownloading.set(true);
    this.downloadState.set('starting');
    this.progress.set(0);
    this.downloadMessage.set('Downloading...');
    this.errorMessage.set(null);

    const fileName = this.buildFileName(this.analysis(), format);
    this.downloadState.set('running');
    this.browserDownload.download(
      format.url,
      fileName,
      progress => this.progress.set(progress),
      this.downloadAbortController.signal
    ).then(() => {
      this.downloadState.set('completed');
      this.progress.set(100);
      this.downloadMessage.set('Download started.');
    }).catch(error => {
      if (this.isAbortError(error)) {
        this.downloadState.set('cancelled');
        this.downloadMessage.set('Cancelled.');
        return;
      }

      this.downloadState.set('failed');
      const message = this.extractErrorMessage(error);
      this.downloadMessage.set('Download failed.');
      this.errorMessage.set(message);
    }).finally(() => {
      this.isDownloading.set(false);
      this.downloadAbortController = undefined;
    });
  }

  cancelDownload(): void {
    this.downloadAbortController?.abort();
  }

  durationLabel(seconds?: number | null): string {
    if (!seconds || seconds <= 0) {
      return 'Duration unavailable';
    }

    const totalSeconds = Math.floor(seconds);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const remainingSeconds = totalSeconds % 60;

    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
    }

    return `${minutes}:${String(remainingSeconds).padStart(2, '0')}`;
  }

  viewsLabel(count?: number | null): string {
    if (!count || count <= 0) {
      return 'Views unavailable';
    }

    return `${new Intl.NumberFormat('en-US').format(count)} views`;
  }

  onThumbnailError(): void {
    this.thumbnailError.set(true);
    this.thumbnailLoaded.set(false);
  }

  private loadDependencies(): void {
    this.api.getDependencies().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: response => {
        this.dependencies.set(response);
        this.statusLabel.set(response.message);
        this.statusIsReady.set(!!response.ready);
        this.statusIsLoading.set(false);
      },
      error: () => {
        const fallback = {
          ytDlpAvailable: false,
          ffmpegAvailable: false,
          ready: false,
          message: 'Backend unavailable.'
        };

        this.dependencies.set(fallback);
        this.statusLabel.set(fallback.message);
        this.statusIsReady.set(false);
        this.statusIsLoading.set(false);
      }
    });
  }

  private syncSelectableControls(): void {
    if (!this.analysis()) {
      this.videoForm.controls.quality.disable({ emitEvent: false });
      this.videoForm.controls.format.disable({ emitEvent: false });
      return;
    }

    if (this.qualityOptions().length) {
      this.videoForm.controls.quality.enable({ emitEvent: false });
    } else {
      this.videoForm.controls.quality.disable({ emitEvent: false });
    }

    if (this.currentFormatOptions().length) {
      this.videoForm.controls.format.enable({ emitEvent: false });
    } else {
      this.videoForm.controls.format.disable({ emitEvent: false });
    }
  }

  private refreshSelectionState(preferDirectQuality = false): void {
    const analysis = this.analysis();
    const url = this.videoForm.controls.url.value.trim();
    const qualities = this.resolveQualityOptions(analysis);

    this.qualityOptions.set(qualities);

    if (!analysis) {
      this.currentFormatOptions.set([...this.defaultFormats]);
      this.canStartDownload.set(false);
      this.syncSelectableControls();
      if (!this.isAnalyzing()) {
        this.downloadMessage.set(url ? 'Analyze the link.' : 'Paste a video link.');
      }
      return;
    }

    const currentQuality = this.videoForm.controls.quality.value;
    if (preferDirectQuality && qualities.length) {
      const nextQuality = qualities.includes(currentQuality) ? currentQuality : qualities[0];
      if (nextQuality && nextQuality !== currentQuality) {
        this.videoForm.controls.quality.setValue(nextQuality, { emitEvent: false });
      }
    }

    const selectedQuality = this.videoForm.controls.quality.value;
    const formatOptions = this.resolveFormatOptions(analysis, selectedQuality);
    this.currentFormatOptions.set(formatOptions);

    if (!qualities.length) {
      this.videoForm.controls.format.setValue(this.defaultFormats[0], { emitEvent: false });
      this.canStartDownload.set(false);
      this.syncSelectableControls();
      this.downloadMessage.set('No direct resolutions available.');
      return;
    }

    if (formatOptions.length) {
      const currentFormat = this.videoForm.controls.format.value;
      if (!formatOptions.includes(currentFormat)) {
        this.videoForm.controls.format.setValue(formatOptions[0], { emitEvent: false });
      }
    } else {
      this.videoForm.controls.format.setValue(this.defaultFormats[0], { emitEvent: false });
    }

    const selectedFormat = this.resolveSelectedFormat(analysis);
    const ready = url.length > 0 && !this.isAnalyzing() && !this.isDownloading() && !!selectedFormat?.url;
    this.canStartDownload.set(ready);
    this.syncSelectableControls();
    this.downloadMessage.set(selectedFormat?.url ? 'Ready to download.' : 'No direct format available.');
  }

  private resetAnalysisState(): void {
    this.analysis.set(null);
    this.downloadState.set('idle');
    this.thumbnailLoaded.set(false);
    this.thumbnailError.set(false);
    this.progress.set(0);
    this.videoForm.controls.quality.setValue('720p', { emitEvent: false });
    this.videoForm.controls.format.setValue('mp4', { emitEvent: false });
  }

  private resolveSelectedFormat(analysis: VideoAnalysis | null = this.analysis()): VideoFormat | null {
    if (!analysis?.formats.length) {
      return null;
    }

    const quality = this.videoForm.controls.quality.value;
    const ext = this.normalizeExt(this.videoForm.controls.format.value);
    const matchingQuality = this.directFormats(analysis).filter(format => this.formatQuality(format) === quality);

    if (!matchingQuality.length) {
      return null;
    }

    const exactMatch = matchingQuality.find(format => this.normalizeExt(format.ext) === ext);
    return exactMatch ?? matchingQuality[0] ?? null;
  }

  private resolveQualityOptions(analysis: VideoAnalysis | null): string[] {
    if (!analysis) {
      return [...this.defaultQualities];
    }

    const qualities = analysis.availableQualities?.length ? [...analysis.availableQualities] : [...this.defaultQualities];
    return qualities.filter(quality => this.hasDirectFormatForQuality(analysis, quality));
  }

  private resolveFormatOptions(analysis: VideoAnalysis, quality: string): string[] {
    const formats = this.directFormats(analysis).filter(format => this.formatQuality(format) === quality);
    return Array.from(new Set(formats.map(format => this.normalizeExt(format.ext)).filter(Boolean)));
  }

  private directFormats(analysis: VideoAnalysis): VideoFormat[] {
    return analysis.formats.filter(format => this.isDirectBrowserFormat(format));
  }

  private hasDirectFormatForQuality(analysis: VideoAnalysis, quality: string): boolean {
    return this.directFormats(analysis).some(format => this.formatQuality(format) === quality);
  }

  private isDirectBrowserFormat(format: VideoFormat): boolean {
    const url = this.normalizeExt(format.url);
    if (!url) {
      return false;
    }

    return !url.includes('/api/manifest/')
      && !url.includes('hls_playlist')
      && !url.includes('.m3u8')
      && !url.includes('manifest.m3u8')
      && !url.includes('dash_playlist');
  }

  private formatQuality(format: VideoFormat): string {
    return format.height ? `${format.height}p` : 'unknown';
  }

  private normalizeExt(value?: string | null): string {
    return value ? value.trim().toLowerCase() : '';
  }

  private buildFileName(analysis: VideoAnalysis | null, format: VideoFormat): string {
    const title = this.sanitizeFileName(analysis?.title || 'download');
    const quality = this.normalizeExt(this.formatQuality(format)).replace(/[^a-z0-9]+/g, '-');
    const ext = this.normalizeExt(format.ext) || 'mp4';
    return `${title}-${quality}.${ext}`;
  }

  private sanitizeFileName(value: string): string {
    return value
      .replace(/[<>:"/\\|?*\u0000-\u001F]/g, '')
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/\s/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 120) || 'download';
  }

  private isAbortError(error: unknown): boolean {
    return error instanceof DOMException && error.name === 'AbortError';
  }

  private extractErrorMessage(error: unknown): string {
    if (error instanceof Error) {
      return error.message;
    }

    if (typeof error === 'string') {
      return error;
    }

    if (error && typeof error === 'object') {
      const candidate = error as { error?: unknown; message?: string; statusText?: string };
      if (candidate.error && typeof candidate.error === 'object') {
        const nested = candidate.error as { message?: string };
        if (typeof nested.message === 'string' && nested.message.trim()) {
          return nested.message;
        }
      }
      if (typeof candidate.error === 'string' && candidate.error.trim()) {
        return candidate.error;
      }
      if (typeof candidate.message === 'string' && candidate.message.trim()) {
        return candidate.message;
      }
      if (typeof candidate.statusText === 'string' && candidate.statusText.trim()) {
        return candidate.statusText;
      }
    }

    return 'Unexpected error';
  }
}
