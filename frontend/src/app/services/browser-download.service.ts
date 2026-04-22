import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class BrowserDownloadService {

  async download(url: string, filename: string, onProgress?: (progress: number) => void, signal?: AbortSignal): Promise<void> {
    const response = await this.tryFetch(url, signal);

    if (response === null) {
      throw new Error('Download blocked by CORS policy. Use a direct download link.');
    }

    if (this.canUseFilePicker() && response.body) {
      await this.saveWithPicker(response, filename, onProgress, signal);
      return;
    }

    const blob = await response.blob();
    this.triggerBlobDownload(blob, filename);
    onProgress?.(100);
  }

  private async tryFetch(url: string, signal?: AbortSignal): Promise<Response | null> {
    try {
      const response = await fetch(url, {
        method: 'GET',
        mode: 'cors',
        credentials: 'omit',
        cache: 'no-store',
        signal
      });

      if (!response.ok) {
        throw new Error(`Download failed with status ${response.status}`);
      }

      return response;
    } catch (error) {
      if (this.isAbortError(error)) {
        throw error;
      }

      return null;
    }
  }

  private async saveWithPicker(
    response: Response,
    filename: string,
    onProgress: ((progress: number) => void) | undefined,
    signal?: AbortSignal
  ): Promise<void> {
    const picker = (window as Window & { showSaveFilePicker?: (options: Record<string, unknown>) => Promise<FileSystemFileHandle> }).showSaveFilePicker;
    if (typeof picker !== 'function') {
      const blob = await response.blob();
      this.triggerBlobDownload(blob, filename);
      onProgress?.(100);
      return;
    }

    const handle = await picker({
      suggestedName: filename
    });

    const writable = await handle.createWritable();
    let completed = false;

    try {
      const totalBytes = Number(response.headers.get('content-length') ?? 0);
      if (!response.body) {
        const blob = await response.blob();
        await writable.write(blob);
        onProgress?.(100);
        completed = true;
        return;
      }

      const reader = response.body.getReader();
      let receivedBytes = 0;

      while (true) {
        if (signal?.aborted) {
          throw new DOMException('The operation was aborted.', 'AbortError');
        }

        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        await writable.write(value);
        receivedBytes += value.byteLength;

        if (totalBytes > 0) {
          onProgress?.(Math.min(99, (receivedBytes / totalBytes) * 100));
        }
      }

      onProgress?.(100);
      completed = true;
    } finally {
      if (completed) {
        await writable.close();
      } else {
        await writable.abort().catch(() => undefined);
      }
    }
  }

  private triggerBlobDownload(blob: Blob, filename: string): void {
    const objectUrl = URL.createObjectURL(blob);
    this.triggerUrlDownload(objectUrl, filename, true);
  }

  private triggerDirectDownload(url: string, filename: string): void {
    this.triggerUrlDownload(url, filename, false);
  }

  private triggerUrlDownload(url: string, filename: string, revokeObjectUrl: boolean): void {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.rel = 'noreferrer noopener';
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    link.remove();

    if (revokeObjectUrl) {
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  }

  private canUseFilePicker(): boolean {
    return typeof window !== 'undefined' && typeof (window as Window & { showSaveFilePicker?: unknown }).showSaveFilePicker === 'function';
  }

  private isAbortError(error: unknown): boolean {
    return error instanceof DOMException && error.name === 'AbortError';
  }
}
