import YoutubeThumbnail from "@/components/YoutubeThumbnail";

type Props = {
  imageUrl: string | null | undefined;
  fallbackVideoId: string | null | undefined;
  alt: string;
  className?: string;
  fit?: "cover" | "contain";
};

export default function SetImage({ imageUrl, fallbackVideoId, alt, className = "", fit = "contain" }: Props) {
  if (!imageUrl) {
    return <YoutubeThumbnail videoId={fallbackVideoId} alt={alt} className={className} fit={fit} />;
  }

  return (
    <div className={`relative overflow-hidden bg-stone-100 ${className}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={imageUrl}
        alt={alt}
        className={`absolute inset-0 h-full w-full ${fit === "contain" ? "object-contain" : "object-cover"}`}
      />
    </div>
  );
}
