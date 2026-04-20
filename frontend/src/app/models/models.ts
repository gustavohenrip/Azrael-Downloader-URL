export interface DependencyStatus {
  ytDlpAvailable: boolean;
  ffmpegAvailable: boolean;
  ready: boolean;
  message: string;
}

export interface VideoFormat {
  formatId: string;
  height?: number | null;
  ext?: string | null;
  url?: string | null;
  filesize?: number | null;
  formatNote?: string | null;
  vcodec?: string | null;
  acodec?: string | null;
  resolution?: string | null;
  fps?: number | null;
}

export interface VideoAnalysis {
  title?: string | null;
  durationSeconds?: number | null;
  viewCount?: number | null;
  uploader?: string | null;
  thumbnailUrl?: string | null;
  formats: VideoFormat[];
  availableQualities: string[];
}
