import { useState, useRef, useEffect } from "react";

interface VideoPlayerProps {
  streamUrl?: string;
  thumbnailUrl?: string;
  isLive?: boolean;
}

export function VideoPlayer({ streamUrl, thumbnailUrl, isLive }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (isLive && videoRef.current && streamUrl) {
      // For a real app, you would initialize HLS.js or WebRTC here.
      // For this demo, we'll just try to play standard video if possible.
      videoRef.current.src = streamUrl;
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    }
  }, [isLive, streamUrl]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(() => {});
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="relative group w-full h-full bg-black rounded-md overflow-hidden flex items-center justify-center">
      {streamUrl ? (
        <video 
          ref={videoRef}
          className="w-full h-full object-cover"
          poster={thumbnailUrl}
          loop={!isLive}
          muted
          playsInline
        />
      ) : (
        <>
          {thumbnailUrl ? (
             <img src={thumbnailUrl} alt="Video Thumbnail" className="w-full h-full object-cover opacity-80" />
          ) : (
             <span className="text-neutral-600 font-mono text-sm">NO SIGNAL</span>
          )}
        </>
      )}

      {/* Play/Pause Overlay */}
      {streamUrl && (
        <div 
          className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
          onClick={togglePlay}
        >
          <div className="bg-white/20 p-4 rounded-full backdrop-blur-sm hover:scale-110 transition-transform">
            {isPlaying ? (
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
            ) : (
              <svg className="w-8 h-8 text-white translate-x-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            )}
          </div>
        </div>
      )}

      {/* Live Badge */}
      {isLive && (
        <div className="absolute top-2 right-2 bg-red-600/90 text-white text-[10px] font-bold px-2 py-1 rounded tracking-widest backdrop-blur-sm flex items-center">
          <span className="w-1.5 h-1.5 bg-white rounded-full mr-1 animate-pulse" />
          LIVE
        </div>
      )}
    </div>
  );
}
