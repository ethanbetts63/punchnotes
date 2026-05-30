type Props = {
  imageUrl: string | null | undefined;
  name: string;
  className?: string;
};

function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .map((word) => word[0].toUpperCase())
    .slice(0, 2)
    .join("");
}

export default function ComedianImage({ imageUrl, name, className = "" }: Props) {
  return (
    <div className={`relative overflow-hidden bg-stone-100 ${className}`}>
      {imageUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={imageUrl} alt={`${name} image`} className="absolute inset-0 h-full w-full object-contain" />
      ) : (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold tracking-wider text-stone-400">{initials(name)}</span>
        </div>
      )}
    </div>
  );
}
