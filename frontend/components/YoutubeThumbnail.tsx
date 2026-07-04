type Props = {
  videoId: string | null | undefined;
  alt?: string;
  className?: string;
  fit?: "cover" | "contain";
  loading?: "eager" | "lazy";
};

export default function YoutubeThumbnail({
  videoId,
  alt = "Episode thumbnail",
  className = "",
  fit = "contain",
  loading,
}: Props) {
  return (
    <div className={`relative overflow-hidden bg-stone-100 ${className}`}>
      {videoId ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
          alt={alt}
          loading={loading}
          decoding="async"
          className={`absolute inset-0 h-full w-full ${fit === "contain" ? "object-contain" : "object-cover"}`}
        />
      ) : (
        <div className="absolute inset-0 flex items-center justify-center">
          <svg className="h-8 w-8 text-stone-300" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
      )}
    </div>
  );
}
